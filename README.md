# Wortwärts

Deutsche Alltagssätze zum Hören und Nachsprechen. Wortwärts richtet sich an Menschen mit
Aphasie nach einem Schlaganfall (insbesondere Wernicke-Aphasie), ihre Angehörigen und
Therapeut:innen. Es ergänzt eine logopädische Therapie, ersetzt sie aber nicht.

**Direkt ausprobieren:** https://tvanekeris.github.io/wortwaerts/

## Funktionen
- 110 Sätze in 10 Themen zu je 11 Sätzen: Begrüßung & Smalltalk, Essen & Trinken, Einkaufen,
  Unterwegs, Arbeit & Termine, Zuhause & Familie, Gesundheit, Freizeit & Verabredungen,
  Verständigung & Höflichkeit, Wetter & Zeit
- Alle abspielen / Pause / Weiter / Stopp, ein Thema abspielen oder einen einzelnen Satz per Klick
- Tempo 0,5×–1,5×, die Tonhöhe bleibt dabei gleich
- Sprachausgabe über fertige MP3-Aufnahmen (Piper, Stimme „Thorsten“). Bietet der Browser eine
  deutsche Stimme an, kann man auf diese umschalten. Startet sie nicht, fällt die Seite
  automatisch auf MP3 zurück.
- Alle Sätze als eine MP3-Datei (ca. 5 Minuten) zum Hören in jedem Player:
  [site/audio/alle-saetze.mp3](site/audio/alle-saetze.mp3)

## Aufbau
| Pfad | Inhalt |
|------|--------|
| [saetze.json](saetze.json) | Die Sätze, Format `{"Thema": ["Satz", …]}` |
| [vorlage/seite.html](vorlage/seite.html) | HTML-Vorlage des Players |
| [scripts/erzeuge_audio.py](scripts/erzeuge_audio.py) | Erzeugt MP3s und baut daraus die Seiten |
| [site/](site/) | Fertige Webseite mit `audio/001.mp3` … `110.mp3`, wird als GitHub Pages veröffentlicht |
| `alltagssaetze.html` | Dieselbe Seite als eine Datei mit eingebetteten MP3s, z. B. zum Weitergeben oder Offline-Öffnen |
| [docs/werkzeuge.md](docs/werkzeuge.md) | Verwendete Werkzeuge, Versionen, Ablauf |
| [.github/workflows/pages.yml](.github/workflows/pages.yml) | Veröffentlicht `site/` bei jedem Push auf `main` |

## Sätze ändern
1. `saetze.json` bearbeiten.
2. Audio neu erzeugen (Piper und ffmpeg nötig, siehe [docs/werkzeuge.md](docs/werkzeuge.md)):
   ```
   python3 scripts/erzeuge_audio.py --piper venv/bin/piper --modell voice/de-thorsten-low.onnx
   ```
   Nur die HTML-Seiten neu bauen (nach Änderungen an der Vorlage):
   `python3 scripts/erzeuge_audio.py --nur-seiten`
3. Committen und auf `main` pushen. Die Seite wird automatisch aktualisiert.

## Stand und nächste Schritte
- Ausgelagert aus dem privaten Sammel-Repo `claude-chats` (Projekt „Alltagssätze“); die
  bisherige Git-Historie ist übernommen.
- Mögliche nächste Schritte: bessere Stimme (Piper medium/high), Nachsprech-Pausen nach jedem
  Satz, Bilder zu den Sätzen, größere Schrift und Bedienelemente.

## Lizenzen
- Stimme „Thorsten“ (Thorsten Müller): CC0
- Piper (`piper-tts`): nur als Werkzeug zum Erzeugen der Audiodateien genutzt, nicht Teil der Seite
- Für den eigenen Code und die Sätze ist noch keine Lizenz festgelegt.
