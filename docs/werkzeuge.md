# Werkzeuge & Ablauf

## Die App (Stand 2026-10-30)

Eine Seite (`site/index.html`, gebaut aus `vorlage/seite.html`): 1 Stimme (Frau/Mann) →
2 Tempo (0,5 / 0,7 / 1,0) → 3 Satzlänge (kurze Sätze mit 3–4 Wörtern aus `saetze_kurz.json` /
lange Sätze aus `saetze.json`) → 4 Thema (14 Themen + „Alle Themen“). Nach der Themenwahl spielt
die Seite sofort einen zufälligen Satz ab; der Text bleibt verdeckt, bis man „Satz aufdecken“
drückt. „Neuer Satz“ wählt und spielt den nächsten Zufallssatz. Innerhalb eines Themas kommt
jeder Satz einmal dran, bevor sich etwas wiederholt. Beim Laden ist „Alle Themen“ gewählt und
ein Zufallssatz vorgeladen (abgespielt wird erst nach dem ersten Tipp – Browser erlauben Ton
erst nach einer Bedienung). Standard beim ersten Besuch: Frau, langsam, kurze Sätze. Stimme, Tempo und Satzlänge merkt
sich der Browser
(`localStorage`, nur Komfort).

Alle Kombinationen sind fertige MP3s, das Tempo wird **nicht** im Browser umgerechnet, sondern
von Azure beim Sprechen erzeugt (SSML `<prosody rate>`), das klingt natürlicher:
`site/audio/<Thema>/<kurz|lang>/<frau|mann>/<0.5|0.7|1.0>/<Nr>.mp3`, z. B.
`site/audio/02-essen-trinken/kurz/frau/0.5/k011.mp3`. Die Themen-Ordner sind in der Reihenfolge
der Themen nummeriert und ohne Umlaute/Sonderzeichen geschrieben; lange Sätze heißen `001.mp3` …
`148.mp3`, kurze `k001.mp3` … `k140.mp3` (Nummern über alle Themen eindeutig) –
288 Sätze × 2 Stimmen × 3 Tempi = 1.728 Dateien. Welche Stimmen verwendet werden, steht in `stimmen.json`.

## Microsoft Azure AI Speech

| Baustein | Version / Stand | Quelle |
|----------|-----------------|--------|
| Azure AI Speech, Text-to-Speech REST-API (`/cognitiveservices/v1`) | abgerufen 2026-10-30 | https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech |
| Tarif | Free F0 (laut Preisseite 0,5 Mio. Zeichen/Monat für neuronale Stimmen; ein kompletter Durchlauf ≈ 47.000 Zeichen: lang 31.600, kurz 15.400) | https://azure.microsoft.com/de-de/pricing/details/speech/ |
| Region | Germany West Central (`germanywestcentral`) | Azure-Portal |
| Stimmen (vorläufig) | Frau: `de-DE-SeraphinaMultilingualNeural`, Mann: `de-DE-KillianNeural` | `stimmen.json` |
| Ausgabeformat | `riff-24khz-16bit-mono-pcm` (WAV), danach ffmpeg → MP3 (24 kHz, mono, 64 kbit/s, Lautheit normalisiert) | |
| ffmpeg (inkl. libmp3lame) | 6.1.1-3ubuntu5 | System, `apt install ffmpeg` |
| Python | 3.13, nur Standardbibliothek (`urllib`), keine Zusatzpakete, kein Node.js | |

Einrichtung (einmalig):
1. Azure-Konto mit Subscription (kostenloses Konto oder „Nutzungsbasierte Bezahlung“).
2. Ressource „Speech-Dienste“ anlegen: Region Germany West Central, Tarif Free F0.
3. „Schlüssel und Endpunkt“ → Schlüssel 1. Als Umgebungsvariablen bereitstellen:
   `AZURE_SPEECH_KEY` (Schlüssel) und `AZURE_SPEECH_REGION` (`germanywestcentral`).
   In der Claude-Cloud-Umgebung: Umgebung bearbeiten → Network secrets; außerdem unter
   Network access die Domain `germanywestcentral.tts.speech.microsoft.com` erlauben.

Ablauf:
```
python3 scripts/erzeuge_audio.py               # fehlende/geänderte MP3s erzeugen + Seite bauen
python3 scripts/erzeuge_audio.py --neu         # alle 1.728 MP3s neu erzeugen
python3 scripts/erzeuge_audio.py --nur-seiten  # nur site/index.html (nach Änderung der Vorlage)
```
Übersicht für Menschen (wird bei jedem Lauf, auch mit `--nur-seiten`, neu geschrieben):
`site/audio/README.md` – je Thema eine Tabelle mit Nummer, Satz und Links auf alle sechs
Aufnahmen; `site/audio/uebersicht.csv` – jede MP3 eine Zeile (Pfad, Thema, Länge, Nr, Satz,
Stimme, Azure-Stimme, Tempo), Semikolon-getrennt, UTF-8 mit BOM, öffnet direkt in Excel.

Ändert sich nur der Ablageort einer Aufnahme (z. B. Thema umbenannt, Ordnerstruktur geändert,
Nummern aufgerückt, weil ein Satz gelöscht wurde), verschiebt das Skript die vorhandene Datei
über ein Zwischenlager (`site/audio/.umzug`, wird danach gelöscht), statt sie neu zu erzeugen.

