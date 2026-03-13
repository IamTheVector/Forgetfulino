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

function tryAutoDetectLibraryRoot(arduino: ArduinoContext | undefined): string | undefined {
  // ArduinoContext.userDirPath is the sketchbook path (directories.user)
  // Standard library install: <sketchbook>/libraries/Forgetfulino
  const userDir = (arduino as any)?.userDirPath as string | undefined;
  if (!userDir) return undefined;
  const candidate = path.join(userDir, 'libraries', 'Forgetfulino');
  if (fs.existsSync(candidate) && fs.statSync(candidate).isDirectory()) return candidate;
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
      const content = fs.readFileSync(p, 'utf8');
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

function toCStringLiteral(value: string, varName: string): string {
  const out: string[] = [];
  for (const ch of value) {
    if (ch === '\\') out.push('\\\\');
    else if (ch === '"') out.push('\\"');
    else if (ch === '\n') out.push('\\n');
    else if (ch === '\r') out.push('\\r');
    else if (ch === '\t') out.push('\\t');
    else out.push(ch);
  }
  const escaped = out.join('');
  return `const char ${varName}[] PROGMEM = "${escaped}";`;
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
  const compressedLiteral = toCStringLiteral(encoded, 'forgetfulino_compressed_data');

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

// Base85-compressed sketch source (null-terminated string)
${compressedLiteral}

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

      out.appendLine(`[Forgetfulino] Sketch: ${mainName}`);
      out.appendLine(`[Forgetfulino] Size: ${fullSource.length} bytes`);

      const sourceHeader = generateSourceHeader(fullSource, mainName);
      const compressedHeader = generateCompressedHeader(fullSource);

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

export function activate(context: vscode.ExtensionContext): void {
  const out = getOutputChannel();

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
    vscode.workspace.onDidSaveTextDocument(async (doc) => {
      const cfg = vscode.workspace.getConfiguration('forgetfulino');
      if (!cfg.get<boolean>('autoGenerateOnSave')) return;
      if (!isSketchSource(doc)) return;
      try {
        await generateHeadersCommand(out);
      } catch (e) {
        // Silent-ish: only log to output to avoid annoying users on every save.
        const msg = e instanceof Error ? e.message : String(e);
        out.appendLine(`\n[Forgetfulino] Auto-generate failed: ${msg}\n`);
      }
    })
  );

  out.appendLine('[Forgetfulino] Extension active.');
}

