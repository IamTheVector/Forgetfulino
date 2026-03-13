@echo off
REM Avvia Watcher Forgetfulino (in tray, gia' attivo) e poi Arduino IDE.
REM Usa questo .bat come scorciatoia "Arduino IDE": un solo clic, il Watcher e' trasparente.
REM Prima volta: apri il Watcher dalla cartella tools, imposta Opzioni -> Percorso Arduino IDE.

pythonw "%~dp0launch_arduino_with_forgetfulino.py"
if %errorlevel% neq 0 (
    python "%~dp0launch_arduino_with_forgetfulino.py"
)
