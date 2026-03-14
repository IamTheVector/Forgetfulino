# Forgetfulino Arduino IDE 2.x Extension (WIP)

This folder contains a **VS Code extension** intended to run inside **Arduino IDE 2.x** (which supports VS Code-style extensions).

## Goals

- **Zero/near-zero user effort**: headers are generated automatically when saving sketch files.
- **Cross-platform**: Windows / macOS / Linux.

## Current state (MVP)

- Command: **Forgetfulino: Generate headers**
- Optional auto-generate on save for `.ino`, `.cpp`, `.c`
- Auto-detects sketch folder via Arduino IDE context (`sketchPath`) when available
- Auto-detects library path as `<sketchbook>/libraries/Forgetfulino` when available

## Settings

- `forgetfulino.autoGenerateOnSave` (default `true`)
- `forgetfulino.libraryRoot` (optional override)
- `forgetfulino.pythonCommand` (optional override)

## Development

From `extension/`:

```bash
npm install
npm run compile
```

## Package as VSIX

From `extension/`:

```bash
npm run package
```

This will produce a `.vsix` file in the `extension/` folder.

## Install into Arduino IDE 2.x (manual, user-level)

Arduino IDE 2.x can load VS Code extensions from your home directory.

- **Windows**: `%USERPROFILE%\.arduinoIDE\extensions`
- **macOS / Linux**: `~/.arduinoIDE/extensions`

Steps:

1. Create the folder if it doesn't exist.
2. Copy the generated `.vsix` into that folder.
3. Restart Arduino IDE.

If your Arduino IDE build does not load from `extensions/`, try `~/.arduinoIDE/plugins` instead.

