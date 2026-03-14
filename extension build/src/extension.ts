import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import type { ArduinoContext } from 'vscode-arduino-api';

const OUTPUT_CHANNEL_NAME = 'Forgetfulino';

function getArduinoContext(): ArduinoContext | undefined {
  return vscode.extensions.getExtension('dankeboy36.vscode-arduino-api')?.exports as ArduinoContext | undefined;
}

function getOutputChannel(): vscode.OutputChannel {
  return vscode.window.createOutputChannel(OUTPUT_CHANNEL_NAME);
}

function isSketchSource(doc: vscode.TextDocument): boolean {
  const ext = path.extname(doc.uri.fsPath).toLowerCase();
  return ext === '.ino' || ext === '.cpp' || ext === '.c';
}

function isForgetfulinoPresent(text: string): boolean {
  return text.includes('Forgetfulino') || text.includes('<Forgetfulino.h>');
}

/** Default Arduino IDE new sketch skeleton (no spaces). If content matches this or is empty → "new file". */
const DEFAULT_ARDUINO_SKELETON =
  'voidsetup(){//putyoursetupcodehere,torunonce:}voidloop(){//putyourmaincodehere,torunrepeatedly:}';

function shouldAutoInjectTemplate(doc: vscode.TextDocument): boolean {
  if (path.extname(doc.uri.fsPath).toLowerCase() !== '.ino') return false;
  const text = doc.getText();
  if (isForgetfulinoPresent(text)) return false;
  const trimmed = text.trim();
  if (!trimmed.length) return true; // file vuoto = nuovo
  // Solo file "nuovi": esattamente il template default di Arduino (setup/loop con commenti standard)
  const normalized = trimmed.replace(/\s+/g, '');
  return normalized === DEFAULT_ARDUINO_SKELETON;
}

function buildInjectTemplate(): string {
  return `#include <Forgetfulino.h>

void setup() {
  Serial.begin(115200);
  delay(1000);

  Forgetfulino.begin();

  // TODO: il tuo codice qui...
  // Quando vuoi recuperare lo sketch, chiama:
  Forgetfulino.dumpCompressed();
}

void loop() {
}
`;
}

/** Block to add in setup when Serial already exists (after Serial.begin). */
const INJECT_BLOCK_AFTER_SERIAL = `  delay(2000);
  Forgetfulino.begin();
  Forgetfulino.dumpCompressed();
  // Forgetfulino.dumpSource();
`;

/** Block to add in setup when Serial does not exist (includes Serial.begin). */
const INJECT_BLOCK_WITH_SERIAL = `  Serial.begin(115200);
  delay(2000);
  Forgetfulino.begin();
  Forgetfulino.dumpCompressed();
  // Forgetfulino.dumpSource();
`;

/**
 * Apply inject to an existing file: add include at top and block in setup.
 * Returns new content or null if Forgetfulino already present (do nothing).
 */
