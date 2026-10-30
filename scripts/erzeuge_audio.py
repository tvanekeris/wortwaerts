#!/usr/bin/env python3
"""
Zweck:   Erzeugt aus saetze.json (lange Sätze) und saetze_kurz.json (kurze Sätze, 3–4 Wörter),
         beide im Format {Thema: [Sätze]}, mit Microsoft Azure AI Speech für jeden Satz
         MP3-Dateien in zwei Stimmen (Frau/Mann, festgelegt in stimmen.json) und drei Tempi
         (0,5 / 0,7 / 1,0 – das Tempo erzeugt Azure direkt, per SSML <prosody rate>) und baut aus
         vorlage/seite.html die Webseite site/index.html. Außerdem schreibt es eine Übersicht,
         welche MP3 zu welchem Satz gehört: site/audio/README.md (Tabelle je Thema mit Links)
         und site/audio/uebersicht.csv (jede Datei eine Zeile, für Tabellenprogramme).
         Ablage: site/audio/<Thema>/<kurz|lang>/<frau|mann>/<0.5|0.7|1.0>/<Nr>.mp3, z. B.
                 site/audio/02-essen-trinken/kurz/frau/0.5/k011.mp3
                 (Themen-Ordner mit laufender Nummer; lange Sätze 001 …, kurze Sätze k001 …)
         Vorhandene Dateien werden nur neu erzeugt, wenn sich Stimme, Tempo oder Satztext geändert
         haben (Buchführung in site/audio/manifest.json) – das spart Azure-Kontingent. Ändert sich
         nur der Ablageort (z. B. Thema umbenannt), wird die vorhandene Datei verschoben.
Aufruf:  python3 scripts/erzeuge_audio.py               (fehlende/geänderte MP3s + Seite)
         python3 scripts/erzeuge_audio.py --neu         (alle MP3s neu erzeugen)
         python3 scripts/erzeuge_audio.py --nur-seiten  (nur site/index.html und Übersicht neu bauen)
         (im Wurzelverzeichnis des Repos wortwaerts ausführen; braucht die Umgebungsvariablen
         AZURE_SPEECH_KEY und AZURE_SPEECH_REGION)
Pakete:  Python 3 (nur Standardbibliothek), ffmpeg (System) – Details in docs/werkzeuge.md
"""
import argparse
import csv
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
TEMPI = ["0.5", "0.7", "1.0"]
GESCHLECHTER = ["frau", "mann"]


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def azure_synthese(stimme, text, wav, tempo=1.0):
    """Spricht text mit einer Azure-Stimme (z. B. de-DE-KatjaNeural) als WAV (24 kHz, mono)."""
    key, region = os.environ["AZURE_SPEECH_KEY"], os.environ["AZURE_SPEECH_REGION"]
    ssml = (f'<speak version="1.0" xml:lang="de-DE"><voice name="{stimme}">'
            f'<prosody rate="{float(tempo):.2f}">{escape(text)}</prosody></voice></speak>')
    anfrage = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml.encode("utf-8"),
        headers={"Ocp-Apim-Subscription-Key": key,
                 "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
                 "User-Agent": "wortwaerts"})
    for versuch in range(8):
        try:
            with urllib.request.urlopen(anfrage, timeout=60) as antwort:
                Path(wav).write_bytes(antwort.read())
            return
        except urllib.error.HTTPError as e:
            # 429: Gratis-Tarif F0 erlaubt nur wenige Anfragen pro Minute
            if e.code not in (429, 500, 502, 503) or versuch == 7:
                raise
            warten = e.headers.get("Retry-After")
            time.sleep(float(warten) if warten and warten.isdigit() else min(60, 2 ** versuch))


def zu_mp3(wav, mp3):
    # Mono, 64 kbit/s, 24 kHz: klar genug für Sprache
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
         "-af", "loudnorm=I=-16:TP=-1.5", "-ar", "24000", "-ac", "1",
         "-codec:a", "libmp3lame", "-b:a", "64k", str(mp3)])


def anzeigename(kurzname):
    return kurzname.split("-")[2].replace("MultilingualNeural", "").replace("Neural", "")


