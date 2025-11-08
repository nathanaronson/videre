import os
import subprocess
import tempfile
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv
import re
import shutil
import traceback

# Load environment variables
load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

client = Anthropic(api_key=API_KEY)

# Get topic from user
topic = input("Enter a topic you'd like to learn about: ").strip()

# Stronger, more concrete prompt
prompt = f"""
You are an expert educator and Manim animator. 
Given the topic: "{topic}", generate **one complete, end-to-end script and runnable Manim code** that teaches this concept visually. Follow these rules:

1. Create a **clear, step-by-step 1-minute script** (~150–180 words) for GTTS narration.
2. The narration must include **specific examples, concrete values, and reasoning**. 
   - For instance, if explaining a graph traversal: "We visit node A first because its distance 3 is the smallest among neighbors. Then we go to node B with distance 5..." 
   - The script should explicitly describe every step, value, and choice.
3. Immediately generate **complete, runnable Python code** using Manim + manim-voiceover that visualizes each step.
4. Visuals must exactly match the narration: animate nodes, arrows, numbers, highlighting choices, distances, and transitions.
5. Break the narration into voiceover blocks using `with self.voiceover(text=...) as tracker:` and include the corresponding animations in each block.
6. Use dynamic, light, and visually appealing effects: shapes, colors, MathTex, arrows, graphs, smooth transitions.
7. Start with these exact imports:
    from manim import *
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.gtts import GTTSService
8. Define a class `GeneratedScene(VoiceoverScene)` with construct() containing all animations.
9. The code must be **standalone and directly runnable**, producing an MP4 with synced voiceover.
10. **Do not summarize, generalize, or skip steps.** Every step of the example must be concrete.

Return **only the Python code**, starting with `import os`, no explanations, no markdown, no extra text.
"""

print("Generating highly specific Manim code + voiceover...")
response = client.messages.create(
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}],
    model="claude-sonnet-4-5-20250929",
)

manim_code = response.content[0].text.strip()

# Robust cleanup of any markdown backticks or language hints
manim_code = re.sub(r"^```(python)?\s*", "", manim_code)
manim_code = re.sub(r"\s*```$", "", manim_code)

print("=" * 60)
print("GENERATED MANIM CODE:")
print("=" * 60)
print(manim_code)
print("=" * 60)

# Save Manim code to a temporary file
temp_dir = tempfile.mkdtemp()
manim_file = Path(temp_dir) / "generated_scene.py"
with open(manim_file, "w") as f:
    f.write(manim_code)

print(f"Saved Manim code to temporary file: {manim_file}")

try:
    # Run Manim using uv from project root
    project_root = Path(__file__).parent.parent.parent
    result = subprocess.run(
        ["uv", "run", "manim", "-pqh", str(manim_file), "GeneratedScene"],
        capture_output=True,
        text=True,
        check=True,
        cwd=str(project_root),
    )
    print("Manim run complete.")
    print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)

    # Move the generated video to examples directory
    output_dir = Path(temp_dir) / "media" / "videos" / "generated_scene" / "1080p60"
    video_files = list(output_dir.glob("*.mp4"))
    if video_files:
        video_path = video_files[0]
        final_path = Path(__file__).parent / f"{topic.replace(' ', '_')}_video.mp4"
        shutil.copy(video_path, final_path)
        print(f"SUCCESS! Video generated at: {final_path}")
    else:
        print("Warning: Could not find generated video file.")
        if output_dir.exists():
            print(f"Contents of {output_dir}:")
            for f in output_dir.iterdir():
                print(f"  {f}")

except subprocess.CalledProcessError as e:
    print(f"Error running Manim: {e}")
    print(f"STDOUT: {e.stdout}")
    print(f"STDERR: {e.stderr}")
except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()
