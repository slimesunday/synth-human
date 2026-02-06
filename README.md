# ✦ Synth.Human

AI-generated UGC that doesn't look like AI-generated UGC.

Upload a product.  
Get an influencer video.  
Vertical. iPhone energy. Ready to post.

---

## What this is

A pipeline for short-form UGC that passes.

Just: *looks like someone filmed this in their apartment.*

The whole system exists to solve the stuff generators get wrong:

- product scale (why is that shoe the size of a torso)
- identity drift (why did her face change)
- room logic (why is the wall suddenly different)
- tone (why does she sound like a robot)

---

## Quick start

```bash
git clone https://github.com/slimesunday/synth-human.git
cd synth-human
pip install -r requirements.txt
streamlit run app.py
```

Or deploy free on [Streamlit Cloud](https://share.streamlit.io).  
Fork → Connect → `app.py` → Done.

---

## API keys

You bring your own.

| Service | What it does |
|---------|--------------|
| fal.ai | Image + video gen |
| OpenAI / Anthropic / Google | LLM (pick one) |

Nothing stored: Your keys, your bill.

---

## Cost

~$1.70 per video.

That covers:
- persona inference
- character generation  
- first + last frame
- 8s video with speech

Bad prompts cost more. Retries add up.  
This repo exists to reduce retries.

---

## How it works

```
Product image
     ↓
Persona inference → who would post this
     ↓
Character gen → what they look like
     ↓
Keyframes → first + last frame anchors
     ↓
Script → 4-5 lines, filler words included
     ↓
Video → 8s vertical, speech, room tone
```

## Configuration

Control:

- tone
- age / gender / geography
- subculture
- custom script (if you want to override)

### Tone presets

| Tone | Vibe |
|------|------|
| Playful | "okay so the secret is literally this thing" |
| Aspirational | quiet flex, "elevated my routine" |
| Relatable | "finally tried it, I get the hype" |
| Edgy | "idk why everyone sleeps on this" |
| Wholesome | "you guys I had to share" |

---

## Tech

- Streamlit (frontend)
- fal.ai — Nano Banana Pro (images) + Veo 3.1 Fast (video)
- LLM — OpenAI / Anthropic / Google (swappable)

---

## Roadmap

What would matter:
- smarter product-type routing
- automatic failure detection  
- fewer retries
- less prompt bloat

---

## License

Look, don't touch.

---

<p align="center">
  <sub>Synth.Human — because "AI-generated" shouldn't be an insult.</sub>
</p>
