#!/usr/bin/env python3
"""
Zweck:   Misst die mittlere Tonhöhe (Grundfrequenz F0, Median über die stimmhaften Abschnitte)
         von MP3-Dateien – z. B. um tiefe und hohe Stimmen der Probehör-Seite zu vergleichen.
         Einfache Autokorrelation je 40-ms-Fenster, Suchbereich 60–400 Hz.
Aufruf:  python3 scripts/messe_tonhoehe.py site/stimmen/audio/*-0.8.mp3
Pakete:  Python 3, numpy (pip install numpy), ffmpeg (System)
"""
import subprocess
import sys

import numpy as np

RATE = 16000


def lade(pfad):
    roh = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", pfad, "-f", "s16le",
                          "-ac", "1", "-ar", str(RATE), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(roh, dtype=np.int16).astype(np.float32) / 32768


def grundfrequenz(signal):
    fenster, schritt = int(0.04 * RATE), int(0.01 * RATE)
    lag_min, lag_max = RATE // 400, RATE // 60
    pegel = np.sqrt(np.mean(signal ** 2))
    werte = []
    for start in range(0, len(signal) - fenster, schritt):
        x = signal[start:start + fenster]
        x = x - x.mean()
        if np.sqrt(np.mean(x ** 2)) < pegel * 0.5:   # leise Stellen/Pausen auslassen
            continue
        ak = np.correlate(x, x, "full")[fenster - 1:]
        if ak[0] <= 0:
            continue
        lag = lag_min + int(np.argmax(ak[lag_min:lag_max]))
        if ak[lag] / ak[0] > 0.5:                     # nur deutlich periodische (stimmhafte) Fenster
            werte.append(RATE / lag)
    return float(np.median(werte)) if werte else float("nan")


def main():
    ergebnisse = sorted((grundfrequenz(lade(p)), p) for p in sys.argv[1:])
    for f0, pfad in ergebnisse:
        print(f"{f0:6.0f} Hz  {pfad}")


if __name__ == "__main__":
    main()
