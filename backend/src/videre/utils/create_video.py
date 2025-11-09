import asyncio
import os
import re
import subprocess
import tempfile
import traceback
import uuid
from pathlib import Path

from anthropic import AsyncAnthropic
from dotenv import load_dotenv


async def generate_video_with_gtts(topic, event_callback=None):
    # Generate UUID for this video
    video_uuid = str(uuid.uuid4())
    scene_class_name = f"Scene_{video_uuid.replace('-', '_')}"  # Python class names can't have hyphens

    # Load environment variables
    load_dotenv()
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

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
    7. When writing Manim code, you must follow the exact format:
    Code(
       code_string=\"<your code here>\",
       language="<language>",
    ). Under no circumstances shall you include a parameter for font_size, code, only the exact example above.
    8. Start with these exact imports:
        from manim import *
        from manim_voiceover import VoiceoverScene
        from manim_voiceover.services.gtts import GTTSService
    9. Define a class `{scene_class_name}(VoiceoverScene)` with construct() containing all animations.
    10. The code must be **standalone and directly runnable**, producing an MP4 with synced voiceover.
    11. **Do not summarize, generalize, or skip steps.** Every step of the example must be concrete.

    Return **only the Python code**, starting with `import os`, no explanations, no markdown, no extra text.
    """

    print("Generating highly specific Manim code + voiceover...")

    # Use async Anthropic client for non-blocking API calls
    async_client = AsyncAnthropic(api_key=API_KEY)

    response = await async_client.messages.create(
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
        model="claude-sonnet-4-5-20250929",
    )

    manim_code = response.content[0].text.strip()
    
    if event_callback:
        await event_callback("video_generation_manim_generated", {"message": "Manim code generated. Preparing to render video..."})

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
    
    if event_callback:
        await event_callback("video_generation_status", {"message": "Rendering video with Manim (this may take a minute)..."})

    try:
        # Run Manim using uv from project root (using async subprocess)
        project_root = Path(__file__).parent.parent.parent

        # Use asyncio.create_subprocess_exec for non-blocking execution
        process = await asyncio.create_subprocess_exec(
            "uv", "run", "manim", "-qh", str(manim_file), scene_class_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(project_root),
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode,
                ["uv", "run", "manim", "-qh", str(manim_file), scene_class_name],
                stdout.decode(),
                stderr.decode()
            )

        print("Manim run complete.")

        if event_callback:
            await event_callback("video_generation_rendering_complete", {"message": "Video rendering complete!"})
        print(stdout.decode())
        if stderr:
            print("STDERR:")
            print(stderr.decode())

        # Manim saves the video relative to project_root (where we run it from)
        # The video will be at: project_root / "media" / "videos" / "generated_scene" / "1080p60" / f"{scene_class_name}.mp4"
        print(f"Video should be saved as: {scene_class_name}.mp4")
        print(f"Video UUID: {video_uuid}")

        return video_uuid, scene_class_name

    except subprocess.CalledProcessError as e:
        print(f"Error running Manim: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return None, None
