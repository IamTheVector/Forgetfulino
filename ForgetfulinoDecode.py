import sys
import re
import base64
import lzma


def main() -> int:
    """
    Legge UNA riga da stdin, rimuove l'eventuale timestamp iniziale
    tipo '23:29:38.524 -> ' e prova a decodificare:
      1) Base85 + LZMA (vecchio formato)
      2) solo Base85 (nuovo formato)
    Stampa il codice su stdout e lo salva in 'sorgente_recuperato.ino'.
    """
    line = sys.stdin.readline().strip()
    if not line:
        sys.stderr.write("Nessun input ricevuto.\n")
        return 1

    # Rimuove timestamp tipo "23:29:38.524 -> " se presente
    line = re.sub(r"^\d+:\d+:\d+\.\d+\s*->\s*", "", line)

    data = None
    text = None

    # 1) Prova Base85 + LZMA (vecchio formato)
    try:
        data = lzma.decompress(base64.a85decode(line))
        text = data.decode("utf-8")
    except Exception:  # noqa: BLE001
        # 2) Prova solo Base85 (nuovo formato)
        try:
            data = base64.a85decode(line)
            text = data.decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"ERRORE DECODIFICA: {exc}\n")
            return 1

    # Stampa a schermo
    sys.stdout.write(text)

    # Salva anche su file
    try:
        with open("sorgente_recuperato.ino", "w", encoding="utf-8") as handle:
            handle.write(text)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"\nERRORE salvataggio file: {exc}\n")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

