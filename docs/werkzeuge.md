# Werkzeuge & Ablauf: Audio für die Alltagssätze

## Microsoft Azure AI Speech (aktuelle Quelle für die Stimmen)

| Baustein | Version / Stand | Quelle |
|----------|-----------------|--------|
| Azure AI Speech, Text-to-Speech REST-API (`/cognitiveservices/v1`) | abgerufen 2026-10-30 | https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech |
| Tarif | Free F0 (laut Preisseite 0,5 Mio. Zeichen/Monat für neuronale Stimmen; alle Sätze ≈ 4.000 Zeichen) | https://azure.microsoft.com/de-de/pricing/details/speech/ |
| Region | Germany West Central (`germanywestcentral`) | Azure-Portal |
| Ausgabeformat | `riff-24khz-16bit-mono-pcm` (WAV), danach ffmpeg → MP3 (24 kHz, mono, 64 kbit/s, Lautheit normalisiert) | |
| Python | 3, nur Standardbibliothek (`urllib`), keine Zusatzpakete, kein Node.js | |

Einrichtung (einmalig):
1. Azure-Konto mit Subscription (kostenloses Konto oder „Nutzungsbasierte Bezahlung“).
2. Ressource „Speech-Dienste“ anlegen: Region Germany West Central, Tarif Free F0.
3. „Schlüssel und Endpunkt“ → Schlüssel 1. Als Umgebungsvariablen bereitstellen:
   `AZURE_SPEECH_KEY` (Schlüssel) und `AZURE_SPEECH_REGION` (`germanywestcentral`).
   In der Claude-Cloud-Umgebung: Umgebung bearbeiten → Network secrets; außerdem unter
   Network access die Domain `germanywestcentral.tts.speech.microsoft.com` erlauben.

Ablauf:
```
python3 scripts/stimmproben.py --liste                 # deutsche Stimmen anzeigen
python3 scripts/stimmproben.py                         # Probehör-Seite site/stimmen/ (alle Stimmen,
                                                       # Testsatz in 0,5× und 0,8×, Tempo per SSML <prosody rate>)
python3 scripts/erzeuge_audio.py --azure de-DE-KatjaNeural   # alle Sätze neu erzeugen
```
Die Probehör-Seite ist online unter https://tvanekeris.github.io/wortwaerts/stimmen/ (17 Stimmen,
Stand 2026-10-30).

`erzeuge_audio.py` schreibt den Stimmennamen nach `site/audio/stimme.txt`; die Seite zeigt ihn an.

## Piper (frühere Quelle, offline)

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
| Chromium (Chrome for Testing) | 153.0.8010.12 | im Container vorinstalliert unter `/opt/pw-browsers/chromium`; sonst z. B. `apt install chromium` – nur für den Test der Seite |

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
3. Auf `main` pushen: Der Workflow `.github/workflows/pages.yml` veröffentlicht `site/` als
   GitHub Pages (https://tvanekeris.github.io/wortwaerts/).
4. Optional: `alltagssaetze.html` (eine Datei mit eingebetteten MP3s) weitergeben oder als
   Claude-Artifact veröffentlichen.

## GitHub Pages

| Baustein | Version | Quelle |
|----------|---------|--------|
| actions/checkout | v6 | https://github.com/actions/checkout |
| actions/configure-pages | v6 | https://github.com/actions/configure-pages |
| actions/upload-pages-artifact | v5 | https://github.com/actions/upload-pages-artifact |
| actions/deploy-pages | v5 | https://github.com/actions/deploy-pages |

Diese Versionen laufen bei GitHub auf Node.js 24 (die älteren auf Node.js 20 erzeugten die
Warnung „Node.js 20 is deprecated“). Node.js läuft dabei nur intern auf GitHubs Servern;
das Projekt selbst braucht kein Node.js.

Einmalig im Repo einstellen: Settings → Pages → Source: „GitHub Actions“. Das Repo muss
öffentlich sein (oder ein bezahlter GitHub-Plan vorliegen).

## Test

- `scripts/test_seite.py` (Python 3, nur Standardbibliothek, plus Chromium; **kein Node.js**):
  startet einen kleinen Webserver für `site/`, lässt Chromium die Seite headless laden
  (`--dump-dom`) und prüft, ob alle Sätze aus `saetze.json` in der Liste stehen. Außerdem
  prüft es, ob das HTML den `<noscript>`-Hinweis für ausgeschaltetes JavaScript enthält.
  ```
  python3 scripts/test_seite.py                                            # lokal
  python3 scripts/test_seite.py https://tvanekeris.github.io/wortwaerts/   # live
  ```
- Frühere Wegwerf-Tests (nicht im Repo, mit Node.js + Playwright): Abspielen, Satzwechsel,
  Tempo; Schalter MP3/Browser-Stimme (keine Stimme, funktionierende Stimme, stumme Stimme
  mit Rückfall auf MP3); Satzliste auf iPhone/Dunkelmodus, ohne `speechSynthesis`, ohne
  localStorage.

## Tempo

Der Player nutzt `HTMLAudioElement.playbackRate` (0,5×–1,5×) mit `preservesPitch`,
die Tonhöhe bleibt also gleich. Für `alle-saetze.mp3` in einem normalen Player regelt man
das Tempo dort (die meisten Podcast-/Medienplayer können das).

## Einblenden am Satzanfang

Problem: Das erste Wort eines Satzes klang wie eingeblendet und undeutlich.

Messung (`scripts/messe_einsatz.html`, Chromium; Hüllkurve in 25-ms-Schritten): Was der
Browser ausgibt, entspricht den MP3-Dateien – die Sprache setzt nach 1–2 Schritten mit voller
Lautstärke ein, bei 1,0× ohne Einblenden. Bei 0,7× und 0,5× macht die Tempo-Umrechnung
(`preservesPitch`) den Einsatz nur um etwa 25 ms weicher. Das Einblenden entsteht also
**nach** dem Browser: Betriebssystem bzw. Audiogerät schalten die Ausgabe in Pausen ab
(Bluetooth-Kopfhörer/-Lautsprecher, HDMI-Monitore, Energiesparmodus der Soundkarte) und
blenden beim nächsten Ton erst wieder ein.

Abhilfe im Player: Beim Abspielen läuft über Web Audio ein unhörbarer Ton (20 Hz, -80 dB),
der die Ausgabe offen hält. Beim ersten Start (oder nach mehr als 30 s Stille) wartet der
Player 0,4 s, bevor der Satz beginnt. 30 s nach dem Stopp wird der Ton angehalten.
