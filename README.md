# Forgetfulino

This repository contains:

- **Forgetfulino-main/** – the **Arduino library** folder (this is the only folder that must be installed under `Arduino/libraries`). It contains:
  - `library.properties` (library metadata, version, URL)
  - `src/` (Forgetfulino library sources and generated headers)
  - `examples/` (Arduino example sketches)
  - `tools/` (lightweight helper scripts, if any)
  - `extensions/` (packaged IDE extension VSIX + `README-Extensions.txt` explaining how to install it)
  - `README.md` (user documentation for the Arduino library)
- **extension build/** – the full development project for the Arduino IDE 2.x extension (TypeScript sources, config files, etc.). This **is not part of the Arduino library ZIP**.

## Arduino Library Manager

When submitting this project to the Arduino Library Manager, the library root is:

`Forgetfulino-main`

Only that folder (and its contents) should be distributed as the Forgetfulino library.

