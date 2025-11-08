# Videre - HackPrinceton 2025

AI-powered video generation platform using Dedalus LLM, Manim animations, and ElevenLabs text-to-speech.

## Quick Start

### Using Just (Recommended)

```bash
# Setup everything
just setup

# Run both frontend and backend
just dev

# See all available commands
just --list
```

### Manual Setup

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on `http://localhost:5173`

**Backend:**
```bash
cd backend
uv pip install -e .
cp .env.example .env
# Edit .env with your API keys
flask --app videre.app run --debug
```
Backend runs on `http://localhost:5000`

## Technologies

**Frontend:**
- React + TypeScript
- Vite
- Tailwind CSS

**Backend:**
- Python 3.12+
- Flask
- Dedalus (LLM)
- Manim (Video generation)
- ElevenLabs (Text-to-speech)

## Development

Common commands:
- `just dev` - Run frontend + backend dev servers
- `just lint` - Lint all code
- `just clean` - Clean build artifacts

See `Justfile` for all available commands or run `just --list`

For detailed setup instructions, see README files in `frontend/` and `backend/`.
