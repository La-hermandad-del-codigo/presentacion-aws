#!/usr/bin/env python3
"""
Compilador modular para las presentaciones Reveal.js de AWS / APM Inversiones EIRL.
Combina template.html + slides/*.html -> presentacion.html (Fase 1)
Combina template.html + slides-fase2/*.html -> presentacion2.html (Fase 2)
"""

import os
import sys
import glob
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, "template.html")

CONFIGS = {
    1: {
        "slides_dir": os.path.join(BASE_DIR, "slides"),
        "output_file": os.path.join(BASE_DIR, "presentacion.html"),
        "title": "Propuesta Cloud AWS | APM Inversiones EIRL - Etapa 1",
    },
    2: {
        "slides_dir": os.path.join(BASE_DIR, "slides-fase2"),
        "output_file": os.path.join(BASE_DIR, "presentacion2.html"),
        "title": "Propuesta Cloud AWS | APM Inversiones EIRL - Etapa 2 (Servicios Core & Datos)",
    },
}

def build_fase(fase=1):
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Error: No se encontró {TEMPLATE_FILE}")
        return False

    cfg = CONFIGS.get(fase)
    if not cfg:
        print(f"Error: Fase {fase} no válida (disponibles: 1, 2)")
        return False

    slides_dir = cfg["slides_dir"]
    output_file = cfg["output_file"]

    if not os.path.exists(slides_dir):
        print(f"Advertencia: Directorio de diapositivas no encontrado: {slides_dir}")
        return False

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = f.read()

    # Reemplazar título de pestaña según la fase
    if "<title>" in template:
        import re
        template = re.sub(r"<title>.*?</title>", f"<title>{cfg['title']}</title>", template)

    slide_files = sorted(glob.glob(os.path.join(slides_dir, "*.html")))
    if not slide_files:
        print(f"Advertencia: No se encontraron diapositivas en {slides_dir}")
        return False

    slides_content = []
    for sf in slide_files:
        basename = os.path.basename(sf)
        with open(sf, "r", encoding="utf-8") as f:
            content = f.read().strip()
            slides_content.append(f"      <!-- Slide: {basename} -->\n      {content}")

    all_slides = "\n\n".join(slides_content)
    output = template.replace("<!-- {{SLIDES}} -->", all_slides)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"✓ [Fase {fase}] Compiladas {len(slide_files)} diapositivas en {os.path.basename(output_file)} ({os.path.getsize(output_file)} bytes)")
    return True

def build_all():
    success = True
    for f in (1, 2):
        if os.path.exists(CONFIGS[f]["slides_dir"]):
            if not build_fase(f):
                success = False
    return success

def watch(fase=2):
    cfg = CONFIGS.get(fase, CONFIGS[2])
    slides_dir = cfg["slides_dir"]
    print(f"Iniciando modo observador para Fase {fase} (--watch). Presiona Ctrl+C para salir...")
    build_fase(fase)

    last_mtimes = {}
    def get_mtimes():
        mtimes = {}
        if os.path.exists(TEMPLATE_FILE):
            mtimes[TEMPLATE_FILE] = os.path.getmtime(TEMPLATE_FILE)
        for sf in glob.glob(os.path.join(slides_dir, "*.html")):
            mtimes[sf] = os.path.getmtime(sf)
        return mtimes

    last_mtimes = get_mtimes()
    try:
        while True:
            time.sleep(0.5)
            current_mtimes = get_mtimes()
            if current_mtimes != last_mtimes:
                print(f"\n[Cambio detectado en Fase {fase}] Recompilando...")
                build_fase(fase)
                last_mtimes = current_mtimes
    except KeyboardInterrupt:
        print("\nObservador detenido.")

def serve(port=8000, fase=2):
    import http.server
    import socketserver
    import threading

    cfg = CONFIGS.get(fase, CONFIGS[2])
    slides_dir = cfg["slides_dir"]
    output_filename = os.path.basename(cfg["output_file"])

    build_all()

    def watcher_thread():
        last_mtimes = {}
        for sf in glob.glob(os.path.join(slides_dir, "*.html")):
            last_mtimes[sf] = os.path.getmtime(sf)
        if os.path.exists(TEMPLATE_FILE):
            last_mtimes[TEMPLATE_FILE] = os.path.getmtime(TEMPLATE_FILE)
        while True:
            time.sleep(0.5)
            current_mtimes = {}
            for sf in glob.glob(os.path.join(slides_dir, "*.html")):
                current_mtimes[sf] = os.path.getmtime(sf)
            if os.path.exists(TEMPLATE_FILE):
                current_mtimes[TEMPLATE_FILE] = os.path.getmtime(TEMPLATE_FILE)
            if current_mtimes != last_mtimes:
                print(f"\n[Cambio detectado en Fase {fase}] Recompilando...")
                build_fase(fase)
                last_mtimes = current_mtimes

    t = threading.Thread(target=watcher_thread, daemon=True)
    t.start()

    os.chdir(BASE_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n🚀 Servidor web activo:")
        print(f"   - Fase 1: http://localhost:{port}/presentacion.html")
        print(f"   - Fase 2: http://localhost:{port}/{output_filename}")
        print("Presiona Ctrl+C para detener.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")

if __name__ == "__main__":
    target_fase = None
    if "1" in sys.argv:
        target_fase = 1
    elif "2" in sys.argv:
        target_fase = 2

    if "--watch" in sys.argv or "-w" in sys.argv:
        watch(fase=target_fase or 2)
    elif "--serve" in sys.argv or "-s" in sys.argv:
        port = 8000
        for arg in sys.argv:
            if arg.isdigit() and int(arg) > 100:
                port = int(arg)
        serve(port=port, fase=target_fase or 2)
    elif target_fase:
        build_fase(target_fase)
    else:
        build_all()
