import os
import subprocess
import tempfile
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

client = Anthropic(api_key=api_key)

topic = input("Enter a topic you'd like to learn about: ").strip()

prompt = f"""
You are an expert educator and scriptwriter for visual learning videos.
Create a clear and engaging **1-minute script** that teaches the topic: "{topic}".

Guidelines:
- Tone: engaging, conversational, and educational — suitable for narration with ElevenLabs.
- Visuals: write in a way that aligns naturally with animations made in Manim.
- Pacing: about 150–180 words (1 minute of spoken audio).
- Structure:
  1. **Hook / introduction** — capture attention and state the key question or curiosity.
  2. **Concept explanation** — define and intuitively explain the topic.
  3. **Visual cues** — naturally include phrases that could inspire animation (e.g., “imagine a curve,” “watch as the points connect”).
  4. **Conclusion** — wrap up with why it matters or a neat insight.

Do **not** include camera directions or scene markup — just the spoken text itself.
Return only the script.
"""

message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="claude-sonnet-4-5-20250929",
)

transcript = message.content[0].text
print("=" * 60)
print("GENERATED TRANSCRIPT:")
print("=" * 60)
print(transcript)
print("=" * 60)

# Step 2: Generate Manim code from the transcript
manim_prompt = f"""
You are an expert in creating Manim animations using the manim-voiceover library.
Given the following educational script, generate Python code that creates an engaging animated video using Manim and manim-voiceover.

Script:
{transcript}

Requirements:
- Start with these exact imports:
  import os
  from manim import *
  from manim_voiceover import VoiceoverScene
  from manim_voiceover.services.elevenlabs import ElevenLabsService
  from dotenv import load_dotenv

  load_dotenv()
  ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

- Create a Scene class called GeneratedScene that extends VoiceoverScene
- In construct(), use: self.set_speech_service(ElevenLabsService(api_key=ELEVEN_API_KEY, voice_id="29vD33N1CtxCmqQRPOHJ"))
- Break the script into logical segments using with self.voiceover(text=...) as tracker: blocks
- For each voiceover block, create relevant animations that visualize the concepts
- Use Manim objects like Text, MathTex, shapes, graphs, arrows, etc. to illustrate ideas
- Make animations smooth and well-paced to match the narration
- Include visual transitions and effects where appropriate
- The code should be complete and runnable as a standalone Python file

Return ONLY the Python code, no explanations, no markdown code blocks, no extra text. Just the raw Python code starting with 'import os'.
"""

print("\nGenerating Manim code...")
manim_message = client.messages.create(
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": manim_prompt,
        }
    ],
    model="claude-sonnet-4-5-20250929",
)

manim_code = manim_message.content[0].text

# Clean up the code if it's wrapped in markdown code blocks
if manim_code.startswith("```python"):
    # Remove ```python from the start and ``` from the end
    manim_code = manim_code.split("```python", 1)[1]
    manim_code = manim_code.rsplit("```", 1)[0]
    manim_code = manim_code.strip()
elif manim_code.startswith("```"):
    # Remove ``` from the start and end
    manim_code = manim_code.split("```", 1)[1]
    manim_code = manim_code.rsplit("```", 1)[0]
    manim_code = manim_code.strip()

print("=" * 60)
print("GENERATED MANIM CODE:")
print("=" * 60)
print(manim_code)
print("=" * 60)

# Step 3: Execute the Manim code to generate the MP4
print("\nSaving Manim code to temporary file...")
temp_dir = tempfile.mkdtemp()
manim_file = Path(temp_dir) / "generated_scene.py"

with open(manim_file, "w") as f:
    f.write(manim_code)

print(f"Manim code saved to: {manim_file}")
print("\nExecuting Manim to generate video...")

try:
    # Run manim to generate the video using uv with high quality and preview
    # Use the project root directory for execution (where pyproject.toml is)
    project_root = Path(__file__).parent.parent.parent

    print(f"Running from project root: {project_root}")
    print(f"Executing: uv run manim -pqh {manim_file} GeneratedScene")

    result = subprocess.run(
        ["uv", "run", "manim", "-pqh", str(manim_file), "GeneratedScene"],
        capture_output=True,
        text=True,
        check=True,
        cwd=str(project_root)
    )

    print("MANIM OUTPUT:")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    # Find the generated video (high quality is 1080p60)
    output_dir = Path(temp_dir) / "media" / "videos" / "generated_scene" / "1080p60"
    video_files = list(output_dir.glob("*.mp4"))

    if video_files:
        video_path = video_files[0]
        # Save to backend/src/examples directory
        output_location = Path(__file__).parent
        final_path = output_location / f"{topic.replace(' ', '_')}_video.mp4"

        # Copy to examples directory
        import shutil
        shutil.copy(video_path, final_path)

        print(f"\n{'=' * 60}")
        print(f"SUCCESS! Video generated at: {final_path}")
        print(f"{'=' * 60}")
    else:
        print("Warning: Could not find generated video file")
        print(f"Searched in: {output_dir}")
        # List what's actually in the media directory
        media_dir = Path(temp_dir) / "media"
        if media_dir.exists():
            print(f"\nContents of media directory:")
            for item in media_dir.rglob("*"):
                print(f"  {item}")

except subprocess.CalledProcessError as e:
    print(f"Error running Manim: {e}")
    print(f"STDOUT: {e.stdout}")
    print(f"STDERR: {e.stderr}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
