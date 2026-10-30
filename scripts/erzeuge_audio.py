#!/usr/bin/env python3
"""
Zweck:   Erzeugt aus saetze.json ({Thema: [Sätze]}) MP3-Dateien für jeden Satz plus eine
         Gesamtdatei – wahlweise mit Microsoft Azure AI Speech (neuronale Stimmen, online) oder
         der Offline-Sprachsynthese Piper – und baut daraus zwei Varianten des Players:
           - site/index.html        Webseite, lädt die MP3s aus site/audio/
           - alltagssaetze.html     Artifact-Version, MP3s als data:-URIs eingebettet
Aufruf:  python3 scripts/erzeuge_audio.py --azure de-DE-KatjaNeural
           (braucht die Umgebungsvariablen AZURE_SPEECH_KEY und AZURE_SPEECH_REGION)
         python3 scripts/erzeuge_audio.py --piper <pfad/zu/piper> --modell <pfad/zu/de-thorsten-low.onnx>
         python3 scripts/erzeuge_audio.py --nur-seiten   (nur HTML neu bauen, vorhandene MP3s nutzen)
         (im Wurzelverzeichnis des Repos wortwaerts ausführen)
Pakete:  ffmpeg (System); für Azure nur die Python-Standardbibliothek;
         für Piper: piper-tts (pip), Stimme voice-de-thorsten-low.tar.gz
         – Details und Versionen in docs/werkzeuge.md
"""
import argparse
import base64
import json
import os
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

PROJEKT = Path(__file__).resolve().parent.parent
PAUSE_SEK = 0.8  # Stille zwischen den Sätzen in der Gesamtdatei


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def synthese(piper, modell, text, wav):
    run([piper, "--model", str(modell), "--output_file", str(wav)],
        input=text.encode("utf-8"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def azure_synthese(stimme, text, wav, tempo=1.0):
    """Spricht text mit einer Azure-Stimme (z. B. de-DE-KatjaNeural) als WAV (24 kHz, mono)."""
    key, region = os.environ["AZURE_SPEECH_KEY"], os.environ["AZURE_SPEECH_REGION"]
    ssml = (f'<speak version="1.0" xml:lang="de-DE"><voice name="{stimme}">'
            f'<prosody rate="{tempo:.2f}">{escape(text)}</prosody></voice></speak>')
    anfrage = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={"Ocp-Apim-Subscription-Key": key,
                 "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
                 "User-Agent": "wortwaerts"})
    for versuch in range(5):
        try:
            with urllib.request.urlopen(anfrage, timeout=60) as antwort:
                Path(wav).write_bytes(antwort.read())
            return
        except urllib.error.HTTPError as e:
            # 429: Gratis-Tarif F0 erlaubt nur wenige Anfragen gleichzeitig/pro Minute
            if e.code != 429 or versuch == 4:
                raise
            time.sleep(2 ** versuch)


def zu_mp3(wav, mp3):
    # Mono, 64 kbit/s, 24 kHz: klar genug für Sprache, Artifact-Datei bleibt klein
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
         "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "24000", "-ac", "1",
         "-codec:a", "libmp3lame", "-b:a", "64k", str(mp3)])


def gesamtdatei(wavs, ziel, tmp):
    stille = tmp / "stille.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
         "anullsrc=r=24000:cl=mono", "-t", str(PAUSE_SEK), str(stille)])
    liste = tmp / "liste.txt"
    teile = []
    for w in wavs:
        teile += [w, stille]
    liste.write_text("".join(f"file '{p}'\n" for p in teile))
    roh = tmp / "gesamt.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(liste), "-ar", "24000", "-ac", "1", str(roh)])
    zu_mp3(roh, ziel)