Das Skript führt in `site/audio/manifest.json` Buch, mit welcher Stimme, welchem Tempo und
welchem Text jede Datei erzeugt wurde. Ändert man `stimmen.json`, `saetze.json` oder
`saetze_kurz.json`, werden
nur die betroffenen Dateien neu erzeugt. Der Gratis-Tarif erlaubt nur wenige Anfragen pro
Minute (das Skript wartet bei HTTP 429 automatisch); ein kompletter Durchlauf dauert etwa
eine Stunde (rund 3 Sekunden je Aufnahme).

Stimme wechseln: Kurznamen in `stimmen.json` eintragen (Liste:
`python3 scripts/stimmproben.py --liste`), dann `python3 scripts/erzeuge_audio.py`.

### Probehör-Seite `site/stimmen/`

```
python3 scripts/stimmproben.py              # alle deutschen Stimmen, Testsatz in 0,5× und 0,8×
python3 scripts/stimmproben.py --nur-seite  # nur HTML neu bauen
```
Online: https://tvanekeris.github.io/wortwaerts/stimmen/ (17 Stimmen, Stand 2026-10-30;
Frauen- und Männerstimmen gruppiert).

Tonhöhe der Stimmen vergleichen: `python3 scripts/messe_tonhoehe.py site/stimmen/audio/*-0.8.mp3`
(numpy 2.5.3, im Container vorhanden; sonst `pip install numpy`). Ergebnis 2026-10-30 (Median F0):
Killian 103 Hz, Conrad 111, Christoph 113, Klaus 117, Florian 132, Kasper 136, Ralf 145, Bernd 152;
Frauen 165 (Seraphina) bis 229 Hz (Maja), Gisela 302 Hz.

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

| Werkzeug | Version | Quelle |
|----------|---------|--------|
| Chromium (Chrome for Testing) | 153.0.8010.12 | im Container vorinstalliert unter `/opt/pw-browsers/chromium`; sonst z. B. `apt install chromium` |

- `scripts/test_seite.py` (Python 3, nur Standardbibliothek, plus Chromium; **kein Node.js**):
  startet einen kleinen Webserver für `site/`, lässt Chromium die Seite headless laden
  (`--dump-dom`) und prüft, ob es für jedes Thema einen Knopf gibt (plus „Alle Themen“), ob
  alle 1.728 Aufnahmen abrufbar sind und ob das HTML den `<noscript>`-Hinweis enthält.
  ```
  python3 scripts/test_seite.py                                            # lokal
  python3 scripts/test_seite.py https://tvanekeris.github.io/wortwaerts/   # live
  ```
- Bedienung (einmalig im Browser getestet, nicht im Repo, mit dem im Container
  vorinstallierten Playwright): Thema wählen spielt sofort ab, Aufdecken/Verdecken,
  „Neuer Satz“ (11 verschiedene Sätze in 11 Schritten, keine direkte Wiederholung),
  Stopp/Nochmal, Einstellungen bleiben nach Neuladen erhalten; iPhone-Ansicht.

## Einblenden am Satzanfang

Problem: Das erste Wort eines Satzes klang wie eingeblendet und undeutlich.

Messung (`scripts/messe_einsatz.html`, Chromium; Hüllkurve in 25-ms-Schritten): Was der
Browser ausgibt, entspricht den MP3-Dateien – die Sprache setzt nach 1–2 Schritten mit voller
Lautstärke ein. Das Einblenden entsteht also **nach** dem Browser: Betriebssystem bzw.
Audiogerät schalten die Ausgabe in Pausen ab (Bluetooth-Kopfhörer/-Lautsprecher,
HDMI-Monitore, Energiesparmodus der Soundkarte) und blenden beim nächsten Ton erst wieder ein.

Abhilfe in der App: Beim Abspielen läuft über Web Audio ein unhörbarer Ton (20 Hz, -80 dB),
der die Ausgabe offen hält. Beim ersten Abspielen (oder nach mehr als 60 s Stille) wartet die
App 0,4 s, bevor der Satz beginnt. 60 s nach dem letzten Satz wird der Ton angehalten.
Außerdem beginnen die Azure-Aufnahmen mit gut 0,1 s Stille.

## Kurze Sätze

Die 100 kurzen Sätze (`saetze_kurz.json`, 10 je Thema, je 3–4 Wörter) wurden am 2026-10-30 von
Claude (Anthropic) passend zu den Themen formuliert und geprüft: Wortzahl 3–4, keine Dubletten,
dieselben Themen in derselben Reihenfolge wie `saetze.json` (prüft auch `erzeuge_audio.py`).

## Weitere Themen (2026-10-30)

Vier Themen speziell für den Alltag nach einem Schlaganfall, je 10 kurze und 10 lange Sätze,
von Claude (Anthropic) formuliert: Körperpflege & Anziehen, Gefühle & Bedürfnisse,
Hilfe & Notfall, Therapie & Reha. Sie stehen am Ende von `saetze.json` / `saetze_kurz.json`,
damit die Nummern der bisherigen Sätze (und deren Aufnahmen) gleich bleiben – neue Themen
immer hinten anfügen. Symbole: Strichzeichnungen in `vorlage/seite.html` (`SYMBOLE`).
