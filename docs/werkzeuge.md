# Werkzeuge & Ablauf: Audio für die Alltagssätze

Ziel: Sprachausgabe nicht mehr über die Browser-Stimme (`speechSynthesis`), sondern über
fertige MP3-Dateien, die überall abspielbar sind (Artifact, Webseite, beliebiger Player).

## Verwendete Software

| Werkzeug | Version | Installation / Quelle |
|----------|---------|-----------------------|
| Python | 3.13.17 | System (Ubuntu 24.04) |
| piper-tts | 1.8.0 | `python3 -m venv venv && ./venv/bin/pip install piper-tts` (PyPI) |
| onnxruntime | 1.31.1 | Abhängigkeit von piper-tts |
| numpy | 2.5.4 | Abhängigkeit von piper-tts |
| Stimme „Thorsten“ (de, low, 16 kHz, Lizenz CC0) | Piper-Release v0.0.2 | https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-de-thorsten-low.tar.gz (entpacken: `de-thorsten-low.onnx` + `.onnx.json`) |
| ffmpeg (inkl. libmp3lame) | 6.1.1-3ubuntu5 | System, `apt install ffmpeg` |
| Playwright + Chromium | vorinstalliert im Container | nur für den Funktionstest (Abspielen, Satzwechsel, Tempo) |

Hinweis: Die besseren Piper-Stimmen (medium/high) liegen auf huggingface.co, das in der
Cloud-Umgebung gesperrt war. Mit Zugriff darauf kann man z. B. `de_DE-thorsten-high`
verwenden und das Skript einfach erneut laufen lassen.

## Schritte

1. Piper und Stimme wie oben installieren bzw. herunterladen.
2. Im Projektordner ausführen:
   ```
   python3 scripts/erzeuge_audio.py --piper venv/bin/piper --modell voice/de-thorsten-low.onnx
   ```
   Das Skript
   - spricht jeden Satz aus `saetze.json` (Format `{"Thema": ["Satz", …]}`) mit Piper ein (WAV),
   - wandelt ihn mit ffmpeg in MP3 um (Lautheit normalisiert, mono, 22,05 kHz, 48 kbit/s) → `site/audio/001.mp3` … `110.mp3` (alte MP3s werden vorher gelöscht),
   - erzeugt `site/audio/alle-saetze.mp3` (alle Sätze mit 0,8 s Pause),
   - füllt `vorlage/seite.html` zweimal: `site/index.html` (lädt die MP3-Dateien) und
     `alltagssaetze.html` (MP3s als base64-`data:`-URIs eingebettet, für das Artifact).
   Nur die Seiten neu bauen (z. B. nach Änderungen an `vorlage/seite.html`), ohne neue MP3s:
   `python3 scripts/erzeuge_audio.py --nur-seiten`
3. Artifact mit `alltagssaetze.html` veröffentlichen.

## Test

Playwright-Skript (nicht im Repo, Wegwerf-Test): Chromium mit
`--autoplay-policy=no-user-gesture-required`, drei Fälle über eine nachgebaute
`speechSynthesis`: keine Stimme (Schalter versteckt, MP3), funktionierende Stimme
(Schalter sichtbar, Browser spricht), stumme Stimme (Rückfall auf MP3 nach 2,5 s).

## Tempo

Der Player nutzt `HTMLAudioElement.playbackRate` (0,5×–1,5×) mit `preservesPitch`,
die Tonhöhe bleibt also gleich. Für `alle-saetze.mp3` in einem normalen Player regelt man
das Tempo dort (die meisten Podcast-/Medienplayer können das).
