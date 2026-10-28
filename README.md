# Alltagssätze zum Hören

- **Begonnen:** 2026-10-28
- **Status:** aktiv

## Ziel
Deutsche Alltagssätze zum Hören: Player mit Play-Button und einstellbarem Tempo. Die
Sprachausgabe läuft über echte Audiodateien, damit sie im Artifact, als Webseite und auch
ohne Browser (MP3 in jedem Player) funktioniert.

## Aktueller Stand
110 Sätze in 10 Themen zu je 11 Sätzen (Begrüßung & Smalltalk, Essen & Trinken, Einkaufen,
Unterwegs, Arbeit & Termine, Zuhause & Familie, Gesundheit, Freizeit & Verabredungen,
Verständigung & Höflichkeit, Wetter & Zeit). Audio offline mit Piper (Stimme „Thorsten“, low)
erzeugt, siehe [docs/werkzeuge.md](docs/werkzeuge.md).

Funktionen: Alle abspielen / Pause / Weiter / Stopp, Thema abspielen, Tempo 0,5×–1,5× (auch
während der Wiedergabe, Tonhöhe bleibt gleich), Einzelsatz per Klick.

Verlauf:
1. Erste Version mit 10 Sätzen über die Browser-Sprachausgabe (`speechSynthesis`) – blieb im
   Artifact stumm (Stand in der Git-Historie, altes Artifact: https://claude.ai/artifact/N476Y37MscE6DGXHHHhiPr, veraltet).
2. Umstellung auf mit Piper erzeugte MP3-Dateien.
3. Auf 110 Sätze in 10 Themen erweitert, englische Übersetzung entfernt.

Mögliche nächste Schritte: bessere Stimme (Piper medium/high, braucht Zugriff auf huggingface.co).

## Ergebnisse & Links
- Artifact: https://claude.ai/artifact/5vRJ13E9FKV4QFw9dp6BWt (Quelle: [alltagssaetze.html](alltagssaetze.html))
- Webseite (lokal per Doppelklick oder auf jedem Webserver): [site/index.html](site/index.html)
- MP3-Dateien: [site/audio/](site/audio/) – einzeln `001.mp3`…`110.mp3`, gesamt `alle-saetze.mp3` (ca. 5 Minuten)
- Sätze bearbeiten: [saetze.json](saetze.json), danach [scripts/erzeuge_audio.py](scripts/erzeuge_audio.py) erneut ausführen
