#!/usr/bin/env python3
"""
Compilador modular para la presentación Reveal.js de AWS / RPsoft.
Combina template.html + slides/*.html -> presentacion.html
"""

import os
import sys
import glob
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SLIDES_DIR = os.path.join(BASE_DIR, "slides")
TEMPLATE_FILE = os.path.join(BASE_DIR, "template.html")
OUTPUT_FILE = os.path.join(BASE_DIR, "presentacion.html")

def build():
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Error: No se encontró {TEMPLATE_FILE}")
        return False

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    # Obtener todas las diapositivas ordenadas
    slide_files = sorted(glob.glob(os.path.join(SLIDES_DIR, "*.html")))
    if not slide_files:
        print(f"Advertencia: No se encontraron diapositivas en {SLIDES_DIR}")
        return False

    slides_content = []
    for sf in slide_files:
        basename = os.path.basename(sf)
        with open(sf, "r", encoding="utf-8") as f:
            content = f.read().strip()
            slides_content.append(f"      <!-- Slide: {basename} -->\n      {content}")

    all_slides = "\n\n".join(slides_content)
    output = template.replace("<!-- {{SLIDES}} -->", all_slides)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"✓ Compiladas {len(slide_files)} diapositivas en {os.path.basename(OUTPUT_FILE)} ({os.path.getsize(OUTPUT_FILE)} bytes)")
    return True

def watch():
    print("Iniciando modo observador (--watch). Presiona Ctrl+C para salir...")
    build()
    
    last_mtimes = {}
    def get_mtimes():
        mtimes = {}
        if os.path.exists(TEMPLATE_FILE):
            mtimes[TEMPLATE_FILE] = os.path.getmtime(TEMPLATE_FILE)
        for sf in glob.glob(os.path.join(SLIDES_DIR, "*.html")):
            mtimes[sf] = os.path.getmtime(sf)
        return mtimes

    last_mtimes = get_mtimes()
    try:
        while True:
            time.sleep(0.5)
            current_mtimes = get_mtimes()
            if current_mtimes != last_mtimes:
                print("\n[Cambio detectado] Recompilando...")
                build()
                last_mtimes = current_mtimes
    except KeyboardInterrupt:
        print("\nObservador detenido.")

def serve(port=8000):
    import http.server
    import socketserver
    import threading

    build()
    
    # Iniciar observador en hilo secundario
    def watcher_thread():
        last_mtimes = {}
        for sf in glob.glob(os.path.join(SLIDES_DIR, "*.html")):
            last_mtimes[sf] = os.path.getmtime(sf)
        if os.path.exists(TEMPLATE_FILE):
            last_mtimes[TEMPLATE_FILE] = os.path.getmtime(TEMPLATE_FILE)
        while True:
            time.sleep(0.5)
            current_mtimes = {}
            for sf in glob.glob(os.path.join(SLIDES_DIR, "*.html")):
                current_mtimes[sf] = os.path.getmtime(sf)
            if os.path.exists(TEMPLATE_FILE):
                current_mtimes[TEMPLATE_FILE] = os.path.getmtime(TEMPLATE_FILE)
            if current_mtimes != last_mtimes:
                print("\n[Cambio detectado] Recompilando...")
                build()
                last_mtimes = current_mtimes

    t = threading.Thread(target=watcher_thread, daemon=True)
    t.start()

    os.chdir(BASE_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n🚀 Servidor web activo en http://localhost:{port}/presentacion.html")
        print("Presiona Ctrl+C para detener.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")

if __name__ == "__main__":
    if "--watch" in sys.argv or "-w" in sys.argv:
        watch()
    elif "--serve" in sys.argv or "-s" in sys.argv:
        port = 8000
        for arg in sys.argv:
            if arg.isdigit():
                port = int(arg)
        serve(port)
    else:
        build()
