# Videre Backend

Flask backend for video generation with Dedalus, Manim, and ElevenLabs.

## Structure

```
src/videre/
├── app.py              # Flask app & routes
├── config.py           # Settings
├── dedalus.py          # LLM client
├── manim_service.py    # Video generation
└── elevenlabs.py       # TTS
```

## Setup

```bash
just install-backend-dev
cp backend/.env.example backend/.env
# Add API keys to .env
just dev-backend
```

Server: `http://localhost:5000`

## Dependencies

- Flask + Flask-CORS
- requests
- pydantic
- python-dotenv
