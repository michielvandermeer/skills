# Video

Under about three minutes unless the request asks for longer, built with Manim Community Edition ([ADR-0057](../../docs/adr/0057-a-video-is-manim-timed-by-narration-recorded-first.md)). **Narration first**: each scene's audio is recorded before it is animated, and its length sets the scene's timing.

Run every command below from `explain/<slug>/`.

## 1. Set up

One cache folder holds the environment, and later runs reuse it:

- Linux: `${XDG_CACHE_HOME:-$HOME/.cache}/mvdmio-explain/`
- macOS: `~/Library/Caches/mvdmio-explain/`
- Windows: `%LOCALAPPDATA%\mvdmio-explain\`

`<python>` below is `<cache>/venv/bin/python` (`<cache>\venv\Scripts\python` on Windows), and `<manim>` sits beside it. The cache is ready when `<python>` imports `manim` and — without `XAI_API_KEY` — `kokoro_onnx`, with `kokoro-v1.0.onnx` and `voices-v1.0.bin` in `<cache>/kokoro/`.

When anything is missing, list all of it in one message with its size, and ask once — even when the user named the video format:

- `uv`, which builds the environment and fetches Python 3.13 for it: a few MB.
- Manim with Typst math: about 0.5 GB.
- Without `XAI_API_KEY`, Kokoro and its model: about 0.4 GB.
- On Linux and macOS, when `pkg-config --exists cairo pangocairo` fails: the Cairo and Pango system libraries. Give the user the command for their system to run themselves, since it needs their admin password, and wait until they say it ran:
  - Debian, Ubuntu: `sudo apt install build-essential python3-dev pkg-config libcairo2-dev libpango1.0-dev`
  - Fedora: `sudo dnf install gcc python3-devel pkg-config cairo-devel pango-devel`
  - Arch: `sudo pacman -S --needed base-devel cairo pango`
  - macOS: `brew install cairo pkg-config`

On a yes, install what is missing — `uv` through its official installer, `curl -LsSf https://astral.sh/uv/install.sh | sh` (on Windows, `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`), then:

```sh
uv venv --python 3.13 <cache>/venv
uv pip install --python <cache>/venv "manim[typst]"
# Kokoro only without XAI_API_KEY:
uv pip install --python <cache>/venv kokoro-onnx
curl -L --create-dirs -o <cache>/kokoro/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -L --create-dirs -o <cache>/kokoro/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

On a no, build a page instead ([PAGE.md](PAGE.md)) and say why.

Done when `<python>` imports what this run needs, or the run has turned to a page.

## 2. Script

- `script.md` — the scene list. Per scene: a title, what is on screen, and its narration. It stays beside the video as its script.
- `narration/NN-<name>.txt` — each scene's narration alone.

One idea per scene, 15 to 40 seconds of narration each. Build the picture up piece by piece, and transform what is on screen rather than cutting to a new picture. The narration points at what appears as it appears. Numbers and symbols are written out as spoken words. When step 2 of `SKILL.md` showed the user a scene list, keep to it.

Done when every scene has its on-screen plan in `script.md` and its narration file.

## 3. Narrate

```sh
<python> <skill>/narrate.py narration/*.txt --out audio [--kokoro-dir <cache>/kokoro] [--voice <name>]
```

`<skill>` is this skill's folder. [narrate.py](narrate.py) speaks with xAI's voice `eve` when `XAI_API_KEY` is set, and Kokoro's `af_heart` otherwise; `--voice` takes another voice the user names. It writes `audio/<NN-name>.wav` and merges each length into `audio/durations.json`. After a narration edit, pass only the changed files.

Done when every scene has its WAV and its length in `audio/durations.json`.

## 4. Animate

`scenes.py` holds one `Scene`, `Explanation`, with one method per scene in order. Each scene method opens with `self.narrate(...)` and ends by calling what it returned, which pads the scene to the end of its audio. The animations' `run_time`s fit inside the narration's length.

```python
import json
from pathlib import Path

from manim import *

DURATIONS = json.loads(Path("audio/durations.json").read_text())


class Explanation(Scene):
    def construct(self):
        ends = []
        for scene in (self.intro, self.split):
            scene()
            ends.append(self.time - 0.2)
            self.play(*[FadeOut(m) for m in self.mobjects])
        Path("frames.json").write_text(json.dumps(ends))

    def narrate(self, name):
        start = self.time
        self.add_sound(f"audio/{name}.wav")
        return lambda: self.wait(max(0.1, DURATIONS[name] - (self.time - start)))

    def intro(self):
        done = self.narrate("01-intro")
        ...
        done()
```

**Layout** is where agent-made Manim videos fail most — overlapping text, labels cut off at the edge, dead time:

- Keep everything inside the 14.2 × 8 unit frame; `scale_to_fit_width(12)` anything wider.
- Place labels relative to what they label — `next_to`, `arrange`, `to_edge`, each with a `buff`.
- Fade out whatever the next idea does not need before it appears.
- `Text` for words, `MathTypst` for math. LaTeX is not installed, so `Tex` and `MathTex` fail.
- Check a Manim name you are unsure of in the installed version: `<python> -c "import manim; help(manim.<Name>)"`.
- The 3Blue1Brown look: Manim's dark background and colour constants, one highlight colour for the thing that changes.

Done when `scenes.py` has one method per scene, each opening with its own narration.

## 5. Draft and check

Render a low-resolution draft, then pull the frame just before each scene ends, where the most is on screen:

```sh
<manim> -ql scenes.py Explanation
```

```python
import av, json
from pathlib import Path

video = "media/videos/scenes/480p15/Explanation.mp4"
Path("frames").mkdir(exist_ok=True)
for i, t in enumerate(json.loads(Path("frames.json").read_text()), 1):
    with av.open(video) as container:
        stream = container.streams.video[0]
        container.seek(int(t / stream.time_base), stream=stream)
        frame = next(f for f in container.decode(stream) if f.time >= t)
        frame.to_image().save(f"frames/{i:02}.png")
```

Look at every frame: text overlapping, cut off, or too small to read, and any scene that ends on an empty screen. Fix `scenes.py` and draft again, for at most two rounds of fixes. Whatever still looks off after that, name it at hand-over.

Done when every frame is clean, or two rounds of fixes have run.

## 6. Final render

```sh
<manim> -qh --fps 30 scenes.py Explanation
```

Copy `media/videos/scenes/1080p30/Explanation.mp4` to `video.mp4`. Delete `media/`, `frames/`, and `frames.json`; they are run scratch. Keep `script.md`, `narration/`, `audio/`, and `scenes.py` for a follow-up, which picks up again at step 3 after a narration edit, or at step 5 after a picture edit.

Done when `video.mp4` exists and only it and the kept files remain in the folder.