function applyInjectToExistingFile(text: string): string | null {
  if (isForgetfulinoPresent(text)) return null;

  let out = text;

  // 1. Add include at top if missing
  if (!out.includes('#include <Forgetfulino.h>')) {
    out = '#include <Forgetfulino.h>\n\n' + out.trimStart();
  }

  // 2. Find void setup() and insert block
  const setupRegex = /void\s+setup\s*\(\s*\)\s*\{/;
  const setupMatch = out.match(setupRegex);
  if (!setupMatch || setupMatch.index === undefined) return out;

  const setupStart = setupMatch.index + setupMatch[0].length;
  let depth = 1;
  let pos = setupStart;
  while (pos < out.length && depth > 0) {
    const ch = out[pos];
    if (ch === '{') depth++;
    else if (ch === '}') depth--;
    pos++;
  }
  const setupEnd = pos;
  const setupBody = out.slice(setupStart, setupEnd);
  const hasSerialInSetup = /Serial\.begin\s*\(/.test(setupBody);

  const block = hasSerialInSetup ? INJECT_BLOCK_AFTER_SERIAL : INJECT_BLOCK_WITH_SERIAL;

  let insertPos: number;
  if (hasSerialInSetup) {
    const serialIdx = out.indexOf('Serial.begin', setupStart);
    if (serialIdx === -1) {
      insertPos = setupStart;
    } else {
      const lineEnd = out.indexOf('\n', serialIdx);
      insertPos = lineEnd !== -1 ? lineEnd + 1 : setupStart;
    }
  } else {
    insertPos = setupStart;
  }

  out = out.slice(0, insertPos) + block + out.slice(insertPos);
  return out;
}

function tryAutoDetectLibraryRoot(arduino: ArduinoContext | undefined): string | undefined {
  // ArduinoContext.userDirPath is the sketchbook path (directories.user)
  // Standard library install: <sketchbook>/libraries/Forgetfulino
  // For development / custom setups we also support <sketchbook>/libraries/Forgetfulino-main
  const userDir = (arduino as any)?.userDirPath as string | undefined;
  if (!userDir) return undefined;
  const librariesDir = path.join(userDir, 'libraries');
  const candidates = ['Forgetfulino', 'Forgetfulino-main'];
  for (const name of candidates) {
    const candidate = path.join(librariesDir, name);
    if (fs.existsSync(candidate) && fs.statSync(candidate).isDirectory()) {
      return candidate;
    }
  }
  return undefined;
}

function resolveLibraryRoot(arduino: ArduinoContext | undefined): string | undefined {
  const cfg = vscode.workspace.getConfiguration('forgetfulino');
  const configured = (cfg.get<string>('libraryRoot') ?? '').trim();
  if (configured) return configured;
  return tryAutoDetectLibraryRoot(arduino);
}

function resolveSketchFolder(arduino: ArduinoContext | undefined): string | undefined {
  const sketchPath = (arduino as any)?.sketchPath as string | undefined;
  if (sketchPath && fs.existsSync(sketchPath) && fs.statSync(sketchPath).isDirectory()) return sketchPath;

  const editor = vscode.window.activeTextEditor;
  if (!editor) return undefined;
  const filePath = editor.document.uri.fsPath;
  if (!filePath) return undefined;
  return path.dirname(filePath);
}

// ---- Generator logic ported from forgetfulino_generator.py (no Python required) ----

/** Strip comments by removing entire lines; no blank lines left, no scattered spaces. */
function stripComments(source: string): string {
  let out = '';
  let i = 0;
  const n = source.length;
  while (i < n) {
    const rest = source.slice(i);
    if (rest.startsWith('//')) {
      i += 2;
      while (i < n && source[i] !== '\n') i++;
      if (i < n) i++;
      continue;
    }
    if (rest.startsWith('/*')) {
      i += 2;
      const end = source.indexOf('*/', i);
      const blockEnd = end === -1 ? n : end + 2;
      while (i < blockEnd) i++;
      i = blockEnd;
      continue;
    }
    if (source[i] === '"' || source[i] === "'") {
      const q = source[i];
      out += source[i];
      i++;
      while (i < n) {
        if (source[i] === '\\') {
          out += source[i];
          i++;
          if (i < n) {
            out += source[i];
            i++;
          }
          continue;
        }
        if (source[i] === q) {
          out += source[i];
          i++;
          break;
        }
        out += source[i];
        i++;
      }
      continue;
    }
    out += source[i];
    i++;
  }
  return out.replace(/\n\n+/g, '\n');
}

/**
 * Sanitize source before generating headers: replace Unicode characters that can cause
 * problems in C literals, PROGMEM, or Base85 with safe ASCII equivalents.
 */
function sanitizeSourceForDump(s: string): string {
  return s
    // Null bytes → space (altrimenti l'output decodificato si tronca al primo \0)
    .replace(/\0/g, ' ')
    // Curly/smart quotes → straight
    .replace(/\u201C/g, '"')  // "
    .replace(/\u201D/g, '"')  // "
    .replace(/\u2018/g, "'")  // '
    .replace(/\u2019/g, "'")  // '
    .replace(/\u201A/g, "'")  // ‚
    .replace(/\u201E/g, '"')  // „
    .replace(/\u201B/g, "'")  // ‛
    .replace(/\u201F/g, '"')  // ‟
    .replace(/\u2039/g, "'")  // ‹
    .replace(/\u203A/g, "'")  // ›
    // Dashes/hyphens → ASCII hyphen-minus
    .replace(/\u2010/g, '-')  // ‐ hyphen
    .replace(/\u2011/g, '-')  // ‑ non-breaking hyphen
    .replace(/\u2012/g, '-')  // ‒ figure dash
    .replace(/\u2013/g, '-')  // – en dash
    .replace(/\u2014/g, '-')  // — em dash
    .replace(/\u2015/g, '-')  // ― horizontal bar
    .replace(/\u2212/g, '-')  // − minus sign
    .replace(/\uFE58/g, '-')  // ﹘ small em dash
    .replace(/\uFE63/g, '-')  // ﹣ small hyphen-minus
    .replace(/\uFF0D/g, '-')  // － fullwidth hyphen-minus
    // Spaces that can cause issues → normal space
    .replace(/\u00A0/g, ' ')   // no-break space
    .replace(/\u2000/g, ' ')   // en quad
    .replace(/\u2001/g, ' ')   // em quad
    .replace(/\u2002/g, ' ')   // en space
    .replace(/\u2003/g, ' ')   // em space
    .replace(/\u2004/g, ' ')   // three-per-em
    .replace(/\u2005/g, ' ')   // four-per-em
    .replace(/\u2006/g, ' ')   // six-per-em
    .replace(/\u2007/g, ' ')   // figure space
    .replace(/\u2008/g, ' ')   // punctuation space
    .replace(/\u2009/g, ' ')   // thin space
    .replace(/\u200A/g, ' ')   // hair space
    .replace(/\u202F/g, ' ')   // narrow no-break space
    .replace(/\u205F/g, ' ')   // medium mathematical space
    .replace(/\u3000/g, ' ')   // ideographic space
    // Ellipsis → three dots
    .replace(/\u2026/g, '...') // …
    // Remove zero-width / invisible (can break encoding)
    .replace(/\u200B/g, '')    // zero-width space
    .replace(/\u200C/g, '')    // zero-width non-joiner
    .replace(/\u200D/g, '')    // zero-width joiner
    .replace(/\u2060/g, '')    // word joiner
    .replace(/\uFEFF/g, '');   // BOM / zero-width no-break
}

function findSketchFile(folder: string): string | undefined {
  const entries = fs.readdirSync(folder);
  const inoFiles = entries.filter((name) => name.toLowerCase().endsWith('.ino'));
  if (!inoFiles.length) return undefined;
  const folderName = path.basename(folder);
  const main = inoFiles.find((name) => path.parse(name).name === folderName);
  return main ? path.join(folder, main) : path.join(folder, inoFiles[0]!);
}

function collectSketchSources(sketchFolder: string): { fullSource: string; mainName: string } {
  const mainIno = findSketchFile(sketchFolder);
  if (!mainIno) return { fullSource: '', mainName: '' };

  const folderName = path.basename(sketchFolder);
  const mainName = path.basename(mainIno);

  const allEntries = fs.readdirSync(sketchFolder);
  const inoList = allEntries
    .filter((name) => name.toLowerCase().endsWith('.ino'))
    .map((name) => path.join(sketchFolder, name))
    .sort((a, b) => {
      const aBase = path.basename(a);
      const bBase = path.basename(b);
      const aKey = aBase === mainName ? `0-${aBase}` : `1-${aBase}`;
      const bKey = bBase === mainName ? `0-${bBase}` : `1-${bBase}`;
      return aKey.localeCompare(bKey);
    });

  const cppList = allEntries
    .filter((name) => {
      const lower = name.toLowerCase();
      return lower.endsWith('.cpp') || lower.endsWith('.c');
    })
    .map((name) => path.join(sketchFolder, name))
    .sort((a, b) => path.basename(a).localeCompare(path.basename(b)));

  const ordered = [...inoList, ...cppList];

  const parts: string[] = [];
  for (const p of ordered) {
    try {
      let content = fs.readFileSync(p, 'utf8');
      content = sanitizeSourceForDump(content);
      const name = path.basename(p);
      parts.push(`// === File: ${name} ===\n`);
      parts.push(content);
      if (!content.endsWith('\n')) parts.push('\n');
      parts.push('\n');
    } catch {
      // ignore unreadable files
    }
  }

  const header =
    `// Sketch: ${folderName}\n` +
    `// Date: ${new Date().toISOString().replace('T', ' ').split('.')[0]}\n` +
    `// Files: ${ordered.length}\n\n`;

  return { fullSource: header + parts.join(''), mainName };
}

function textToCArray(text: string, varName: string): string {
  const lines: string[] = [];
  let segment: string[] = [];

  for (let i = 0; i < text.length; i++) {
    const ch = text[i]!;
    let token: string;
    if (ch === '\n') token = "'\\n'";
    else if (ch === '\r') token = "'\\r'";
    else if (ch === '\t') token = "'\\t'";
    else if (ch === '\\') token = "'\\\\'";
    else if (ch === '"') token = "'\\\"'";
    else if (ch === "'") token = "'\\''";
    else token = `'${ch}'`;

    segment.push(token);
    if ((i + 1) % 16 === 0 || i === text.length - 1) {
      lines.push('    ' + segment.join(', '));
      segment = [];
    }
  }

  const arrayContent = lines.join(',\n');
  return `const char ${varName}[] PROGMEM = {\n${arrayContent}\n};`;
}

/** Chunk size in chars: C99 requires string literals ≤4095 chars; keep under that to avoid truncation. */
const COMPRESSED_CHUNK_SIZE = 4095;

function escapeForCStringLiteral(value: string): string {
  const out: string[] = [];
  for (const ch of value) {
    if (ch === '\\') out.push('\\\\');
    else if (ch === '"') out.push('\\"');
    else if (ch === '\n') out.push('\\n');
    else if (ch === '\r') out.push('\\r');
    else if (ch === '\t') out.push('\\t');
    else out.push(ch);
  }
  return out.join('');
}

function toCStringLiteral(value: string, varName: string): string {
  const escaped = escapeForCStringLiteral(value);
  return `const char ${varName}[] PROGMEM = "${escaped}";`;
}

/** Generate multiple PROGMEM arrays + pointer table so total size has no compiler limit. */
function generateCompressedChunks(encoded: string): string {
  const lines: string[] = [];
  const chunkNames: string[] = [];
  for (let i = 0; i < encoded.length; i += COMPRESSED_CHUNK_SIZE) {
    const chunk = encoded.slice(i, i + COMPRESSED_CHUNK_SIZE);
    const name = `forgetfulino_compressed_data_${chunkNames.length}`;
    chunkNames.push(name);
    lines.push(`const char ${name}[] PROGMEM = "${escapeForCStringLiteral(chunk)}";`);
  }
  lines.push('');
  lines.push(`#define FORGETFULINO_COMPRESSED_CHUNK_SIZE ${COMPRESSED_CHUNK_SIZE}`);
  lines.push(`const unsigned int forgetfulino_compressed_chunk_count = ${chunkNames.length};`);
  lines.push(`const unsigned long forgetfulino_compressed_total_len = ${encoded.length}UL;`);
  lines.push(`const char* const forgetfulino_compressed_chunks[] PROGMEM = { ${chunkNames.join(', ')} };`);
  return lines.join('\n');
}

function ascii85Encode(buf: Uint8Array): string {
  let result = '';
  const n = buf.length;
  let i = 0;
  while (i < n) {
    const remaining = n - i;
    const chunk = buf.subarray(i, Math.min(i + 4, n));
    let value = 0;
    for (let j = 0; j < 4; j++) {
      value = (value << 8) | (j < chunk.length ? chunk[j]! : 0);
    }
    const tmp: number[] = new Array(5);
    for (let j = 4; j >= 0; j--) {
      tmp[j] = (value % 85) + 33;
      value = Math.floor(value / 85);
    }
    let outChars = String.fromCharCode(...tmp);
    if (remaining < 4) {
      // drop the extra chars for padded bytes
      outChars = outChars.substring(0, remaining + 1);
    }
    result += outChars;
    i += 4;
  }
  return result;
}

function ascii85Decode(text: string): Uint8Array {
  const cleaned = text.replace(/\s+/g, '');
  const bytes: number[] = [];
  let i = 0;
  while (i < cleaned.length) {
    const remaining = cleaned.length - i;
    const groupLen = remaining >= 5 ? 5 : remaining;
    if (groupLen <= 0) break;
    const group = cleaned.substring(i, i + groupLen);
    i += groupLen;

    const digits: number[] = new Array(5);
    for (let j = 0; j < 5; j++) {
      if (j < groupLen) {
        digits[j] = group.charCodeAt(j) - 33;
      } else {
        digits[j] = 84; // pad with 'u' (84) as per Ascii85
      }
    }

    let value = 0;
    for (let j = 0; j < 5; j++) {
      value = value * 85 + digits[j];
    }

    const tmp = [
      (value >>> 24) & 0xff,
      (value >>> 16) & 0xff,
      (value >>> 8) & 0xff,
      value & 0xff
    ];

    if (groupLen < 5) {
      const nBytes = groupLen - 1; // inverse of encode's truncation
      for (let k = 0; k < nBytes; k++) bytes.push(tmp[k]!);
    } else {
      bytes.push(...tmp);
    }
  }
  return new Uint8Array(bytes);
}

function generateSourceHeader(fullSource: string, mainName: string): string {
  return `// Forgetfulino generated source data
// AUTO-GENERATED - DO NOT EDIT

#ifndef FORGETFULINO_SOURCE_DATA_H
#define FORGETFULINO_SOURCE_DATA_H

#include <Arduino.h>

// Platform-specific PROGMEM
#if defined(ARDUINO_ARCH_AVR)
    #include <avr/pgmspace.h>
#elif defined(ESP8266) || defined(ESP32)
    #undef PROGMEM
    #define PROGMEM
#endif

// Sketch source code
${textToCArray(fullSource, 'forgetfulino_source_data')}

// Metadata
const unsigned int forgetfulino_source_size = ${fullSource.length};
const char forgetfulino_sketch_name[] PROGMEM = "${mainName}";

#endif
`;
}

function generateCompressedHeader(fullSource: string): string {
  const bytes = new TextEncoder().encode(fullSource);
  const encoded = ascii85Encode(bytes);
  const chunksBlock = generateCompressedChunks(encoded);

  return `// Forgetfulino generated compressed data
// AUTO-GENERATED - DO NOT EDIT

#ifndef FORGETFULINO_COMPRESSED_H
#define FORGETFULINO_COMPRESSED_H

#include <Arduino.h>

// Platform-specific PROGMEM
#if defined(ARDUINO_ARCH_AVR)
    #include <avr/pgmspace.h>
#elif defined(ESP8266) || defined(ESP32)
    #undef PROGMEM
    #define PROGMEM
#endif

#define FORGETFULINO_USE_CHUNKS 1
// Base85-compressed sketch source (multiple chunks to avoid "variable too large")
${chunksBlock}

// Original uncompressed source size in bytes
const unsigned int forgetfulino_original_size = ${fullSource.length};

#endif
`;
}

async function generateHeadersCommand(out: vscode.OutputChannel): Promise<void> {
  const arduino = getArduinoContext();
  const sketchFolder = resolveSketchFolder(arduino);
  const libraryRoot = resolveLibraryRoot(arduino);

  if (!sketchFolder) {
    vscode.window.showErrorMessage('Forgetfulino: cannot determine sketch folder. Open a sketch and try again.');
    return;
  }
  if (!libraryRoot) {
    vscode.window.showErrorMessage(
      'Forgetfulino: cannot find the Forgetfulino library. Set setting "Forgetfulino › Library Root" and retry.'
    );
    return;
  }

  const libSrcPath = path.join(libraryRoot, 'src');
  if (!fs.existsSync(libSrcPath) || !fs.statSync(libSrcPath).isDirectory()) {
    vscode.window.showErrorMessage(`Forgetfulino: library src folder not found at ${libSrcPath}`);
    return;
  }

  out.show(true);
  out.appendLine(`[Forgetfulino] Sketch folder: ${sketchFolder}`);
  out.appendLine(`[Forgetfulino] Library root: ${libraryRoot}`);

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'Forgetfulino: generating headers…', cancellable: false },
    async () => {
      const { fullSource, mainName } = collectSketchSources(sketchFolder);
      if (!fullSource) {
        throw new Error('No .ino file found in sketch folder.');
      }

      const cfg = vscode.workspace.getConfiguration('forgetfulino');
      const includeComments = cfg.get<boolean>('includeCommentsInDump', true);
      const effectiveSource = includeComments ? fullSource : stripComments(fullSource);

      out.appendLine(`[Forgetfulino] Sketch: ${mainName}`);
      out.appendLine(`[Forgetfulino] Size: ${effectiveSource.length} bytes (comments ${includeComments ? 'included' : 'stripped'})`);

      const sourceHeader = generateSourceHeader(effectiveSource, mainName);
      const compressedHeader = generateCompressedHeader(effectiveSource);

      const sourceHeaderPath = path.join(libSrcPath, 'forgetfulino_source_data.h');
      const compressedHeaderPath = path.join(libSrcPath, 'forgetfulino_compressed.h');

      fs.writeFileSync(sourceHeaderPath, sourceHeader, 'utf8');
      fs.writeFileSync(compressedHeaderPath, compressedHeader, 'utf8');

      out.appendLine(`[Forgetfulino] Generated: ${sourceHeaderPath}`);
      out.appendLine(`[Forgetfulino] Generated: ${compressedHeaderPath}`);
    }
  );

  vscode.window.showInformationMessage('Forgetfulino: headers generated.');
}