def seite(vorlage, daten, fusszeile, stimme):
    html = vorlage.replace("/*__DATEN__*/", json.dumps(daten, ensure_ascii=False))
    html = html.replace("/*__STIMME__*/", stimme)
    html = html.replace("/*__ANZAHL__*/", str(len(daten)))
    html = html.replace("/*__THEMEN__*/", str(len({d["thema"] for d in daten})))
    return html.replace("/*__FUSSZEILE__*/", fusszeile)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--azure", metavar="STIMME",
                    help="Azure-Stimme, z. B. de-DE-KatjaNeural (Liste: scripts/stimmproben.py --liste)")
    ap.add_argument("--piper")
    ap.add_argument("--modell", type=Path)
    ap.add_argument("--nur-seiten", action="store_true",
                    help="keine Sprachsynthese, nur die HTML-Seiten aus vorhandenen MP3s bauen")
    a = ap.parse_args()
    if not a.nur_seiten and not a.azure and not (a.piper and a.modell):
        ap.error("--azure STIMME oder --piper und --modell sind nötig (oder --nur-seiten)")

    themen = json.loads((PROJEKT / "saetze.json").read_text(encoding="utf-8"))
    saetze = [(thema, de) for thema, liste in themen.items() for de in liste]
    audio_dir = PROJEKT / "site" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    vorlage = (PROJEKT / "vorlage" / "seite.html").read_text(encoding="utf-8")

    if not a.nur_seiten:
        for alt in audio_dir.glob("*.mp3"):
            alt.unlink()
        with tempfile.TemporaryDirectory() as t:
            tmp = Path(t)
            wavs = []
            for i, (_thema, de) in enumerate(saetze, 1):
                wav = tmp / f"{i:03d}.wav"
                if a.azure:
                    azure_synthese(a.azure, de, wav)
                else:
                    synthese(a.piper, a.modell, de, wav)
                zu_mp3(wav, audio_dir / f"{i:03d}.mp3")
                wavs.append(wav)
                print(f"{i:03d}.mp3  {de}")
            gesamtdatei(wavs, audio_dir / "alle-saetze.mp3", tmp)
            print("alle-saetze.mp3")
        stimme = (f"{a.azure.split('-')[2].replace('MultilingualNeural', '').replace('Neural', '')}"
                  " (Microsoft Azure, Deutsch)") if a.azure else "Thorsten (Piper, Deutsch)"
        (audio_dir / "stimme.txt").write_text(stimme + "\n", encoding="utf-8")
    stimme_datei = audio_dir / "stimme.txt"
    stimme = (stimme_datei.read_text(encoding="utf-8").strip() if stimme_datei.exists()
              else "Thorsten (Piper, Deutsch)")

    # Webseite: relative Pfade, funktioniert lokal (Doppelklick) und auf jedem Webserver
    web = [{"thema": t, "de": de, "src": f"audio/{i:03d}.mp3"} for i, (t, de) in enumerate(saetze, 1)]
    kopf = ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="description" content="Wortwärts: deutsche Alltagssätze zum Hören und '
            'Nachsprechen, mit einstellbarem Tempo – zum Üben bei Aphasie.">\n'
            '<style>body{margin:0}[hidden]{display:none!important}</style>\n')
    inhalt = seite(vorlage, web, '<a href="audio/alle-saetze.mp3" style="color:inherit">Alle Sätze als MP3</a>',
                   stimme)
    inhalt = inhalt.replace("<div class=\"wrap\">", "</head>\n<body>\n<div class=\"wrap\">", 1)
    (PROJEKT / "site" / "index.html").write_text(kopf + inhalt + "</body>\n</html>\n", encoding="utf-8")

    # Artifact: MP3s als data:-URIs, damit keine externen Dateien nötig sind
    art = []
    for i, (t, de) in enumerate(saetze, 1):
        b64 = base64.b64encode((audio_dir / f"{i:03d}.mp3").read_bytes()).decode()
        art.append({"thema": t, "de": de, "src": "data:audio/mpeg;base64," + b64})
    (PROJEKT / "alltagssaetze.html").write_text(
        seite(vorlage, art, "Audio eingebettet, offline abspielbar", stimme), encoding="utf-8")
    print("site/index.html und alltagssaetze.html geschrieben")


if __name__ == "__main__":
    main()
