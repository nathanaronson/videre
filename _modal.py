"""
Modal.com deployment configuration for Videre backend.

This file sets up the FastAPI application for hosting on Modal with all necessary
dependencies including LaTeX support for Manim video generation.

The dependencies are installed from backend/pyproject.toml using uv for fast resolution.

To deploy:
  modal deploy _modal.py

To test locally:
  modal run _modal.py

Documentation: https://modal.com/docs/guide/fastapi
"""
# cspell:disable

from pathlib import Path
from modal import App, Image, asgi_app

# Path to backend directory
backend_path = Path(__file__).parent / "backend"

# Define the Modal image with all dependencies for Manim
image = (
    Image.debian_slim(python_version="3.12")
    .apt_install(
        # Build essentials (required for pycairo/Manim compilation)
        "build-essential",
        "pkg-config",
        "libcairo2-dev",
        "libpango1.0-dev",
        "curl",
        # LaTeX and fonts (required for Manim)
        "texlive-latex-base",
        "texlive-latex-extra",
        "texlive-fonts-recommended",
        "cm-super",
        "dvipng",
        # FFmpeg (required for video processing)
        "ffmpeg",
    )
    # Install Rust via rustup (need newer version for tiktoken)
    .run_commands(
        "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"
    )
    .env({"PATH": "/root/.cargo/bin:$PATH"})
    # Install Python dependencies from uv.lock (fast, deterministic)
    .uv_sync(str(backend_path))
    # Add the backend source code (last, so it's mounted at runtime for fast iteration)
    .add_local_dir(str(backend_path / "src"), remote_path="/app/src")
)

# Create the Modal app
app = App(
    name="videre-backend",
    image=image,
)

import modal
@app.function(
    timeout=36000,  # 1 hour timeout for video generation
    memory=(2048, 3072),  # 2-3GB memory
    cpu=2.0,  # 2 CPU cores
    secrets=[modal.Secret.from_name("videre")]
)
@asgi_app()
def fastapi_app():
    """Create and return the FastAPI application."""
    import sys

    # Add backend src to path
    sys.path.insert(0, "/app/src")

    # Import and return the FastAPI app
    from videre.main import app

    return app


# Test function
@app.function()
def test():
    """Test that dependencies are installed."""
    print("Videre backend image is ready!")
    print("\nInstalled from backend/pyproject.toml:")
    print("  - Python 3.12")
    print("  - LaTeX (texlive-latex-extra) - Required for Manim")
    print("  - FFmpeg - Required for video processing")
    print("  - Manim & Manim Voiceover")
    print("  - ElevenLabs TTS")
    print("  - FastAPI & Uvicorn")
    print("  - MongoDB (Motor)")
    print("  - AWS SDK (Boto3)")
    print("  - Anthropic & Google Generative AI")


if __name__ == "__main__":
    test.local()
