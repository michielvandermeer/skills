#!/usr/bin/env python3
"""Turn each scene's narration text into a WAV file and record how long it is.

    narrate.py SCENE.txt [SCENE.txt ...] --out DIR [--voice NAME] [--lang CODE] [--kokoro-dir DIR]

Writes DIR/<stem>.wav per scene, merges each length in seconds into DIR/durations.json,
and prints "<stem> <seconds>". Uses xAI text-to-speech when XAI_API_KEY is set, and the
Kokoro model in --kokoro-dir otherwise.
"""
import argparse
import base64
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path


def xai(text, voice, lang, out):
    body = json.dumps({
        "text": text,
        "language": lang or "auto",
        "voice_id": voice or "eve",
        "output_format": {"codec": "wav", "sample_rate": 24000},
        "with_timestamps": True,
    }).encode()
    headers = {
        "Authorization": f"Bearer {os.environ['XAI_API_KEY']}",
        "Content-Type": "application/json",
    }
    for attempt in range(4):
        request = urllib.request.Request("https://api.x.ai/v1/tts", data=body, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=900) as response:
                payload = response.read()
                content_type = response.headers.get("Content-Type", "")
            break
        except urllib.error.HTTPError as error:
            if error.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            sys.exit(f"xAI text-to-speech failed: HTTP {error.code} {error.read().decode(errors='replace')}")
    if content_type.startswith("application/json"):
        data = json.loads(payload)
        out.write_bytes(base64.b64decode(data["audio"]))
        return data.get("duration")
    out.write_bytes(payload)
    return None


class Kokoro:
    def __init__(self, model_dir):
        import espeakng_loader
        from kokoro_onnx import Kokoro as Model
        from kokoro_onnx.config import EspeakConfig
        model_dir = Path(model_dir)
        data = Path(espeakng_loader.get_data_path()).resolve()
        # espeak-ng silently ignores a data path of 160 characters or more, so a deep venv gets a short copy.
        if len(str(data)) >= 150:
            short = model_dir / "espeak-ng-data"
            if not short.exists():
                shutil.copytree(data, short)
            data = short
        self.model = Model(
            str(model_dir / "kokoro-v1.0.onnx"),
            str(model_dir / "voices-v1.0.bin"),
            espeak_config=EspeakConfig(data_path=str(data)),
        )

    def __call__(self, text, voice, lang, out):
        import numpy as np
        samples, rate = self.model.create(text, voice=voice or "af_heart", speed=1.0, lang=lang or "en-us")
        pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2")
        with wave.open(str(out), "wb") as file:
            file.setnchannels(1)
            file.setsampwidth(2)
            file.setframerate(rate)
            file.writeframes(pcm.tobytes())
        return None


def seconds(path):
    with wave.open(str(path), "rb") as file:
        return file.getnframes() / file.getframerate()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scenes", nargs="+", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--voice")
    parser.add_argument("--lang")
    parser.add_argument("--kokoro-dir")
    args = parser.parse_args()

    if os.environ.get("XAI_API_KEY"):
        speak = xai
    elif args.kokoro_dir:
        speak = Kokoro(args.kokoro_dir)
    else:
        sys.exit("Set XAI_API_KEY, or pass --kokoro-dir with the Kokoro model files.")

    args.out.mkdir(parents=True, exist_ok=True)
    index = args.out / "durations.json"
    durations = json.loads(index.read_text()) if index.exists() else {}
    for scene in args.scenes:
        out = args.out / f"{scene.stem}.wav"
        reported = speak(scene.read_text().strip(), args.voice, args.lang, out)
        durations[scene.stem] = round(reported or seconds(out), 3)
        index.write_text(json.dumps(durations, indent=2) + "\n")
        print(scene.stem, durations[scene.stem])


if __name__ == "__main__":
    main()
