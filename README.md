# ✦ Synth.Human

**AI-Powered UGC Video Generator**

Turn any product image into viral influencer content in minutes. No actors. No studio. Just upload.

![Synth.Human](https://img.shields.io/badge/Synth.Human-AI%20UGC-8b5cf6?style=for-the-badge)

---

## 🚀 Quick Start

### Option 1: Run Locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/synth-human.git
cd synth-human

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Option 2: Deploy to Streamlit Cloud (Free)

1. Fork this repository to your GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your forked repo
5. Set the main file path to `app.py`
6. Click "Deploy"

Your app will be live at: `https://YOUR-APP-NAME.streamlit.app`

---

## 🔑 API Keys Required

Users need to provide their own API keys:

| Service | Purpose | Get Key |
|---------|---------|---------|
| **fal.ai** | Image & video generation | [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys) |
| **OpenAI** | LLM (option 1) | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| **Anthropic** | LLM (option 2) | [console.anthropic.com](https://console.anthropic.com/) |
| **Google** | LLM (option 3) | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |

---

## 💰 Cost Per Video

Approximately **$1.70** per video:

| Service | Cost |
|---------|------|
| LLM calls (4 nodes) | ~$0.05 |
| Character image | $0.15 |
| First frame | $0.15 |
| Last frame | $0.15 |
| 8-second video with audio | $1.20 |

---

## 🎬 How It Works

1. **Upload** — Drop in your product image
2. **Configure** — Set product name, tone, and targeting
3. **Generate** — AI creates persona, character, frames, and video
4. **Download** — Get your viral-ready UGC video

### The Pipeline

```
Product Image
     ↓
┌─────────────────┐
│ Persona Inference│ → Who would buy this? What's their vibe?
└────────┬────────┘
         ↓
┌─────────────────┐
│ Character Builder│ → Create a photorealistic influencer
└────────┬────────┘
         ↓
┌─────────────────┐
│ Frame Generation │ → First frame + Last frame
└────────┬────────┘
         ↓
┌─────────────────┐
│  Script Writer   │ → Natural, casual dialogue
└────────┬────────┘
         ↓
┌─────────────────┐
│ Video Generation │ → 8-second video with speech
└────────┬────────┘
         ↓
    UGC Video 🎬
```

---

## ⚙️ Configuration Options

### Tone Presets

| Tone | Style |
|------|-------|
| **Playful** | Humorous, self-aware, "okay the secret is literally this thing..." |
| **Aspirational** | Confident, elevated, subtle flex |
| **Relatable** | Warm, discovery energy, "just like you" |
| **Edgy** | Nonchalant, cool, "idk why everyone sleeps on this" |
| **Wholesome** | Genuine excitement, sharing with friends |

### Advanced Targeting

- Target age range
- Target gender
- Target geography
- Target ethnicity
- Subculture/aesthetic
- Custom script override

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit with custom CSS
- **Image Gen:** Nano Banana Pro (fal.ai)
- **Video Gen:** Veo 3.1 Fast (fal.ai)
- **LLM:** OpenAI / Anthropic / Google (user choice)

---

## 📝 License

MIT License — use it however you want.

---

## 🤝 Contributing

PRs welcome! Feel free to:
- Improve the prompts
- Add new tone presets
- Enhance the UI
- Fix bugs

---

<p align="center">
  <strong>✦ Synth.Human</strong><br>
  <sub>AI-Powered UGC Generation</sub>
</p>