function stripSerialTimestamp(raw: string): string {
  // Single line from Serial Monitor: strip "HH:MM:SS.mmm -> " at the start, then trim and collapse whitespace (like old working VSIX)
  const one = raw.replace(/^\d+:\d+:\d+\.\d+\s*->\s*/, '').trim();
  return one.replace(/\s+/g, '');
}

/** Sketchbook libraries path (e.g. .../Arduino/libraries). Used to resolve library versions for #include comments. */
function getLibrariesPath(): string | undefined {
  const arduino = getArduinoContext();
  const userDir = (arduino as { userDirPath?: string })?.userDirPath;
  if (!userDir || !fs.existsSync(userDir)) return undefined;
  const libPath = path.join(userDir, 'libraries');
  return fs.existsSync(libPath) && fs.statSync(libPath).isDirectory() ? libPath : undefined;
}

/** Read version from library.properties in a library folder. Returns undefined if not found. */
function getLibraryVersion(librariesPath: string, includePath: string): string | undefined {
  // includePath can be "EEPROM.h" or "Adafruit_GFX/Adafruit_GFX.h" → library folder is first segment or basename without .h
  const base = path.basename(includePath, '.h');
  const topDir = includePath.includes('/') ? includePath.split('/')[0]! : base;
  const propsPath = path.join(librariesPath, topDir, 'library.properties');
  if (!fs.existsSync(propsPath)) return undefined;
  try {
    const content = fs.readFileSync(propsPath, 'utf8');
    const m = content.match(/^\s*version\s*=\s*(.+)\s*$/m);
    return m ? m[1].trim() : undefined;
  } catch {
    return undefined;
  }
}

