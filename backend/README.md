# Videre Backend

FastAPI backend for video generation with Dedalus, Manim, and ElevenLabs.

## Structure

```
src/videre/
├── main.py             # FastAPI app & routes
├── claude_client.py    # Claude/Anthropic client
├── integration.py      # Integration logic
└── utils/
    └── send_to_aws.py  # AWS utilities
```

## Setup

```bash
cd backend
uv sync
```

## Running the Server

From the `backend` directory:

```bash
uv run uvicorn videre.main:app --reload --host 0.0.0.0 --port 8000
```

Or from the `backend/src` directory:

```bash
uv run uvicorn videre.main:app --reload --host 0.0.0.0 --port 8000
```

Server: `http://localhost:8000`

## Dependencies

- FastAPI
- uvicorn
- requests
- pydantic
- python-dotenv
- manim
- manim-voiceover
