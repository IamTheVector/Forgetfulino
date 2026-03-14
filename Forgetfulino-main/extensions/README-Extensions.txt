Forgetfulino – IDE Extension
============================

This folder contains the **packaged Forgetfulino Arduino IDE 2.x extension** (`.vsix` file).

It is intentionally small and does **not** contain the full development project (`node_modules`, TypeScript sources, etc.).

Files you should find here
--------------------------

- `forgetfulino-arduino-ide-extension-<version>.vsix`
- `README-Extensions.txt` (this file)

How to install the extension (manual install)
---------------------------------------------

1. **Close Arduino IDE 2.x.**

2. Locate your **`.arduinoIDE`** configuration folder:

   - **Windows**: `C:\Users\<your_user>\.arduinoIDE\`
   - **macOS**: `/Users/<your_user>/.arduinoIDE/`
   - **Linux**: `/home/<your_user>/.arduinoIDE/`

3. Inside that folder, locate (or create) the subfolder:

   - `.arduinoIDE\extensions\`

4. Copy the Forgetfulino extension:

   - Option A (recommended):  
     copy **only** the file  
     `forgetfulino-arduino-ide-extension-<version>.vsix`  
     into `.arduinoIDE/extensions/`.

   - Option B:  
     copy the entire `extensions` folder from the Forgetfulino library  
     into your `.arduinoIDE/` folder, so you end up with for example:  
     `.arduinoIDE/extensions/forgetfulino-arduino-ide-extension-0.0.1.vsix`.

5. **Start Arduino IDE 2.x** again.

6. Verify that the plugin was deployed:

   - Open the folder:
     - `.arduinoIDE/deployedPlugins/`
   - Check that there is a file or folder whose name looks like  
     `forgetfulino-arduino-ide-extension-0.0.1` (or similar containing **“Forgetfulino”**).

Once deployed, the Forgetfulino extension will:

- auto-generate the Forgetfulino headers on save (if enabled),
- optionally auto-inject a Forgetfulino template into new sketches,
- provide commands to generate headers and decode compressed dumps.