const INCLUDE_REGEX = /^(\s*#\s*include\s*[<"])([^>"]+)([>"])(\s*)(.*)$/;

/** Append version comment to each #include line when decoding a dump. */
function addIncludeVersions(decodedSource: string, librariesPath: string | undefined): string {
  if (!decodedSource) return decodedSource;
  const lines = decodedSource.split(/\r?\n/);
  const out: string[] = [];
  for (const line of lines) {
    const m = line.match(INCLUDE_REGEX);
    if (!m) {
      out.push(line);
      continue;
    }
    const [, pre, includePath, closing, space, rest] = m;
    const comment = (() => {
      if (librariesPath) {
        const ver = getLibraryVersion(librariesPath, includePath.trim());
        if (ver) return ` // version ${ver}`;
      }
      return ' // version number';
    })();
    // If line already has a trailing comment, keep it; otherwise append our comment
    const trimmedRest = rest.trim();
    const alreadyComment = /^\s*\/\/.*/.test(trimmedRest);
    const newRest = alreadyComment ? rest : (rest + comment);
    out.push(`${pre}${includePath}${closing}${space}${newRest}`.trimEnd());
  }
  return out.join('\n');
}

async function decodeFromSelection(out: vscode.OutputChannel): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage('Forgetfulino: no active editor/selection to decode from.');
    return;
  }

  const sel = editor.selection;
  const rawLine =
    !sel.isEmpty
      ? editor.document.getText(sel)
      : editor.document.lineAt(sel.active.line).text;

  const line = stripSerialTimestamp(rawLine);
  if (!line) {
    vscode.window.showErrorMessage('Forgetfulino: selection/line is empty.');
    return;
  }

  try {
    const bytes = ascii85Decode(line);
    const decoded = new TextDecoder('utf-8', { fatal: false }).decode(bytes);
    const librariesPath = getLibrariesPath();
    const withVersions = addIncludeVersions(decoded, librariesPath);

    out.show(true);
    out.appendLine('\nForgetfulino output:');
    out.appendLine(withVersions);

    // Also open in a new editor for easy copy
    const doc = await vscode.workspace.openTextDocument({
      content: withVersions,
      language: 'cpp'
    });
    await vscode.window.showTextDocument(doc, { preview: false });
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    out.appendLine(`\n[Forgetfulino] Decode error: ${msg}\n`);
    vscode.window.showErrorMessage('Forgetfulino: failed to decode compressed dump (is it a valid Forgetfulino string?).');
  }
}

