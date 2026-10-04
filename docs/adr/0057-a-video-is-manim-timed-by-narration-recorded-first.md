# A video is Manim, timed by narration recorded first

`/explain` builds a video with Manim Community Edition. The agent writes each scene as Python, and each scene's narration is recorded first, so the length of that audio sets how long the scene runs. The voice comes from xAI's text-to-speech when `XAI_API_KEY` is set. Without the key, it comes from Kokoro, which runs on the user's own machine. Manim is the library behind 3Blue1Brown's videos, and it renders from a script with no editor. Every agent-built explainer pipeline we found uses it. Recording the narration first means the picture waits for the voice, so the two never drift apart.

## Considered options

- **Remotion** — free only for individuals, non-profits, and companies of up to three people. Larger companies pay per seat or per render. Its support for math and diagrams is also weaker than Manim's.
- **Motion Canvas** — renders through its own editor, so an agent working from a shell cannot drive it well.
- **Recording an HTML animation in a headless browser** — gives full freedom, but the skill would have to carry its own code for stepping through frames and encoding them.
- **manim-voiceover** — syncs Manim to narration, but its ElevenLabs support is pinned to a years-old SDK, and it needs the SoX tool. Recording narration first does the same job with one small script.
- **ElevenLabs as the paid voice** — the post that inspired `/explain` names it. The owner uses xAI, and one paid voice keeps the narration script small.
- **Piper as the local voice** — several of its popular voices forbid commercial use. Kokoro's licences allow it.

## Consequences

- On Linux and macOS, Manim needs the Cairo and Pango libraries from the system. The skill gives the user the one command that installs them. Everything else goes into one environment in the user's cache folder, which later runs reuse.
- Math is typeset with Typst, so no LaTeX install is needed.
- espeak-ng, which Kokoro uses, ignores a data path of 160 characters or more. The narration script works around this with a short copy of the data.
