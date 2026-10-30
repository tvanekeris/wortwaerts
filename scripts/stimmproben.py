#!/usr/bin/env python3
"""
Zweck:   Erzeugt Hörproben mehrerer deutscher Azure-Stimmen (dieselben Beispielsätze für jede
         Stimme) und eine HTML-Seite mit eingebetteten MP3s zum Vergleichen und Auswählen.
         Die gewählte Stimme gibt man dann an: scripts/erzeuge_audio.py --azure <Stimme>
Aufruf:  python3 scripts/stimmproben.py --ziel <ordner>                  (Standardauswahl Stimmen)
         python3 scripts/stimmproben.py --ziel <ordner> --stimmen de-DE-KatjaNeural de-DE-ConradNeural
         python3 scripts/stimmproben.py --liste                          (alle deutschen Stimmen)
         (im Wurzelverzeichnis des Repos wortwaerts ausführen; braucht AZURE_SPEECH_KEY und
         AZURE_SPEECH_REGION als Umgebungsvariablen)
Pakete:  Python 3 (Standardbibliothek), ffmpeg (System)
"""
import argparse
import base64
import json
import os
import sys
import tempfile
import urllib.request
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from erzeuge_audio import azure_synthese, zu_mp3  # noqa: E402

STIMMEN = ["de-DE-KatjaNeural", "de-DE-ConradNeural", "de-DE-SeraphinaMultilingualNeural",
           "de-DE-FlorianMultilingualNeural", "de-DE-AmalaNeural", "de-DE-KillianNeural"]
SAETZE = ["Darf ich mich vorstellen? Ich heiße Anna.",
          "Ich hätte gern einen Kaffee mit Milch, bitte.",
          "Können wir das Meeting auf morgen verschieben?",
          "Bis später, mach's gut!",
          "Es ist Viertel nach drei."]


def liste():
    key, region = os.environ["AZURE_SPEECH_KEY"], os.environ["AZURE_SPEECH_REGION"]
    anfrage = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list",
        headers={"Ocp-Apim-Subscription-Key": key})
    with urllib.request.urlopen(anfrage, timeout=30) as antwort:
        for v in json.load(antwort):
            if v["Locale"] == "de-DE":
                print(f'{v["ShortName"]:40} {v["Gender"]}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ziel", type=Path)
    ap.add_argument("--stimmen", nargs="+", default=STIMMEN)
    ap.add_argument("--liste", action="store_true", help="deutsche Stimmen auflisten")
    a = ap.parse_args()
    if a.liste:
        return liste()
    if not a.ziel:
        ap.error("--ziel ist nötig")
    a.ziel.mkdir(parents=True, exist_ok=True)

    zeilen = []
    with tempfile.TemporaryDirectory() as t:
        for stimme in a.stimmen:
            name = stimme.split("-")[2].replace("MultilingualNeural", " (mehrsprachig)").replace("Neural", "")
            zellen = []
            for j, satz in enumerate(SAETZE, 1):
                wav, mp3 = Path(t) / "x.wav", a.ziel / f"{stimme}-{j}.mp3"
                azure_synthese(stimme, satz, wav)
                zu_mp3(wav, mp3)
                b64 = base64.b64encode(mp3.read_bytes()).decode()
                zellen.append(f'<td><audio controls preload="none" src="data:audio/mpeg;base64,{b64}"></audio></td>')
            zeilen.append(f"<tr><th>{escape(name)}<br><code>{stimme}</code></th>{''.join(zellen)}</tr>")
            print(stimme)

    kopf = "".join(f"<th>{escape(s)}</th>" for s in SAETZE)
    (a.ziel / "stimmproben.html").write_text(f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Stimmproben</title>
<style>
  body {{ font: 16px/1.4 system-ui, sans-serif; margin: 16px; background: #fff; color: #222; }}
  table {{ border-collapse: collapse; }} th, td {{ border: 1px solid #ccc; padding: 8px; vertical-align: top; }}
  thead th {{ font-weight: 500; font-size: 14px; max-width: 220px; }} tbody th {{ text-align: left; white-space: nowrap; }}
  code {{ font-size: 12px; color: #666; }} audio {{ width: 200px; }} .scroll {{ overflow-x: auto; }}
</style></head><body>
<h1>Stimmproben (Microsoft Azure)</h1>
<p>Jede Zeile ist eine Stimme, jede Spalte ein Beispielsatz.</p>
<div class="scroll"><table><thead><tr><th>Stimme</th>{kopf}</tr></thead>
<tbody>{''.join(zeilen)}</tbody></table></div>
</body></html>
""", encoding="utf-8")
    print(a.ziel / "stimmproben.html")


if __name__ == "__main__":
    main()