def erzeuge_mp3s(saetze, stimmen, audio_dir, neu):
    """saetze: Liste von (nr, text, ordner), z. B. ("k011", "Ich habe Hunger.", "02-essen-trinken/kurz")."""
    manifest_datei = audio_dir / "manifest.json"
    manifest = {} if neu or not manifest_datei.exists() else json.loads(manifest_datei.read_text("utf-8"))
    soll = {}
    for g in GESCHLECHTER:
        for tempo in TEMPI:
            for nr, de, ordner in saetze:
                soll[f"{ordner}/{g}/{tempo}/{nr}.mp3"] = (stimmen[g], tempo, de)

    # Vorhandene Aufnahmen mit gleichem Inhalt (Stimme, Tempo, Text) an einem anderen Ort
    # verschieben statt neu erzeugen
    # (derselbe Text kann mehrfach vorkommen, z. B. als kurzer und als langer Satz)
    vorhanden = {}
    for pfad, w in manifest.items():
        if pfad not in soll and (audio_dir / pfad).exists():
            vorhanden.setdefault(tuple(w), []).append(pfad)
    verschoben = 0
    for pfad, w in soll.items():
        if manifest.get(pfad) == list(w) and (audio_dir / pfad).exists():
            continue
        alt = vorhanden.get(w, []).pop() if vorhanden.get(w) else None
        if alt:
            (audio_dir / pfad).parent.mkdir(parents=True, exist_ok=True)
            os.replace(audio_dir / alt, audio_dir / pfad)
            manifest[pfad] = list(w)
            del manifest[alt]
            verschoben += 1
    if verschoben:
        print(f"{verschoben} MP3s an den neuen Ablageort verschoben")

    # Dateien, die nicht mehr gebraucht werden (z. B. Satz gelöscht), entfernen
    for alt in audio_dir.rglob("*.mp3"):
        if alt.relative_to(audio_dir).as_posix() not in soll:
            alt.unlink()
            manifest.pop(alt.relative_to(audio_dir).as_posix(), None)
    for ordner in sorted((d for d in audio_dir.rglob("*") if d.is_dir()), reverse=True):
        if not any(ordner.iterdir()):
            ordner.rmdir()

    offen = [(pfad, w) for pfad, w in soll.items()
             if manifest.get(pfad) != list(w) or not (audio_dir / pfad).exists()]
    print(f"{len(offen)} von {len(soll)} MP3s zu erzeugen")
    with tempfile.TemporaryDirectory() as t:
        wav = Path(t) / "x.wav"
        for n, (pfad, (stimme, tempo, de)) in enumerate(offen, 1):
            ziel = audio_dir / pfad
            ziel.parent.mkdir(parents=True, exist_ok=True)
            azure_synthese(stimme, de, wav, tempo)
            zu_mp3(wav, ziel)
            manifest[pfad] = [stimme, tempo, de]
            if n % 20 == 0 or n == len(offen):
                # Zwischenstand sichern, damit ein Abbruch nicht alles wiederholt
                manifest_datei.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")
            print(f"[{n}/{len(offen)}] {pfad}  {de}", flush=True)
    manifest_datei.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")


def themen_ordner(index, thema):
    """z. B. (2, "Essen & Trinken") -> "02-essen-trinken" (ohne Umlaute und Sonderzeichen)."""
    name = thema.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        name = name.replace(a, b)
    woerter = "".join(z if z.isascii() and z.isalnum() else " " for z in name).split()
    return f"{index:02d}-" + "-".join(woerter)


def nummeriere(lang, kurz):
    """Liefert {Thema: {"lang": [(nr, text, ordner)], "kurz": [...]}} mit fortlaufenden Nummern;
    ordner ist der Ablageort relativ zu site/audio, z. B. "02-essen-trinken/kurz"."""
    ergebnis = {thema: {"lang": [], "kurz": []} for thema in lang}
    ordner = {thema: themen_ordner(i, thema) for i, thema in enumerate(lang, 1)}
    for laenge, themen, praefix in (("lang", lang, ""), ("kurz", kurz, "k")):
        nr = 0
        for thema, liste in themen.items():
            for de in liste:
                nr += 1
                ergebnis[thema][laenge].append((f"{praefix}{nr:03d}", de, f"{ordner[thema]}/{laenge}"))
    return ergebnis


