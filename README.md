# Wortwärts

Deutsche Alltagssätze zum Hören und Nachsprechen. Wortwärts richtet sich an Menschen mit
Aphasie nach einem Schlaganfall (insbesondere Wernicke-Aphasie), ihre Angehörigen und
Therapeut:innen. Es ergänzt eine logopädische Therapie, ersetzt sie aber nicht.

**Direkt ausprobieren:** https://tvanekeris.github.io/wortwaerts/

## So funktioniert es
1. **Stimme** wählen: Frau oder Mann.
2. **Tempo** wählen: langsam (0,5×), mittel (0,7×) oder normal (1,0×).
3. **Thema** antippen – eines von 10 Themen oder „Alle Themen“. Ein zufälliger Satz aus dem
   Thema wird sofort vorgespielt.
4. Mit dem großen **Abspielen**-Knopf den Satz so oft wiederholen wie nötig.
5. **Satz aufdecken** zeigt den Text – erst nach dem Hören, zum Üben des Sprachverständnisses.
6. **Neuer Satz** spielt den nächsten Zufallssatz aus dem Thema.

110 Sätze in 10 Themen zu je 11 Sätzen: Begrüßung & Smalltalk, Essen & Trinken, Einkaufen,
Unterwegs, Arbeit & Termine, Zuhause & Familie, Gesundheit, Freizeit & Verabredungen,
Verständigung & Höflichkeit, Wetter & Zeit.

Die Aufnahmen kommen von Microsoft Azure (neuronale Stimmen); jedes Tempo ist eigens
eingesprochen, nicht nachträglich verlangsamt. Probehören aller deutschen Stimmen:
https://tvanekeris.github.io/wortwaerts/stimmen/

## Aufbau
| Pfad | Inhalt |
|------|--------|
| [saetze.json](saetze.json) | Die Sätze, Format `{"Thema": ["Satz", …]}` |
| [stimmen.json](stimmen.json) | Welche Azure-Stimme für „Frau“ und „Mann“ verwendet wird |
| [vorlage/seite.html](vorlage/seite.html) | HTML-Vorlage der App |
| [scripts/erzeuge_audio.py](scripts/erzeuge_audio.py) | Erzeugt die MP3s (Azure) und baut daraus `site/index.html` |
| [scripts/stimmproben.py](scripts/stimmproben.py) | Baut die Probehör-Seite `site/stimmen/` |
| [scripts/test_seite.py](scripts/test_seite.py) | Prüft die Seite (Themen, alle Aufnahmen, Hinweis ohne JavaScript) |
| [site/](site/) | Fertige Webseite mit `audio/<frau\|mann>/<tempo>/001.mp3` …, wird als GitHub Pages veröffentlicht |
| [docs/werkzeuge.md](docs/werkzeuge.md) | Verwendete Werkzeuge, Versionen, Ablauf |
| [.github/workflows/pages.yml](.github/workflows/pages.yml) | Veröffentlicht `site/` bei jedem Push auf `main` |

## Sätze oder Stimmen ändern
1. `saetze.json` bzw. `stimmen.json` bearbeiten.
2. Audio erzeugen (Azure-Zugang und ffmpeg nötig, siehe [docs/werkzeuge.md](docs/werkzeuge.md)):
   ```
   python3 scripts/erzeuge_audio.py
   ```
   Es werden nur geänderte bzw. fehlende Aufnahmen neu erzeugt. Nur die Seite neu bauen
   (nach Änderungen an der Vorlage): `python3 scripts/erzeuge_audio.py --nur-seiten`
3. `python3 scripts/test_seite.py` ausführen, committen und auf `main` pushen. Die Seite wird
   automatisch aktualisiert.

## Stand und nächste Schritte
- Ausgelagert aus dem privaten Sammel-Repo `claude-chats` (Projekt „Alltagssätze“); die
  bisherige Git-Historie ist übernommen.
- Die Stimmen (vorläufig Seraphina und Killian) wählt der Patient noch aus.
- Mögliche nächste Schritte: Bilder zu den Sätzen, Nachsprech-Pausen, weitere Themen.

## Lizenzen
- Audio: erzeugt mit Microsoft Azure AI Speech (Nutzung gemäß den Azure-Bedingungen)
- Für den eigenen Code und die Sätze ist noch keine Lizenz festgelegt.
