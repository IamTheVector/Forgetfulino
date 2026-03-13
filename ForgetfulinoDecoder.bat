@echo off
title Forgetfulino Decoder
echo ========================================
echo       FORGETFULINO OFFLINE DECODER
echo ========================================
echo.
echo Incolla QUI sotto la riga ricevuta via Serial
echo (puoi includere anche l'orario tipo "23:29:38.524 -> ...")
echo poi premi INVIO:
echo.

REM Qui NON leggiamo noi la riga: la legge direttamente lo script Python ForgetfulinoDecode.py
REM che si trova nella stessa cartella di questo .bat.

python "%~dp0ForgetfulinoDecode.py"

echo.
echo.
if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Il codice e' stato scritto anche in 'sorgente_recuperato.ino'
) else (
    echo.
    echo ERRORE: Qualcosa e' andato storto, controlla la stringa.
)
pause
