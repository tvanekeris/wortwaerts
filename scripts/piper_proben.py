#!/usr/bin/env python3
"""
Zweck:   Erzeugt Hörproben eines Testsatzes mit Piper-Stimmen (offline, frei), um sie mit den
         Azure-Stimmen zu vergleichen. Lädt fehlende Modelle von Hugging Face
         (rhasspy/piper-voices) und schreibt je Stimme eine MP3 in normalem Tempo und eine
         langsame (Piper-Parameter --length-scale, d. h. von Piper selbst langsamer gesprochen).
Aufruf:  python3 scripts/piper_proben.py --piper <venv>/bin/piper --modelle <ordner> --ziel <ordner>
         python3 scripts/piper_proben.py ... --stimme de_DE-thorsten-high --stimme de_DE-mls-medium:12
         (Stimme als Modellname, bei Modellen mit mehreren Sprechern mit :Sprechernummer)
Pakete:  piper-tts 1.8.0 (pip install piper-tts, bringt onnxruntime mit), ffmpeg (System);
         Netzzugriff auf huggingface.co und us.aws.cdn.hf.co für den Modell-Download
"""
import argparse
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from erzeuge_audio import zu_mp3  # noqa: E402

BASIS = "https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE"
SATZ = "Ich hätte gern einen Kaffee mit Milch, bitte."
STIMMEN = ["de_DE-thorsten-high", "de_DE-kerstin-low"]
LANGSAM = 2.0   # length-scale: 2.0 = halbes Tempo, entspricht etwa Tempo 0,5


def lade_modell(name, ordner):
    _, sprecher, qualitaet = name.split("-", 2)
    for endung in ("onnx", "onnx.json"):
        ziel = ordner / f"{name}.{endung}"
        if not ziel.exists():
            urllib.request.urlretrieve(f"{BASIS}/{sprecher}/{qualitaet}/{name}.{endung}", ziel)
    return ordner / f"{name}.onnx"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--piper", required=True)
    ap.add_argument("--modelle", type=Path, required=True)
    ap.add_argument("--ziel", type=Path, required=True)
    ap.add_argument("--stimme", action="append", help="Modellname[:Sprecher], mehrfach möglich")
    ap.add_argument("--satz", default=SATZ)
    a = ap.parse_args()
    a.modelle.mkdir(parents=True, exist_ok=True)
    a.ziel.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as t:
        wav = Path(t) / "x.wav"
        for eintrag in a.stimme or STIMMEN:
            name, _, sprecher = eintrag.partition(":")
            modell = lade_modell(name, a.modelle)
            for tempo, skala in (("normal", 1.0), ("langsam", LANGSAM)):
                cmd = [a.piper, "-m", str(modell), "-f", str(wav), "--length-scale", str(skala)]
                if sprecher:
                    cmd += ["-s", sprecher]
                subprocess.run(cmd, input=a.satz.encode("utf-8"), check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                mp3 = a.ziel / f"piper-{name.removeprefix('de_DE-')}{'-' + sprecher if sprecher else ''}-{tempo}.mp3"
                zu_mp3(wav, mp3)
                print(mp3)


if __name__ == "__main__":
    main()
