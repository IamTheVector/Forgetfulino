import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { spawn } from 'child_process';
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

function parsePythonCommandSetting(): { cmd: string; args: string[] } | undefined {
  const cfg = vscode.workspace.getConfiguration('forgetfulino');
  const raw = (cfg.get<string>('pythonCommand') ?? '').trim();
  if (!raw) return undefined;

  // Minimal split respecting quotes is overkill here; keep it simple:
  // allow forms like: py -3
  const parts = raw.split(' ').filter(Boolean);
  return { cmd: parts[0]!, args: parts.slice(1) };
}

async function spawnAndWait(
  cmd: string,
  args: string[],
  cwd: string,
  env: NodeJS.ProcessEnv,
  out: vscode.OutputChannel
): Promise<number> {
  return await new Promise((resolve, reject) => {
    const child = spawn(cmd, args, { cwd, env, windowsHide: true });
    child.stdout.on('data', (d) => out.append(d.toString()));
    child.stderr.on('data', (d) => out.append(d.toString()));
    child.on('error', reject);
    child.on('close', (code) => resolve(code ?? 1));
  });
}

async function runGenerator(sketchFolder: string, libraryRoot: string, out: vscode.OutputChannel): Promise<void> {
  const generatorPath = path.join(libraryRoot, 'tools', 'forgetfulino_generator.py');
  if (!fs.existsSync(generatorPath)) {
    throw new Error(`Generator not found at: ${generatorPath}`);
  }

  const pythonSetting = parsePythonCommandSetting();
  const candidates: Array<{ cmd: string; args: string[] }> = pythonSetting
    ? [pythonSetting]
    : [
        { cmd: 'python3', args: [] },
        { cmd: 'python', args: [] },
        { cmd: 'py', args: ['-3'] }
      ];

  const env = { ...process.env, FORGETFULINO_LIBRARY_ROOT: libraryRoot };
  let lastErr: unknown = undefined;

  for (const c of candidates) {
    try {
      out.appendLine(`\n[Forgetfulino] Running: ${c.cmd} ${[...c.args, generatorPath].join(' ')}`);
      const code = await spawnAndWait(c.cmd, [...c.args, generatorPath], sketchFolder, env, out);
      if (code === 0) return;
      lastErr = new Error(`Generator failed with exit code ${code}`);
    } catch (e) {
      lastErr = e;
    }
  }

  throw lastErr instanceof Error ? lastErr : new Error('Failed to run generator (Python not found?)');
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

  out.show(true);
  out.appendLine(`[Forgetfulino] Sketch folder: ${sketchFolder}`);
  out.appendLine(`[Forgetfulino] Library root: ${libraryRoot}`);

  await vscode.window.withProgress(
    { location: vscode.ProgressLocation.Notification, title: 'Forgetfulino: generating headers…', cancellable: false },
    async () => {
      await runGenerator(sketchFolder, libraryRoot, out);
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

  out.appendLine('[Forgetfulino] Extension activated.');
}

