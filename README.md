# Alltagssätze zum Hören

- **Begonnen:** 2026-10-28
- **Status:** abgeschlossen

## Ziel
Kleines interaktives Artifact mit 10 deutschen Alltagssätzen und einem Play-Button,
der die Sätze nacheinander mit einstellbarer Geschwindigkeit vorliest.

## Aktueller Stand
**Abgelöst durch [2026-10-alltagssaetze-audio](../2026-10-alltagssaetze-audio/)** – die Browser-Stimme bleibt im Artifact stumm.

Die Sprachausgabe nutzt die Web Speech API des Browsers (`speechSynthesis`,
Sprache `de-DE`) – keine externen Dienste, keine Audiodateien.

Funktionen:
- „Alle abspielen“ / Pause / Weiter / Stopp, aktueller Satz wird hervorgehoben
- Tempo-Regler 0,5× bis 1,5×
- Auswahl der auf dem Gerät installierten deutschen Stimmen
- Klick auf einen einzelnen Satz spielt nur diesen ab
- Englische Übersetzung ein-/ausblendbar

## Ergebnisse & Links
- Artifact: https://claude.ai/artifact/N476Y37MscE6DGXHHHhiPr
- Quellcode: [alltagssaetze.html](alltagssaetze.html)
