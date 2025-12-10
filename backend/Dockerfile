# Videre Backend Dockerfile
# This image includes all dependencies needed for the Manim-based video generation backend

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Manim, LaTeX, and other tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # LaTeX and fonts (required for Manim)
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    cm-super \
    dvipng \
    # FFmpeg (required for video processing)
    ffmpeg \
    # Build essentials
    build-essential \
    git \
    # Additional utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV for faster Python dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy backend files
COPY pyproject.toml README.md ./
COPY src ./src

# Install Python dependencies
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -e .

# Create directories for outputs and temporary files
RUN mkdir -p /app/output /app/tmp /app/media/videos /app/media/voiceovers

# Expose port for FastAPI (if using uvicorn)
EXPOSE 8000

# Default command: start the FastAPI server
CMD ["uvicorn", "videre.main:app", "--host", "0.0.0.0", "--port", "8000"]
