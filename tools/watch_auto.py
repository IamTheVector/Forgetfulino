#!/usr/bin/env python3
"""
Forgetfulino Auto-Watcher
Monitora le cartelle sketch e genera automaticamente i file .h
"""

import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class SketchWatcher(FileSystemEventHandler):
    def __init__(self, base_path, generator_path):
        self.base_path = base_path
        self.generator_path = generator_path
        print(f"Monitoraggio: {base_path}")
        
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.ino'):
            sketch_folder = os.path.dirname(event.src_path)
            sketch_name = os.path.basename(event.src_path)
            print(f"\nModificato: {sketch_name}")
            try:
                subprocess.run([sys.executable, self.generator_path, sketch_folder], check=True)
                print(f"Generato: {sketch_name}")
            except Exception as e:
                print(f"Errore: {e}")

def main():
    # Se passato un parametro, usalo come percorso base
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        # Altrimenti cerca automaticamente
        home = os.path.expanduser("~")
        possible_paths = [
            os.path.join(home, "Dropbox", "Arduino"),
            os.path.join(home, "Documents", "Arduino"),
            os.path.join(home, "Arduino")
        ]
        base_path = None
        for p in possible_paths:
            if os.path.exists(p):
                base_path = p
                break
    
    if not base_path or not os.path.exists(base_path):
        print("ERRORE: Non trovo la cartella sketch!")
        print("Specifica il percorso: python watch_auto.py C:\\percorso\\cartella\\sketch")
        sys.exit(1)
    
    generator_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "forgetfulino_generator.py"
    )
    
    print("\nFORGETFULINO AUTO-WATCHER")
    print("=========================")
    print(f"Sketch folder: {base_path}")
    print(f"Generator: {generator_path}")
    print("\nMonitoraggio in corso... (Ctrl+C per fermare)")
    
    handler = SketchWatcher(base_path, generator_path)
    observer = Observer()
    observer.schedule(handler, base_path, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nMonitoraggio fermato.")
    observer.join()

if __name__ == "__main__":
    main()