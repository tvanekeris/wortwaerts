#!/usr/bin/env python3
"""Prüft, ob die Wortwärts-Seite ihre Satzliste aufbaut und ohne JavaScript einen Hinweis zeigt.

Zweck:
    1. Mit JavaScript: Chromium (headless) lädt die Seite, führt das Skript aus und gibt
       das fertige DOM aus. Darin müssen so viele Sätze (<li>) stehen wie in saetze.json.
    2. Ohne JavaScript: Das ausgelieferte HTML muss den <noscript>-Hinweis enthalten
       (genau diesen Text zeigt der Browser dann an Stelle der Satzliste).

Aufruf:
    python3 scripts/test_seite.py                 # startet selbst einen Webserver für site/
    python3 scripts/test_seite.py https://tvanekeris.github.io/wortwaerts/   # Live-Seite
    Chromium-Pfad ändern: CHROMIUM=/pfad/zu/chrome python3 scripts/test_seite.py

Benötigt:
    Python 3 (nur Standardbibliothek) und einen Chromium/Chrome-Browser
    (Standard: /opt/pw-browsers/chromium, sonst "chromium" bzw. "google-chrome" im PATH).
    Kein Node.js.
"""
import functools
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
HINWEIS = "braucht JavaScript"


def finde_chromium():
    for kandidat in (os.environ.get("CHROMIUM"), "/opt/pw-browsers/chromium",
                     shutil.which("chromium"), shutil.which("google-chrome")):
        if kandidat and Path(kandidat).exists():
            return kandidat
    sys.exit("Kein Chromium gefunden (Umgebungsvariable CHROMIUM setzen).")


class StillerHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def starte_server():
    handler = functools.partial(StillerHandler, directory=WURZEL / "site")
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}/"


def main():
    server = None
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        server, url = starte_server()

    erwartet = sum(len(s) for s in json.loads((WURZEL / "saetze.json").read_text("utf-8")).values())
    ok = True

    # 1. Mit JavaScript: fertiges DOM aus Chromium
    dom = subprocess.run(
        [finde_chromium(), "--headless", "--no-sandbox", "--disable-gpu",
         "--virtual-time-budget=3000", "--dump-dom", url],
        capture_output=True, text=True, timeout=60).stdout
    anzahl = len(re.findall(r"<li\b", dom))
    print(f"mit JavaScript:  {anzahl} von {erwartet} Sätzen angezeigt")
    ok &= anzahl == erwartet

    # 2. Ohne JavaScript: Hinweis im <noscript> des ausgelieferten HTML
    html = urllib.request.urlopen(url, timeout=30).read().decode("utf-8")
    noscript = re.search(r"<noscript>(.*?)</noscript>", html, re.S)
    hinweis = bool(noscript and HINWEIS in noscript.group(1))
    print(f"ohne JavaScript: Hinweis vorhanden = {hinweis}")
    ok &= hinweis

    if server:
        server.shutdown()
    print("OK" if ok else "FEHLER")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
