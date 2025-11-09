import os
import re
import subprocess
import tempfile
import traceback
import uuid
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv


async def generate_video_with_gtts(topic, event_callback=None):
    # Generate UUID for this video
    video_uuid = str(uuid.uuid4())
    scene_class_name = f"Scene_{video_uuid.replace('-', '_')}"  # Python class names can't have hyphens

    # Load environment variables
    load_dotenv()
    API_KEY = os.getenv("ANTHROPIC_API_KEY")
    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

    client = Anthropic(api_key=API_KEY)

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
    
    # if event_callback:
    #     await event_callback("video_generation_status", {"message": "Generating Manim code with AI..."})

    response = client.messages.create(
        max_tokens=max_tokens,
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
        # Run Manim using uv from project root
        project_root = Path(__file__).parent.parent.parent
        result = subprocess.run(
            ["uv", "run", "manim", "-qh", str(manim_file), scene_class_name],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(project_root),
        )
        print("Manim run complete.")
        
        if event_callback:
            await event_callback("video_generation_rendering_complete", {"message": "Video rendering complete!"})
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)

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
