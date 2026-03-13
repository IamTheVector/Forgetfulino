#!/usr/bin/env python3
"""
Forgetfulino Watcher & Decoder — cross-platform GUI (Windows, macOS, Linux).

- Watcher: monitors a sketch folder and runs the generator when .ino files change.
- Decoder: paste compressed string, decompress and view/copy result.
- Minimizes to system tray so it does not get in the way.
- Configurable sketch path and automatic language (EN/IT).
"""

from __future__ import annotations

import base64
import json
import locale
import lzma
import os
import re
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Callable

# Optional GUI and watcher deps (install via requirements-watcher.txt)
try:
    import customtkinter as ctk
    from watchdog.events import FileSystemEvent, FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError as e:
    print("Missing dependencies. Install with: pip install -r tools/requirements-watcher.txt", file=sys.stderr)
    raise SystemExit(1) from e

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None  # type: ignore
    Image = None
    ImageDraw = None

# -----------------------------------------------------------------------------
# i18n — all user-facing strings (code and comments in English)
# -----------------------------------------------------------------------------

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "Forgetfulino Watcher & Decoder",
        "paste_here": "Paste compressed string here",
        "paste_hint": "Paste the line from Serial Monitor (with or without timestamp, e.g. 23:29:38.524 -> …)",
        "decompressed": "Decompressed source",
        "decompressed_hint": "Recovered sketch code appears here. You can copy it.",
        "decompress_btn": "Decompress",
        "decompress_hint": "Decodes the pasted Base85 string and shows the source below.",
        "sketch_path": "Sketch folder to watch",
        "sketch_path_hint": "Folder that contains your .ino file. The watcher will regenerate headers when you save.",
        "browse": "Browse",
        "start_watcher": "Start watcher",
        "stop_watcher": "Stop watcher",
        "watcher_status_stopped": "Watcher: stopped",
        "watcher_status_running": "Watcher: running",
        "watcher_hint": "Start to monitor the sketch folder; stop when you are done.",
        "language": "Language",
        "language_hint": "Interface language (restart or change to apply everywhere).",
        "library_path": "Library folder (standalone app)",
        "library_path_hint": "Path to Forgetfulino library so the watcher can write generated headers. Auto-detected if empty.",
        "section_options": "Options",
        "option_launch_arduino": "Launch Arduino IDE when Watcher starts",
        "option_launch_arduino_hint": "If checked, Arduino IDE is opened when you start this app, so you don't forget to run the watcher.",
        "arduino_ide_path": "Arduino IDE path",
        "option_auto_inject": "Auto-inject Forgetfulino template in new sketches",
        "option_auto_inject_hint": "When a .ino file in the watched folder does not include Forgetfulino, add the template (include + Serial.begin, delay, dumpCompressed in setup).",
        "log_title": "Log",
        "log_modified": "File modified: {file} — headers generated.",
        "error_decode": "Decode error",
        "error_no_input": "Paste a compressed string first.",
        "error_path": "Choose a valid sketch folder.",
        "error_library_path": "When using the standalone app, set the Forgetfulino library folder (or install the library in Documents/Arduino/libraries/Forgetfulino).",
        "success_decompress": "Decompressed successfully.",
        "tray_show": "Show",
        "tray_quit": "Quit",
        "create_shortcut": "Create shortcut: ARDUINO + FORGETFULINO",
        "create_shortcut_hint": "Creates a shortcut on the Desktop. Use it to open Arduino with the Watcher in the tray.",
        "success_shortcut": "Shortcut created on Desktop: ARDUINO + FORGETFULINO",
        "error_shortcut_no_ide": "Set the Arduino IDE path above first (click Browse), then create the shortcut.",
        "error_shortcut_failed": "Could not create shortcut",
    },
    "it": {
        "app_title": "Forgetfulino Watcher e Decoder",
        "paste_here": "Incolla qui la stringa compressa",
        "paste_hint": "Incolla la riga dal Serial Monitor (con o senza orario, es. 23:29:38.524 -> …)",
        "decompressed": "Sorgente decompresso",
        "decompressed_hint": "Qui appare il codice recuperato. Puoi copiarlo.",
        "decompress_btn": "Decomprimi",
        "decompress_hint": "Decodifica la stringa Base85 incollata e mostra il sorgente sotto.",
        "sketch_path": "Cartella sketch da monitorare",
        "sketch_path_hint": "Cartella che contiene il file .ino. Il watcher rigenera gli header quando salvi.",
        "browse": "Sfoglia",
        "start_watcher": "Avvia watcher",
        "stop_watcher": "Ferma watcher",
        "watcher_status_stopped": "Watcher: fermo",
        "watcher_status_running": "Watcher: attivo",
        "watcher_hint": "Avvia per monitorare la cartella sketch; ferma quando hai finito.",
        "language": "Lingua",
        "language_hint": "Lingua dell'interfaccia (cambia per applicare a menu e testi).",
        "library_path": "Cartella libreria (app standalone)",
        "library_path_hint": "Percorso alla libreria Forgetfulino per scrivere gli header generati. Se vuoto viene rilevato automaticamente.",
        "section_options": "Opzioni",
        "option_launch_arduino": "Avvia Arduino IDE all'avvio del Watcher",
        "option_launch_arduino_hint": "Se attivo, Arduino IDE si apre quando avvii questa app, così non dimentichi di avere il watcher attivo.",
        "arduino_ide_path": "Percorso Arduino IDE",
        "option_auto_inject": "Inserisci automaticamente il template Forgetfulino nei nuovi sketch",
        "option_auto_inject_hint": "Se un file .ino nella cartella monitorata non include Forgetfulino, aggiunge il template (include + Serial.begin, delay, dumpCompressed in setup).",
        "log_title": "Log",
        "log_modified": "File modificato: {file} — header generati.",
        "error_decode": "Errore decodifica",
        "error_no_input": "Incolla prima la stringa compressa.",
        "error_path": "Scegli una cartella sketch valida.",
        "error_library_path": "Usando l'app standalone, imposta la cartella della libreria Forgetfulino (o installala in Documents/Arduino/libraries/Forgetfulino).",
        "success_decompress": "Decompresso con successo.",
        "tray_show": "Mostra",
        "tray_quit": "Esci",
        "create_shortcut": "Crea scorciatoia: ARDUINO + FORGETFULINO",
        "create_shortcut_hint": "Crea una scorciatoia sul Desktop. Usala per aprire Arduino con il Watcher in tray.",
        "success_shortcut": "Scorciatoia creata sul Desktop: ARDUINO + FORGETFULINO",
        "error_shortcut_no_ide": "Imposta prima il percorso Arduino IDE sopra (Sfoglia), poi crea la scorciatoia.",
        "error_shortcut_failed": "Impossibile creare la scorciatoia",
    },
}


