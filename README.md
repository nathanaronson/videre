# Videre - HackPrinceton 2025

AI-powered video generation platform using Manim animations and ElevenLabs.

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

## Installation

### LaTeX for Manim

**Install TinyTeX**:

```bash
curl -sL "https://yihui.org/tinytex/install-bin-unix.sh" | sh
```

**Use `tlmgr` to install the necessary packages**:

```bash
tlmgr install \
  amsmath babel-english cbfonts-fd cm-super count1to ctex doublestroke dvisvgm everysel \
  fontspec frcursive fundus-calligra gnu-freefont jknapltx latex-bin mathastext microtype multitoc \
  physics preview prelim2e ragged2e relsize rsfs setspace standalone tipa wasy wasysym xcolor xetex xkeyval
```

**Create Symbolic Links (Optional)**:

For binaries like `dvisvgm`, you may need a symlink to make them accessible system-wide:

```bash
# Replace [username] with your macOS username and [binary_name] with the executable
ln -s /Users/[username]/Library/TinyTeX/bin/universal-darwin/[binary_name] /usr/local/bin/[binary_name]
```

> This step is optional if the binary is already in your PATH.

### MongoDB

```bash
brew tap mongodb/brew
brew install mongodb-community
```
