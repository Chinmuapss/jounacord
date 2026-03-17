# Voice Translator App (Supabase)

Simple web app where users can:
- Sign up / log in with Supabase Auth
- Record speech (browser speech recognition)
- Translate transcript to another language
- Save transcript + translation in Supabase
- See only their own saved history after login

## 1) Setup Supabase

1. Create a new Supabase project.
2. In the Supabase SQL editor, run `supabase/schema.sql`.
3. Copy `config.example.js` to `config.js` and fill in your project values:

```bash
cp config.example.js config.js
```

## 2) Run locally

Use any static web server. Example:

```bash
python3 -m http.server 4173
```

Open: `http://localhost:4173`

## Notes

- This app uses browser `SpeechRecognition` (`webkitSpeechRecognition` fallback). Chrome-based browsers work best.
- Translation uses the MyMemory free translation API for demo purposes.
- Data persistence safety comes from Supabase Auth + Row Level Security policies in `supabase/schema.sql`, so each logged-in user only sees their own entries.

## 3) Streamlit Coding Learning Hub

A standalone Streamlit app is included at `streamlit_app.py`.

Features:
- Login + sign-up
- 6 technologies: Python, Java, C++, JavaScript, Go, Rust
- Dashboard with completion + accuracy stats
- Quiz engine with **100 questions per language** (no repeated questions for a user)
- Cheat sheets and special interactive modes (daily challenge, lightning round, notes)
- Persistent progress using local SQLite (`learning_hub.db`)

Run it with:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