async function setForgetfulinoConfig(key: string, value: boolean): Promise<void> {
  await vscode.workspace.getConfiguration('forgetfulino').update(key, value, vscode.ConfigurationTarget.Global);
}

export function activate(context: vscode.ExtensionContext): void {
  const out = getOutputChannel();

  // Long lines (e.g. Base85 dump from Serial) must be tokenized or the editor shows strange chars
  const editorCfg = vscode.workspace.getConfiguration('editor');
  const currentMax = editorCfg.get<number>('maxTokenizationLineLength');
  if (currentMax == null || currentMax < 200000) {
    editorCfg.update('maxTokenizationLineLength', 200000, vscode.ConfigurationTarget.Global);
  }

  context.subscriptions.push(
    vscode.commands.registerCommand('forgetfulino.generateHeaders', async () => {
      try {
        await generateHeadersCommand(out);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        out.appendLine(`\n[Forgetfulino] ERROR: ${msg}\n`);
        vscode.window.showErrorMessage(`Forgetfulino: ${msg}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forgetfulino.decodeFromSelection', async () => {
      try {
        await decodeFromSelection(out);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        out.appendLine(`\n[Forgetfulino] Decode command error: ${msg}\n`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forgetfulino.activateAutoGenerate', async () => {
      await setForgetfulinoConfig('autoGenerateOnSave', true);
      vscode.window.showInformationMessage('Forgetfulino: auto-generate on save activated.');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forgetfulino.deactivateAutoGenerate', async () => {
      await setForgetfulinoConfig('autoGenerateOnSave', false);
      vscode.window.showInformationMessage('Forgetfulino: auto-generate on save deactivated.');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forgetfulino.activateAutoInject', async () => {
      await setForgetfulinoConfig('autoInjectTemplate', true);
      vscode.window.showInformationMessage('Forgetfulino: auto-inject template activated.');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forgetfulino.deactivateAutoInject', async () => {
      await setForgetfulinoConfig('autoInjectTemplate', false);
      vscode.window.showInformationMessage('Forgetfulino: auto-inject template deactivated.');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forgetfulino.activateIncludeCommentsInDump', async () => {
      await setForgetfulinoConfig('includeCommentsInDump', true);
      vscode.window.showInformationMessage('Forgetfulino: comments will be included in the dump.');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forgetfulino.deactivateIncludeCommentsInDump', async () => {
      await setForgetfulinoConfig('includeCommentsInDump', false);
      vscode.window.showInformationMessage('Forgetfulino: comments will be stripped from the dump.');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forgetfulino.injectTemplateNow', async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || path.extname(editor.document.uri.fsPath).toLowerCase() !== '.ino') {
        vscode.window.showErrorMessage('Forgetfulino: open a .ino file first.');
        return;
      }
      const text = editor.document.getText();
      const isNewFile = !text.trim() || text.trim().replace(/\s+/g, '') === DEFAULT_ARDUINO_SKELETON;

      if (isNewFile) {
        const template = buildInjectTemplate();
        await editor.edit((builder) => {
          const fullRange = new vscode.Range(
            editor.document.positionAt(0),
            editor.document.positionAt(text.length)
          );
          builder.replace(fullRange, template);
        });
        vscode.window.showInformationMessage('Forgetfulino: template injected.');
        return;
      }

      const newContent = applyInjectToExistingFile(text);
      if (newContent === null) {
        vscode.window.showInformationMessage('Forgetfulino: already present, nothing to add.');
        return;
      }
      await editor.edit((builder) => {
        const fullRange = new vscode.Range(
          editor.document.positionAt(0),
          editor.document.positionAt(text.length)
        );
        builder.replace(fullRange, newContent);
      });
      vscode.window.showInformationMessage('Forgetfulino: inject applied (include + setup block).');
    })
  );

  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(async (doc) => {
      const cfg = vscode.workspace.getConfiguration('forgetfulino');
      const autoInject = cfg.get<boolean>('autoInjectTemplate');
      const autoGenerate = cfg.get<boolean>('autoGenerateOnSave');

      if (autoInject && shouldAutoInjectTemplate(doc)) {
        const editor = vscode.window.visibleTextEditors.find((e) => e.document === doc);
        if (editor) {
          const template = buildInjectTemplate();
          await editor.edit((builder) => {
            const fullRange = new vscode.Range(
              doc.positionAt(0),
              doc.positionAt(doc.getText().length)
            );
            builder.replace(fullRange, template);
          });
        }
      }

      if (autoGenerate && isSketchSource(doc)) {
        try {
          await generateHeadersCommand(out);
        } catch (e) {
          // Silent-ish: only log to output to avoid annoying users on every save.
          const msg = e instanceof Error ? e.message : String(e);
          out.appendLine(`\n[Forgetfulino] Auto-generate failed: ${msg}\n`);
        }
      }
    })
  );

  out.appendLine('[Forgetfulino] Extension active.');
}

