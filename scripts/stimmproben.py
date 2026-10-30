#!/usr/bin/env python3
"""
Zweck:   Erzeugt Hörproben deutscher Azure-Stimmen (ein Satz, mehrere Tempi pro Stimme) und eine
         Webseite zum Probehören mit großen Knöpfen, damit der Patient die passende Stimme wählen
         kann. Frauen- und Männerstimmen stehen in eigenen Gruppen; die Stimmen sind durchgehend
         nummeriert („Stimme 1“ …), damit man sie leicht benennen kann.
         Die gewählte Stimme gibt man dann an: scripts/erzeuge_audio.py --azure <Stimme>
Aufruf:  python3 scripts/stimmproben.py                      (alle deutschen Stimmen → site/stimmen/)
         python3 scripts/stimmproben.py --satz "Guten Morgen!" --tempi 0.5 0.8 1.0
         python3 scripts/stimmproben.py --stimmen de-DE-KatjaNeural de-DE-ConradNeural --ziel /tmp/proben
         python3 scripts/stimmproben.py --nur-seite               (nur HTML neu, vorhandene MP3s nutzen)
         python3 scripts/stimmproben.py --liste                   (deutsche Stimmen nur auflisten)
         (im Wurzelverzeichnis des Repos wortwaerts ausführen; braucht AZURE_SPEECH_KEY und
         AZURE_SPEECH_REGION als Umgebungsvariablen)
Pakete:  Python 3 (Standardbibliothek), ffmpeg (System)
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import urllib.request
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from erzeuge_audio import PROJEKT, azure_synthese, zu_mp3  # noqa: E402

SATZ = "Ich hätte gern einen Kaffee mit Milch, bitte."
TEMPI = [0.5, 0.8]


def deutsche_stimmen():
    key, region = os.environ["AZURE_SPEECH_KEY"], os.environ["AZURE_SPEECH_REGION"]
    anfrage = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list",
        headers={"Ocp-Apim-Subscription-Key": key})
    with urllib.request.urlopen(anfrage, timeout=30) as antwort:
        return [v for v in json.load(antwort) if v["Locale"] == "de-DE"]


def anzeigename(kurzname):
    return kurzname.split("-")[2].replace("MultilingualNeural", "").replace("Neural", "")


def tempo_text(t):
    return f"{t:.1f}".replace(".", ",") + "×"


GRUPPEN = [("Female", "Frauenstimmen"), ("Male", "Männerstimmen")]


def seite(satz, tempi, stimmen):
    # Frauen zuerst, dann Männer (Unbekanntes zuletzt); Nummern laufen durch
    reihenfolge = {g: i for i, (g, _) in enumerate(GRUPPEN)}
    stimmen = sorted(stimmen, key=lambda s: reihenfolge.get(s[1], len(GRUPPEN)))
    titel = dict(GRUPPEN)
    abschnitte = []
    for n, (kurz, geschlecht) in enumerate(stimmen, 1):
        if n == 1 or geschlecht != stimmen[n - 2][1]:
            karten = []
            abschnitte.append((titel.get(geschlecht, "Weitere Stimmen"), karten))
        knoepfe = "".join(
            f'<button type="button" data-src="audio/{kurz}-{t:.1f}.mp3">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>'
            f'<span>Tempo {tempo_text(t)}</span></button>' for t in tempi)
        karten.append(
            f'<li><div class="kopf"><span class="nr">Stimme {n}</span>'
            f'<span class="name">{escape(anzeigename(kurz))}</span></div>'
            f'<div class="knoepfe">{knoepfe}</div></li>')
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Stimmen probehören</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Literata:opsz,wght@7..72,400;7..72,500&display=swap">
<style>
  :root {{
    --bg: #eef1f4; --surface: #ffffff; --ink: #17202b; --muted: #5d6877; --line: #d6dce3;
    --accent: #1f5f8b; --accent-ink: #ffffff; --mark: #f2c14e; --mark-soft: #fbf0d2;
    --font-display: "Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
    --font-body: "Literata", Georgia, "Times New Roman", serif;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #11161d; --surface: #19212b; --ink: #e8edf2; --muted: #98a4b3; --line: #2a3542;
      --accent: #6fb0e0; --accent-ink: #0d1620; --mark: #e2b443; --mark-soft: #2c2716;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #11161d; --surface: #19212b; --ink: #e8edf2; --muted: #98a4b3; --line: #2a3542;
    --accent: #6fb0e0; --accent-ink: #0d1620; --mark: #e2b443; --mark-soft: #2c2716;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font-body); }}
  .wrap {{ max-width: 760px; margin: 0 auto; padding: 32px 16px 64px; }}
  h1 {{ font-family: var(--font-display); font-weight: 800; font-size: clamp(28px, 6vw, 40px); margin: 0 0 12px; }}
  p {{ font-size: 19px; line-height: 1.5; margin: 0 0 12px; color: var(--muted); }}
  .satz {{ font-size: clamp(22px, 5vw, 28px); color: var(--ink); background: var(--surface);
          border: 1px solid var(--line); border-radius: 14px; padding: 16px 20px; margin: 20px 0 28px; }}
  ol {{ list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }}
  li {{ background: var(--surface); border: 2px solid var(--line); border-radius: 14px; padding: 16px 20px;
        display: flex; flex-wrap: wrap; gap: 12px 20px; align-items: center; justify-content: space-between; }}
  li.aktiv {{ border-color: var(--mark); background: var(--mark-soft); }}
  .kopf {{ display: grid; gap: 2px; }}
  h2 {{ font-family: var(--font-display); font-weight: 800; font-size: 24px; margin: 32px 0 12px; }}
  .nr {{ font-family: var(--font-display); font-weight: 800; font-size: 26px; }}
  .name {{ font-size: 16px; color: var(--muted); }}
  .knoepfe {{ display: flex; flex-wrap: wrap; gap: 10px; }}
  button {{ font: 600 18px var(--font-display); display: inline-flex; align-items: center; gap: 10px;
           min-height: 56px; padding: 0 22px; border-radius: 999px; border: 0; cursor: pointer;
           background: var(--accent); color: var(--accent-ink); }}
  button svg {{ width: 20px; height: 20px; fill: currentColor; }}
  button:focus-visible {{ outline: 3px solid var(--mark); outline-offset: 3px; }}
  button.spielt {{ background: var(--mark); color: #17202b; }}
  a {{ color: var(--accent); }}
  .fuss {{ margin-top: 32px; font-size: 15px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Welche Stimme gefällt Ihnen?</h1>
  <p>Alle Stimmen sprechen denselben Satz. Tippen Sie auf einen Knopf, um ihn zu hören.
     Merken Sie sich die Nummer der Stimme, die Sie am besten verstehen.</p>
  <div class="satz">„{escape(satz)}“</div>
  <noscript><p>Zum Abspielen wird JavaScript benötigt.</p></noscript>
  {''.join(f"<section><h2>{t}</h2><ol>{''.join(k)}</ol></section>" for t, k in abschnitte)}
  <p class="fuss"><a href="../">Zurück zu Wortwärts</a></p>
</div>
<script>
  const audio = new Audio();
  let aktiv = null;
  function zuruecksetzen() {{
    if (!aktiv) return;
    aktiv.classList.remove("spielt");
    aktiv.closest("li").classList.remove("aktiv");
    aktiv = null;
  }}
  audio.addEventListener("ended", zuruecksetzen);
  document.querySelectorAll("button[data-src]").forEach(b => b.addEventListener("click", () => {{
    const gleicher = aktiv === b && !audio.paused;
    audio.pause();
    zuruecksetzen();
    if (gleicher) return;   // zweiter Klick auf denselben Knopf stoppt
    aktiv = b;
    b.classList.add("spielt");
    b.closest("li").classList.add("aktiv");
    audio.src = b.dataset.src;
    audio.play().catch(zuruecksetzen);
  }}));
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--satz", default=SATZ)
    ap.add_argument("--tempi", nargs="+", type=float, default=TEMPI)
    ap.add_argument("--stimmen", nargs="+", help="Kurznamen; ohne Angabe alle deutschen Stimmen")
    ap.add_argument("--ziel", type=Path, default=PROJEKT / "site" / "stimmen")
    ap.add_argument("--nur-seite", action="store_true", help="keine Synthese, nur index.html neu bauen")
    ap.add_argument("--liste", action="store_true", help="deutsche Stimmen nur auflisten")
    a = ap.parse_args()

    alle = deutsche_stimmen()
    if a.liste:
        for v in alle:
            print(f'{v["ShortName"]:40} {v["Gender"]}')
        return
    geschlecht = {v["ShortName"]: v["Gender"] for v in alle}
    stimmen = [(s, geschlecht.get(s, "")) for s in (a.stimmen or [v["ShortName"] for v in alle])]

    audio_dir = a.ziel / "audio"
    if a.nur_seite:
        fehlend = [f"{k}-{t:.1f}.mp3" for k, _ in stimmen for t in a.tempi
                   if not (audio_dir / f"{k}-{t:.1f}.mp3").exists()]
        if fehlend:
            sys.exit("Fehlende MP3s: " + ", ".join(fehlend))
        (a.ziel / "index.html").write_text(seite(a.satz, a.tempi, stimmen), encoding="utf-8")
        print(a.ziel / "index.html")
        return
    shutil.rmtree(audio_dir, ignore_errors=True)
    audio_dir.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as t:
        wav = Path(t) / "x.wav"
        for kurz, _ in stimmen:
            for tempo in a.tempi:
                azure_synthese(kurz, a.satz, wav, tempo)
                zu_mp3(wav, audio_dir / f"{kurz}-{tempo:.1f}.mp3")
            print(kurz)
    (a.ziel / "index.html").write_text(seite(a.satz, a.tempi, stimmen), encoding="utf-8")
    print(a.ziel / "index.html")


if __name__ == "__main__":
    main()
