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
