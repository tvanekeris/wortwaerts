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

Funktionen: Alle abspielen / Pause / Weiter / Stopp, Thema abspielen, Tempo 0,5×–1,5×
(Tonhöhe bleibt gleich), Einzelsatz per Klick.

Sprachausgabe: Standard sind die MP3-Aufnahmen. Bietet der Browser eine deutsche Stimme an,
erscheint ein Schalter „MP3-Aufnahme / Browser-Stimme“ (plus Auswahl der Stimme; die Wahl
wird im Browser gemerkt). Ohne deutsche Browser-Stimme bleibt der Schalter versteckt. Startet
die Browser-Stimme nicht innerhalb von 2,5 s oder meldet einen Fehler (z. B. im Artifact),
schaltet die Seite automatisch auf MP3 um und blendet den Schalter aus.

Verlauf:
1. Erste Version mit 10 Sätzen über die Browser-Sprachausgabe (`speechSynthesis`) – blieb im
   Artifact stumm (Stand in der Git-Historie, altes Artifact: https://claude.ai/artifact/N476Y37MscE6DGXHHHhiPr, veraltet).
2. Umstellung auf mit Piper erzeugte MP3-Dateien.
3. Auf 110 Sätze in 10 Themen erweitert, englische Übersetzung entfernt.
4. Schalter MP3 / Browser-Stimme mit automatischer Erkennung und Rückfall auf MP3.

Mögliche nächste Schritte: bessere Stimme (Piper medium/high, braucht Zugriff auf huggingface.co).

## Ergebnisse & Links
- Artifact: https://claude.ai/artifact/5vRJ13E9FKV4QFw9dp6BWt (Quelle: [alltagssaetze.html](alltagssaetze.html))
- Webseite (lokal per Doppelklick oder auf jedem Webserver): [site/index.html](site/index.html)
- MP3-Dateien: [site/audio/](site/audio/) – einzeln `001.mp3`…`110.mp3`, gesamt `alle-saetze.mp3` (ca. 5 Minuten)
- Sätze bearbeiten: [saetze.json](saetze.json), danach [scripts/erzeuge_audio.py](scripts/erzeuge_audio.py) erneut ausführen