def _detect_language() -> str:
    try:
        lang, _ = locale.getlocale()
        if lang:
            lang = (lang or "").lower()
            if lang.startswith("it"):
                return "it"
    except Exception:
        pass
    return "en"


def t(key: str, lang: str | None = None) -> str:
    if lang is None:
        lang = getattr(t, "_lang", "en")
    return STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))


# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------

def _app_config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", os.path.expanduser("~")))
    else:
        base = Path(os.path.expanduser("~"))
    return base / "Forgetfulino"


def _config_path() -> Path:
    return _app_config_dir() / "watcher_config.json"


def load_config() -> dict[str, Any]:
    path = _config_path()
    defaults = {
        "sketch_path": "",
        "language": "auto",
        "library_path": "",
        "launch_arduino_with_watcher": False,
        "arduino_ide_path": "",
        "auto_inject_template": False,
        "template_top": "#include <Forgetfulino.h>",
        "template_setup": "Serial.begin(115200);\n  delay(1000);\n  Forgetfulino.dumpCompressed();",
    }
    if not path.exists():
        return defaults.copy()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
        return data
    except Exception:
        return defaults.copy()


def save_config(cfg: dict[str, Any]) -> None:
    _app_config_dir().mkdir(parents=True, exist_ok=True)
    with open(_config_path(), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


# -----------------------------------------------------------------------------
# Decode logic (same as ForgetfulinoDecode.py)
# -----------------------------------------------------------------------------

def decompress_string(raw: str) -> tuple[bool, str]:
    """
    Returns (success, result_text_or_error_message).
    Strips optional timestamp prefix (e.g. 23:29:38.524 -> ) then tries Base85+LZMA, then Base85 only.
    """
    line = raw.strip()
    if not line:
        return False, "error_no_input"
    line = re.sub(r"^\d+:\d+:\d+\.\d+\s*->\s*", "", line)
    try:
        data = lzma.decompress(base64.a85decode(line))
        return True, data.decode("utf-8")
    except Exception:
        try:
            data = base64.a85decode(line)
            return True, data.decode("utf-8", errors="replace")
        except Exception as e:
            return False, str(e)


# -----------------------------------------------------------------------------
# Watcher — runs generator when .ino changes
# -----------------------------------------------------------------------------

def _detect_library_root() -> Path | None:
    """Try to find Forgetfulino library root (for standalone app). Returns None if not found."""
    home = Path.home()
    candidates = [
        home / "Documents" / "Arduino" / "libraries" / "Forgetfulino",
        home / "Arduino" / "libraries" / "Forgetfulino",
        home / "Dropbox" / "Arduino" / "libraries" / "Forgetfulino",
    ]
    if sys.platform == "win32":
        candidates.extend([
            Path(os.environ.get("USERPROFILE", home)) / "Documents" / "Arduino" / "libraries" / "Forgetfulino",
            Path(os.environ.get("USERPROFILE", home)) / "Dropbox" / "Arduino" / "libraries" / "Forgetfulino",
        ])
    for p in candidates:
        if (p / "src" / "Forgetfulino.h").exists():
            return p
    return None


def _generator_script_path() -> Path:
    """Path to generator script: from bundle when frozen (PyInstaller), else from script dir."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "forgetfulino_generator.py"
    return Path(__file__).resolve().parent / "forgetfulino_generator.py"


class SketchWatcherHandler(FileSystemEventHandler):
    def __init__(self, generator_path: Path, app: "ForgetfulinoApp") -> None:
        self.generator_path = generator_path
        self.app = app

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if not event.src_path.endswith(".ino"):
            return
        path = event.src_path
        sketch_folder = os.path.dirname(path)
        try:
            # Optional: auto-inject template if enabled and file doesn't have Forgetfulino
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                content = ""
            cfg = self.app.get_inject_config()
            if cfg.get("auto_inject_template") and "Forgetfulino" not in content:
                self.app._do_inject(path)
            # Run generator
            if getattr(sys, "frozen", False):
                import runpy
                old_argv = list(sys.argv)
                sys.argv = [sys.argv[0], sketch_folder]
                try:
                    runpy.run_path(str(self.generator_path), run_name="__main__")
                finally:
                    sys.argv = old_argv
            else:
                subprocess.run(
                    [sys.executable, str(self.generator_path), sketch_folder],
                    check=True,
                    capture_output=True,
                    timeout=30,
                )
            basename = os.path.basename(path)
            self.app.after(0, lambda: self.app._append_log(t("log_modified").format(file=basename)))
        except Exception:
            pass  # avoid crashing observer thread


# -----------------------------------------------------------------------------
# Tray icon (optional)
# -----------------------------------------------------------------------------

def _make_tray_image() -> "Image.Image":
    if Image is None or ImageDraw is None:
        raise RuntimeError("PIL required for tray")
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Simple "F" shape
    d.rectangle([8, 8, 56, 56], fill=(70, 130, 180), outline=(50, 100, 150))
    d.text((18, 18), "F", fill=(255, 255, 255))
    return img


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

class ForgetfulinoApp(ctk.CTk):
    def __init__(self, start_watching: bool = False, minimize_to_tray: bool = False) -> None:
        super().__init__()
        self._start_watching_on_load = start_watching
        self._minimize_to_tray_on_load = minimize_to_tray

        self.config = load_config()
        lang_cfg = self.config.get("language", "auto")
        t._lang = "it" if lang_cfg == "it" else ("en" if lang_cfg == "en" else _detect_language())
        self.lang_var = ctk.StringVar(value=lang_cfg if lang_cfg in ("en", "it") else _detect_language())

        self.observer: Observer | None = None
        self.tray_icon: "pystray.Icon | None" = None
        self._tray_thread: threading.Thread | None = None
        self._hiding_to_tray = False

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.geometry("960x720")
        self.minsize(560, 500)
        self._build_ui()
        self._apply_lang()
        self.after(500, self._maybe_launch_arduino)
        self.after(900, self._on_launcher_startup)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        if sys.platform == "win32":
            self.bind("<Unmap>", self._on_unmap)

        if self._minimize_to_tray_on_load:
            self.withdraw()

    def _build_ui(self) -> None:
        self.title(t("app_title"))
        # Row 1: language, sketch path, browse, watcher button
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=6)
        self.label_lang = ctk.CTkLabel(row1, text=t("language") + ":")
        self.label_lang.pack(side="left", padx=(0, 4))
        self.lang_menu = ctk.CTkOptionMenu(
            row1, values=["auto", "en", "it"], variable=self.lang_var, width=80, command=self._on_lang_change
        )
        self.lang_menu.pack(side="left", padx=(0, 12))
        self.label_sketch = ctk.CTkLabel(row1, text=t("sketch_path") + ":")
        self.label_sketch.pack(side="left", padx=(0, 4))
        self.path_entry = ctk.CTkEntry(row1, placeholder_text="C:\\... or /home/...", width=280)
        self.path_entry.pack(side="left", fill="x", expand=True, padx=4)
        if self.config.get("sketch_path"):
            self.path_entry.insert(0, self.config["sketch_path"])
        self.btn_browse = ctk.CTkButton(row1, text=t("browse"), width=72, command=self._browse)
        self.btn_browse.pack(side="left", padx=2)
        self.watcher_btn = ctk.CTkButton(row1, text=t("start_watcher"), width=110, command=self._toggle_watcher)
        self.watcher_btn.pack(side="left", padx=4)

        # Row 2: Watcher status + Log (always visible)
        row2 = ctk.CTkFrame(self, fg_color=("gray90", "gray25"))
        row2.pack(fill="x", padx=10, pady=(0, 6))
        self.watcher_label = ctk.CTkLabel(row2, text=t("watcher_status_stopped"), text_color="gray", font=("", 12))
        self.watcher_label.pack(side="left", padx=8, pady=6)
        self.label_log = ctk.CTkLabel(row2, text=t("log_title") + ":", font=("", 10))
        self.label_log.pack(side="left", padx=(4, 0))
        self.log_text = ctk.CTkTextbox(row2, height=48, font=("Consolas", 10), wrap="word", state="disabled")
        self.log_text.pack(side="left", fill="x", expand=True, padx=4, pady=4)

        # Row 3: Library path
        row3 = ctk.CTkFrame(self, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=(0, 6))
        self.label_library = ctk.CTkLabel(row3, text=t("library_path") + ":")
        self.label_library.pack(side="left", padx=(0, 4))
        self.library_entry = ctk.CTkEntry(row3, placeholder_text="Optional; auto-detected if empty", width=320)
        self.library_entry.pack(side="left", fill="x", expand=True, padx=4)
        if self.config.get("library_path"):
            self.library_entry.insert(0, self.config["library_path"])
        self.btn_browse_lib = ctk.CTkButton(row3, text=t("browse"), width=72, command=self._browse_library)
        self.btn_browse_lib.pack(side="left", padx=2)

        # Options frame
        opt_f = ctk.CTkFrame(self, fg_color=("gray92", "gray22"))
        opt_f.pack(fill="x", padx=10, pady=(0, 6))
        self.label_options = ctk.CTkLabel(opt_f, text=t("section_options"), font=("", 12))
        self.label_options.pack(anchor="w", padx=8, pady=(6, 2))
        self.var_launch_arduino = ctk.BooleanVar(value=self.config.get("launch_arduino_with_watcher", False))
        self.cb_launch_arduino = ctk.CTkCheckBox(
            opt_f, text=t("option_launch_arduino"), variable=self.var_launch_arduino, command=self._save_options
        )
        self.cb_launch_arduino.pack(anchor="w", padx=8, pady=2)
        self.hint_launch = ctk.CTkLabel(opt_f, text=t("option_launch_arduino_hint"), font=("", 10), text_color="gray", anchor="w")
        self.hint_launch.pack(anchor="w", padx=24, pady=(0, 2))
        row_ide = ctk.CTkFrame(opt_f, fg_color="transparent")
        row_ide.pack(fill="x", padx=24, pady=2)
        self.label_ide = ctk.CTkLabel(row_ide, text=t("arduino_ide_path") + ":")
        self.label_ide.pack(side="left", padx=(0, 4))
        self.ide_path_entry = ctk.CTkEntry(row_ide, width=300)
        self.ide_path_entry.pack(side="left", fill="x", expand=True, padx=2)
        if self.config.get("arduino_ide_path"):
            self.ide_path_entry.insert(0, self.config["arduino_ide_path"])
        ctk.CTkButton(row_ide, text=t("browse"), width=72, command=self._browse_ide).pack(side="left", padx=2)
        row_shortcut = ctk.CTkFrame(opt_f, fg_color="transparent")
        row_shortcut.pack(fill="x", padx=24, pady=(4, 2))
        self.btn_create_shortcut = ctk.CTkButton(
            row_shortcut, text=t("create_shortcut"), width=280, command=self._create_shortcut
        )
        self.btn_create_shortcut.pack(side="left", padx=(0, 8))
        self.hint_shortcut = ctk.CTkLabel(
            row_shortcut, text=t("create_shortcut_hint"), font=("", 10), text_color="gray", anchor="w"
        )
        self.hint_shortcut.pack(side="left", fill="x", expand=True)
        self.var_auto_inject = ctk.BooleanVar(value=self.config.get("auto_inject_template", False))
        self.cb_auto_inject = ctk.CTkCheckBox(
            opt_f, text=t("option_auto_inject"), variable=self.var_auto_inject, command=self._save_options
        )
        self.cb_auto_inject.pack(anchor="w", padx=8, pady=(8, 2))
        self.hint_inject = ctk.CTkLabel(opt_f, text=t("option_auto_inject_hint"), font=("", 10), text_color="gray", anchor="w")
        self.hint_inject.pack(anchor="w", padx=24, pady=(0, 6))

        # Main: two text areas with hints
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=10, pady=4)
        left_frame = ctk.CTkFrame(main, fg_color=("gray85", "gray20"))
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 4))
        self.label_paste = ctk.CTkLabel(left_frame, text=t("paste_here"), anchor="w")
        self.label_paste.pack(fill="x", padx=8, pady=4)
        self.hint_paste = ctk.CTkLabel(left_frame, text=t("paste_hint"), font=("", 9), text_color="gray", anchor="w")
        self.hint_paste.pack(fill="x", padx=8, pady=(0, 2))
        self.paste_text = ctk.CTkTextbox(left_frame, font=("Consolas", 11), wrap="word")
        self.paste_text.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        right_frame = ctk.CTkFrame(main, fg_color=("gray85", "gray20"))
        right_frame.pack(side="right", fill="both", expand=True, padx=(4, 0))
        self.label_decompressed = ctk.CTkLabel(right_frame, text=t("decompressed"), anchor="w")
        self.label_decompressed.pack(fill="x", padx=8, pady=4)
        self.hint_decompressed = ctk.CTkLabel(right_frame, text=t("decompressed_hint"), font=("", 9), text_color="gray", anchor="w")
        self.hint_decompressed.pack(fill="x", padx=8, pady=(0, 2))
        self.result_text = ctk.CTkTextbox(right_frame, font=("Consolas", 11), wrap="word")
        self.result_text.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        # Bottom: Decompress with hint
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=10, pady=8)
        self.decompress_btn = ctk.CTkButton(
            bottom, text=t("decompress_btn"), width=140, height=36, command=self._decompress, font=("", 14)
        )
        self.decompress_btn.pack(side="left", pady=4)
        self.hint_decompress = ctk.CTkLabel(bottom, text=t("decompress_hint"), font=("", 9), text_color="gray")
        self.hint_decompress.pack(side="left", padx=12, pady=4)

    def _apply_lang(self) -> None:
        lang = self.lang_var.get()
        t._lang = "it" if lang == "it" else ("en" if lang == "en" else _detect_language())
        self.title(t("app_title"))
        self.label_lang.configure(text=t("language") + ":")
        self.label_sketch.configure(text=t("sketch_path") + ":")
        self.btn_browse.configure(text=t("browse"))
        self.watcher_btn.configure(text=t("stop_watcher" if self.observer else "start_watcher"))
        self.watcher_label.configure(text=t("watcher_status_running" if self.observer else "watcher_status_stopped"))
        self.label_log.configure(text=t("log_title") + ":")
        self.label_library.configure(text=t("library_path") + ":")
        self.btn_browse_lib.configure(text=t("browse"))
        self.label_options.configure(text=t("section_options"))
        self.cb_launch_arduino.configure(text=t("option_launch_arduino"))
        self.hint_launch.configure(text=t("option_launch_arduino_hint"))
        self.label_ide.configure(text=t("arduino_ide_path") + ":")
        self.btn_create_shortcut.configure(text=t("create_shortcut"))
        self.hint_shortcut.configure(text=t("create_shortcut_hint"))
        self.cb_auto_inject.configure(text=t("option_auto_inject"))
        self.hint_inject.configure(text=t("option_auto_inject_hint"))
        self.label_paste.configure(text=t("paste_here"))
        self.hint_paste.configure(text=t("paste_hint"))
        self.label_decompressed.configure(text=t("decompressed"))
        self.hint_decompressed.configure(text=t("decompressed_hint"))
        self.decompress_btn.configure(text=t("decompress_btn"))
        self.hint_decompress.configure(text=t("decompress_hint"))

    def get_inject_config(self) -> dict[str, Any]:
        return {
            "auto_inject_template": self.var_auto_inject.get(),
            "template_top": self.config.get("template_top", "#include <Forgetfulino.h>"),
            "template_setup": self.config.get("template_setup", "Serial.begin(115200);\n  delay(1000);\n  Forgetfulino.dumpCompressed();"),
        }

    def _do_inject(self, ino_path: str) -> bool:
        try:
            with open(ino_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return False
        if "Forgetfulino" in content:
            return False
        top = self.config.get("template_top", "#include <Forgetfulino.h>")
        setup_code = self.config.get("template_setup", "Serial.begin(115200);\n  delay(1000);\n  Forgetfulino.dumpCompressed();")
        setup_lines = "\n  ".join(setup_code.strip().split("\n"))
        if top.strip() and top.strip() not in content:
            content = top.strip() + "\n\n" + content
        match = re.search(r"void\s+setup\s*\(\s*\)\s*\{", content)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + "\n  " + setup_lines + "\n" + content[insert_pos:]
        try:
            with open(ino_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            return False
        return True

    def _append_log(self, msg: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _save_options(self) -> None:
        self.config["launch_arduino_with_watcher"] = self.var_launch_arduino.get()
        self.config["arduino_ide_path"] = self.ide_path_entry.get().strip()
        self.config["auto_inject_template"] = self.var_auto_inject.get()
        save_config(self.config)

    def _browse_ide(self) -> None:
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title=t("arduino_ide_path"),
            filetypes=[("Executable", "*.exe"), ("Application", "*.app"), ("All", "*")],
        )
        if path:
            self.ide_path_entry.delete(0, "end")
            self.ide_path_entry.insert(0, path)
            self.config["arduino_ide_path"] = path
            save_config(self.config)

    def _create_shortcut(self) -> None:
        from tkinter import messagebox
        ide_path = (self.ide_path_entry.get() or "").strip()
        if not ide_path or not os.path.isfile(ide_path):
            messagebox.showwarning(t("error_shortcut_failed"), t("error_shortcut_no_ide"))
            return
        self.config["arduino_ide_path"] = ide_path
        save_config(self.config)
        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            desktop = Path.home()
        shortcut_name = "ARDUINO + FORGETFULINO.bat"
        shortcut_path = desktop / shortcut_name
        try:
            if getattr(sys, "frozen", False):
                exe_path = Path(sys.executable).resolve()
                bat_lines = [
                    "@echo off",
                    f'start "" "{exe_path}" --start-watching --minimize',
                    "timeout /t 2 /nobreak >nul",
                    f'start "" "{ide_path}"',
                ]
            else:
                tools_dir = Path(__file__).resolve().parent
                bat_lines = [
                    "@echo off",
                    f'cd /d "{tools_dir}"',
                    "pythonw launch_arduino_with_forgetfulino.py",
                    "if errorlevel 1 python launch_arduino_with_forgetfulino.py",
                ]
            with open(shortcut_path, "w", encoding="utf-8", newline="\r\n") as f:
                f.write("\n".join(bat_lines))
            messagebox.showinfo(t("success_decompress"), t("success_shortcut"))
        except Exception as e:
            messagebox.showerror(t("error_shortcut_failed"), f"{t('error_shortcut_failed')}: {e}")

    def _maybe_launch_arduino(self) -> None:
        if not self.config.get("launch_arduino_with_watcher"):
            return
        path = (self.ide_path_entry.get() or self.config.get("arduino_ide_path") or "").strip()
        if path and os.path.isfile(path):
            try:
                subprocess.Popen([path])
            except Exception:
                pass

    def _on_launcher_startup(self) -> None:
        """When started via launcher (--start-watching --minimize): start watcher then show only in tray."""
        if self._start_watching_on_load:
            path = self.path_entry.get().strip()
            if path and os.path.isdir(path):
                self._start_watcher()
        if self._minimize_to_tray_on_load and pystray is not None:
            self._hide_to_tray()

    def _on_lang_change(self, value: str) -> None:
        self.config["language"] = value
        save_config(self.config)
        self._apply_lang()

    def _browse(self) -> None:
        from tkinter import filedialog
        path = filedialog.askdirectory(title=t("sketch_path"))
        if path:
            self.path_entry.delete(0, "end")
            self.path_entry.insert(0, path)
            self.config["sketch_path"] = path
            save_config(self.config)

    def _browse_library(self) -> None:
        from tkinter import filedialog
        path = filedialog.askdirectory(title=t("library_path"))
        if path:
            self.library_entry.delete(0, "end")
            self.library_entry.insert(0, path)
            self.config["library_path"] = path
            save_config(self.config)

    def _toggle_watcher(self) -> None:
        if self.observer and self.observer.is_alive():
            self._stop_watcher()
        else:
            self._start_watcher()

    def _start_watcher(self) -> None:
        path = self.path_entry.get().strip()
        if not path or not os.path.isdir(path):
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", t("error_path"))
            return
        self.config["sketch_path"] = path
        if getattr(sys, "frozen", False):
            lib_path = self.library_entry.get().strip() or (self.config.get("library_path") or "").strip()
            if not lib_path or not os.path.isdir(lib_path):
                lib_root = _detect_library_root()
                if lib_root is None:
                    self.result_text.delete("1.0", "end")
                    self.result_text.insert("1.0", t("error_library_path"))
                    return
                lib_path = str(lib_root)
            self.config["library_path"] = lib_path
            os.environ["FORGETFULINO_LIBRARY_ROOT"] = lib_path
        save_config(self.config)
        gen = _generator_script_path()
        if not gen.exists():
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", "Generator script not found: " + str(gen))
            return
        handler = SketchWatcherHandler(gen, self)
        self.observer = Observer()
        self.observer.schedule(handler, path, recursive=True)
        self.observer.start()
        self.watcher_btn.configure(text=t("stop_watcher"))
        self.watcher_label.configure(text=t("watcher_status_running"), text_color="lime")

    def _stop_watcher(self) -> None:
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2)
            self.observer = None
        self.watcher_btn.configure(text=t("start_watcher"))
        self.watcher_label.configure(text=t("watcher_status_stopped"), text_color="gray")

    def _decompress(self) -> None:
        raw = self.paste_text.get("1.0", "end")
        ok, msg = decompress_string(raw)
        self.result_text.delete("1.0", "end")
        if ok:
            self.result_text.insert("1.0", msg)
            self.result_text.insert("end", "\n\n" + t("success_decompress"))
        else:
            lang = getattr(t, "_lang", "en")
            keys = list(STRINGS.get(lang, STRINGS["en"]).keys())
            display = t(msg) if msg in keys else msg
            self.result_text.insert("1.0", f"{t('error_decode')}: {display}")

    def _on_unmap(self, event: Any) -> None:
        if getattr(self, "_hiding_to_tray", False):
            return
        try:
            if self.state() == "iconic" and pystray is not None:
                self.after(100, self._hide_to_tray)
        except Exception:
            pass

    def _hide_to_tray(self) -> None:
        if not pystray or self.tray_icon is not None:
            return
        self._hiding_to_tray = True
        try:
            try:
                icon_image = _make_tray_image()
            except Exception:
                return
            menu = pystray.Menu(
                pystray.MenuItem(t("tray_show"), self._show_from_tray, default=True),
                pystray.MenuItem(t("tray_quit"), self._quit_from_tray),
            )
            self.tray_icon = pystray.Icon("forgetfulino", icon_image, t("app_title"), menu)
            self.withdraw()
            self._tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self._tray_thread.start()
        finally:
            self._hiding_to_tray = False

    def _show_from_tray(self, *args: Any) -> None:
        if self.tray_icon:
            self.after(0, self._do_show_from_tray)

    def _do_show_from_tray(self) -> None:
        self.deiconify()
        self.lift()
        self.focus_force()
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
            self.tray_icon = None

    def _quit_from_tray(self, *args: Any) -> None:
        self.after(0, self._on_close)

    def _on_close(self) -> None:
        self._stop_watcher()
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.destroy()


def _parse_launcher_flags() -> tuple[bool, bool]:
    """Parse --start-watching and --minimize from argv; remove them so GUI code doesn't see them."""
    start_watching = "--start-watching" in sys.argv
    minimize = "--minimize" in sys.argv
    sys.argv = [a for a in sys.argv if a not in ("--start-watching", "--minimize")]
    return start_watching, minimize


def main() -> None:
    start_watching, minimize_to_tray = _parse_launcher_flags()
    app = ForgetfulinoApp(start_watching=start_watching, minimize_to_tray=minimize_to_tray)
    app.mainloop()


if __name__ == "__main__":
    main()
