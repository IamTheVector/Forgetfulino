Forgetfulino – IDE Extensions
=============================

This folder is meant to contain ONLY lightweight build artifacts related to the Forgetfulino Arduino IDE 2.x extension, NOT the full extension development project.

What should be stored here
--------------------------

- The packaged extension file:
  - `forgetfulino-arduino-ide-extension-<version>.vsix`
- Optional:
  - A short changelog for the extension
  - Additional README files or release notes

What must NOT be stored here
----------------------------

- No `node_modules/` folders
- No full TypeScript sources of the extension
- No build caches or large development-only artifacts

Those development files belong in the separate `extension-build` (or similar) folder at the repository root and are NOT distributed as part of the Arduino library ZIP.

How the user installs the extension
-----------------------------------

1. Locate the VSIX file in this folder, e.g.:

   `forgetfulino-arduino-ide-extension-0.0.1.vsix`

2. Open **Arduino IDE 2.x**.
3. Open the **Extensions** view.
4. Use **“Install from VSIX…”**.
5. Select the Forgetfulino VSIX file.
6. Restart Arduino IDE if requested.

After installation, the Forgetfulino extension will:
- auto-generate the Forgetfulino headers on save (if enabled),
- optionally auto-inject a Forgetfulino template into new sketches,
- provide commands to generate headers and decode compressed dumps.

