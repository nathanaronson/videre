import os
import subprocess
import tempfile
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

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
- Use manim-voiceover with the set_speech_service method to integrate narration
- Create a Scene class called GeneratedScene that extends VoiceoverScene
- Use self.set_speech_service() at the beginning of construct() - you can use any service (e.g., GTTSService, ElevenLabsService if API key available)
- Break the script into logical segments using with self.voiceover(text=...) blocks
- For each voiceover block, create relevant animations that visualize the concepts
- Use Manim objects like Text, MathTex, shapes, graphs, arrows, etc. to illustrate ideas
- Make animations smooth and well-paced to match the narration
- Include visual transitions and effects where appropriate
- The code should be complete and runnable

Return ONLY the Python code, no explanations or markdown formatting. The code should start with imports.
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
    # Run manim to generate the video
    result = subprocess.run(
        ["manim", str(manim_file), "GeneratedScene", "-ql"],
        capture_output=True,
        text=True,
        check=True
    )

    print("MANIM OUTPUT:")
    print(result.stdout)

    # Find the generated video
    output_dir = Path(temp_dir) / "media" / "videos" / "generated_scene" / "480p15"
    video_files = list(output_dir.glob("*.mp4"))

    if video_files:
        video_path = video_files[0]
        final_path = Path.cwd() / f"{topic.replace(' ', '_')}_video.mp4"

        # Copy to current directory
        import shutil
        shutil.copy(video_path, final_path)

        print(f"\n{'=' * 60}")
        print(f"SUCCESS! Video generated at: {final_path}")
        print(f"{'=' * 60}")
    else:
        print("Warning: Could not find generated video file")

except subprocess.CalledProcessError as e:
    print(f"Error running Manim: {e}")
    print(f"STDOUT: {e.stdout}")
    print(f"STDERR: {e.stderr}")
except Exception as e:
    print(f"Error: {e}")
