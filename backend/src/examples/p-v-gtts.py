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
max_tokens = 4096

prompt = f"""
use library /manimcommunity/manim-voiceover

You are an expert educator and Manim animator.

Use Context7’s live docs to ensure correctness.
Generate complete Manim Voiceover code for "{topic}"...

Given the topic: "{topic}", generate **one complete, end-to-end script and runnable Manim code** that teaches this concept visually. Follow these rules:

0. Videos must have constant nonstop animation, with corresponding text to speech in exactly 60 seconds. 
   - There should be action at every second of the 60 seconds, either in the form of animation or speech or both.
1. Create a **clear, step-by-step 60 second script** for GTTS.
   - Ensure script and code is produced so that it fits the maximum tokens allowed: {max_tokens}.
2. The narration must start with **defining definitions, then describe procedure, then demonstrating concrete examples with reasoning, then conclude.**. 
   - For instance, if explaining a graph traversal: "Graph traversal is [definition]. First, visit node 'A' because [reasoning]. Then, we go to node B because [reasoning].." 
   - The script should explicitly describe every step, reasoning, and choice.
3. Immediately generate **complete, runnable Python code** using Manim + manim-voiceover that visualizes each step corresponding to the script.
    - There must be no blank spaces within the video with no animations or speech.
    - Do not add visuals in safe areas or outside of canvas restrictions (writing stays centralized and intuitive).
4. Visuals must exactly match the narration: animate nodes, arrows for pointers, colors, numbers, matrices, highlighting choices, distances, and transitions.
    - Visuals such as numbers and symbols should not be written over.
    - Include proper signs ('=', '+', etc.) and symbols for the topic.
5. Break the narration into voiceover blocks using `with self.voiceover(text=...) as tracker:` and include the corresponding animations in each block.
6. Use dynamic, light, and visually appealing effects: shapes, colors, MathTex, arrows, graphs, smooth transitions.
7. Start with these exact imports:
    from manim import *
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.gtts import GTTSService
8. Define a class `GeneratedScene(VoiceoverScene)` with construct() containing all animations.
9. The code must be **standalone and directly runnable**, producing an MP4 with synced voiceover.
10. **Do not summarize, generalize, or skip steps.** Every step of the example must be concrete.
11. A beginner to the topic should fully understand all key topics, procedures, and solutions after watching the produced video animation and script.
13. Remember, you are creating two separate things: a text script with proper punctuation, and Manim python code with proper python syntax.
14. Only values of type VMobject can be added as submobjects of VGroup, but the value Mobject (at index 0 of parameter 9) is of type Mobject. You can try adding this value into a Group instead.

Return **only the Python code**, starting with `import os`, no explanations, no markdown, no extra text.
"""

print("Generating highly specific Manim code + voiceover...")
response = client.messages.create(
    max_tokens=max_tokens,
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
