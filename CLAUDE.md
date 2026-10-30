# Regeln für das Projekt Wortwärts

## Ansprache auf den Seiten
- Der Patient wird auf allen Seiten **geduzt** („Drück auf Abspielen“, „Welche Stimme gefällt dir?“),
  auch in Hinweisen, Fehlermeldungen, Knopf-Beschriftungen und `aria-label`s.
- Das gilt nicht für die Übungssätze selbst (`saetze.json`, `saetze_kurz.json`): Dort bleibt „Sie“ stehen, wo es zur
  Alltagssituation gehört („Könnten Sie mir bitte helfen?“).
- Seiten, die per Skript erzeugt werden, ändert man in der Quelle: `vorlage/seite.html`
  (Hauptseite) und `scripts/stimmproben.py` (Probehör-Seite `site/stimmen/`), danach neu bauen
  (`python3 scripts/erzeuge_audio.py --nur-seiten`, `python3 scripts/stimmproben.py --nur-seite`).

## Sätze
- Zwei Gruppen mit denselben Themen in derselben Reihenfolge: `saetze_kurz.json` (kurze Sätze,
  **3–4 Wörter**, wirklich einfach) und `saetze.json` (lange Sätze).
- Neue Themen immer **am Ende** anfügen: Die Sätze werden fortlaufend nummeriert, so bleiben
  die Nummern und Aufnahmen der bestehenden Sätze unverändert. Für jedes neue Thema ein Symbol
  in `SYMBOLE` (`vorlage/seite.html`) ergänzen.