def baue_seite(nummern, stimmen):
    daten = {
        "themen": [], "tempi": TEMPI,
        "stimmen": {g: anzeigename(stimmen[g]) for g in GESCHLECHTER},
    }
    for thema, laengen in nummern.items():
        daten["themen"].append({"name": thema, **{
            laenge: [{"nr": nr, "de": de, "ordner": ordner} for nr, de, ordner in eintraege]
            for laenge, eintraege in laengen.items()}})
    vorlage = (PROJEKT / "vorlage" / "seite.html").read_text(encoding="utf-8")
    html = vorlage.replace("/*__DATEN__*/", json.dumps(daten, ensure_ascii=False))
    (PROJEKT / "site" / "index.html").write_text(html, encoding="utf-8")


def tempo_text(tempo):
    return tempo.replace(".", ",")


def schreibe_uebersicht(nummern, stimmen, audio_dir):
    """site/audio/README.md (je Thema eine Tabelle) und site/audio/uebersicht.csv (je Datei eine Zeile)."""
    namen = {g: anzeigename(stimmen[g]) for g in GESCHLECHTER}
    anzahl = sum(len(l) for laengen in nummern.values() for l in laengen.values())
    md = [
        "# Übersicht der Aufnahmen",
        "",
        "Automatisch erzeugt von `scripts/erzeuge_audio.py` – bitte nicht von Hand bearbeiten.",
        "",
        f"{anzahl} Sätze × 2 Stimmen × 3 Tempi = {anzahl * 6} MP3-Dateien. Ablage: "
        "`<Thema>/<kurz|lang>/<frau|mann>/<tempo>/<nr>.mp3` – lange Sätze `001` …, kurze Sätze `k001` …",
        "",
        f"- Frau: {namen['frau']} (`{stimmen['frau']}`)",
        f"- Mann: {namen['mann']} (`{stimmen['mann']}`)",
        "- Tempo: 0,5 = langsam, 0,7 = mittel, 1,0 = normal",
        "",
        "Dieselben Angaben je Datei: [uebersicht.csv](uebersicht.csv)",
    ]
    zeilen = []
    for thema, laengen in nummern.items():
        md += ["", f"## {thema}", "", "| Nr | Länge | Satz | Frau | Mann |", "|----|-------|------|------|------|"]
        for laenge in ("kurz", "lang"):
            for nr, de, ordner in laengen[laenge]:
                links = {g: " · ".join(f"[{tempo_text(t)}]({ordner}/{g}/{t}/{nr}.mp3)" for t in TEMPI)
                         for g in GESCHLECHTER}
                md.append(f"| {nr} | {laenge} | {de.replace('|', '\\|')} | {links['frau']} | {links['mann']} |")
                for g in GESCHLECHTER:
                    for t in TEMPI:
                        zeilen.append([f"site/audio/{ordner}/{g}/{t}/{nr}.mp3", thema, laenge, nr, de,
                                       g, stimmen[g], tempo_text(t)])
    (audio_dir / "README.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    # Semikolon und BOM, damit Excel die Datei mit Umlauten direkt richtig öffnet
    with open(audio_dir / "uebersicht.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Pfad", "Thema", "Länge", "Nr", "Satz", "Stimme", "Azure-Stimme", "Tempo"])
        w.writerows(zeilen)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--neu", action="store_true", help="alle MP3s neu erzeugen")
    ap.add_argument("--nur-seiten", action="store_true", help="keine Sprachsynthese, nur site/index.html bauen")
    a = ap.parse_args()

    lang = json.loads((PROJEKT / "saetze.json").read_text(encoding="utf-8"))
    kurz = json.loads((PROJEKT / "saetze_kurz.json").read_text(encoding="utf-8"))
    if list(lang) != list(kurz):
        raise SystemExit("saetze.json und saetze_kurz.json müssen dieselben Themen in derselben Reihenfolge haben")
    stimmen = json.loads((PROJEKT / "stimmen.json").read_text(encoding="utf-8"))
    nummern = nummeriere(lang, kurz)
    saetze = [e for laengen in nummern.values() for liste in laengen.values() for e in liste]
    audio_dir = PROJEKT / "site" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    if not a.nur_seiten:
        erzeuge_mp3s(saetze, stimmen, audio_dir, a.neu)
    baue_seite(nummern, stimmen)
    schreibe_uebersicht(nummern, stimmen, audio_dir)
    print("site/index.html, site/audio/README.md und site/audio/uebersicht.csv geschrieben")


if __name__ == "__main__":
    main()
