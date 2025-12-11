import ast
import asyncio
import os
import re
import subprocess
import tempfile
import uuid
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from .fetch_context7_docs import fetch_context7_docs


def validate_python_syntax(code: str) -> tuple[bool, str | None]:
    """Validate Python code syntax. Returns (is_valid, error_message)."""
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"


def clean_manim_code(code: str) -> str:
    """Clean up markdown and extra formatting from generated code."""
    code = code.strip()
    code = re.sub(r"^```(?:python)?", "", code, flags=re.MULTILINE).strip()
    code = re.sub(r"```$", "", code, flags=re.MULTILINE).strip()
    return code

async def generate_video_with_gtts(topic, event_callback=None):
    # Generate UUID for this video
    video_uuid = str(uuid.uuid4())
    scene_class_name = f"Scene_{video_uuid.replace('-', '_')}"  # Python class names can't have hyphens

    # Load environment variables
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

    # Configure Gemini
    genai.configure(api_key=GEMINI_API_KEY)

    try:
        context7_docs = await fetch_context7_docs()
    except Exception as e:
        print(f"Warning: could not fetch Context7 docs: {e}")
        context7_docs = "No context available (fallback)."

    max_tokens = 4096

    prompt = f"""

    use library /manimcommunity/manim-voiceover

    Use Context7’s live docs to ensure correctness:

    {context7_docs}

    You are an expert educator and Manim animator. 
    Given the topic: "{topic}", generate **one complete, end-to-end script and runnable Manim code** that teaches this concept visually. Follow these rules:

    1. Create a **clear, step-by-step 15-second script** (~40-50 words) for GTTS narration.
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
        import os
        from manim import *
        from manim_voiceover import VoiceoverScene
        from manim_voiceover.services.elevenlabs import ElevenLabsService
        from dotenv import load_dotenv

        load_dotenv()
        ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
    9. For the speech service service, use voice_id: TVtDNgumMv4lb9zzFzA2
    10. Define a class `{scene_class_name}(VoiceoverScene)` with construct() containing all animations.
    11. The code must be **standalone and directly runnable**, producing an MP4 with synced voiceover.
    12. **Do not summarize, generalize, or skip steps.** Every step of the example must be concrete.

    Return **only the Python code**, starting with `import os`, no explanations, no markdown, no extra text.
    """

    print("Generating highly specific Manim code + voiceover...")

    model = genai.GenerativeModel("gemini-2.5-flash")
    project_root = Path(__file__).parent.parent.parent

    # Retry loop for syntax AND runtime errors (up to 3 attempts)
    max_retries = 3
    manim_code = None
    last_error = None
    error_type = None  # "syntax" or "runtime"

    for attempt in range(1, max_retries + 1):
        print(f"Generation attempt {attempt}/{max_retries}...")

        if attempt == 1:
            current_prompt = prompt
        else:
            # Ask the model to fix the error
            error_description = "syntax error" if error_type == "syntax" else "runtime error"
            current_prompt = f"""
The following Python code has a {error_description}:

```python
{manim_code}
```

Error: {last_error}

Please fix the {error_description} and return the corrected, complete Python code.
Make sure to:
- Fix the specific error mentioned above
- Keep all imports and the class structure intact
- Ensure all Manim objects and methods are used correctly

Return **only the Python code**, no explanations, no markdown backticks.
"""

        response = await model.generate_content_async(current_prompt)
        manim_code = clean_manim_code(response.text)

        # Step 1: Validate syntax
        is_valid, syntax_error = validate_python_syntax(manim_code)

        if not is_valid:
            last_error = syntax_error
            error_type = "syntax"
            print(f"Syntax error on attempt {attempt}: {syntax_error}")
            if event_callback:
                await event_callback("video_generation_retry", {
                    "message": f"Fixing syntax error (attempt {attempt}/{max_retries})...",
                    "error": syntax_error
                })
            continue

        print(f"Syntax validation passed on attempt {attempt}")

        # Step 2: Try running Manim
        if event_callback:
            await event_callback("video_generation_manim_generated", {"message": f"Manim code generated (attempt {attempt}). Rendering..."})

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
            await event_callback("video_generation_status", {
                "message": "Rendering video with Manim (this may take a minute)..."
            })

        try:
            # Run Manim using uv from project root (using async subprocess)
            process = await asyncio.create_subprocess_exec(
                "uv", "run", "manim", "-qh", str(manim_file), scene_class_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(project_root),
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                # Extract the error from stderr
                stderr_text = stderr.decode()
                # Try to get the most relevant error line
                runtime_error = _extract_python_error(stderr_text)
                raise subprocess.CalledProcessError(
                    process.returncode,
                    ["uv", "run", "manim", "-qh", str(manim_file), scene_class_name],
                    stdout.decode(),
                    runtime_error
                )

            # Success!
            print("Manim run complete.")

            if event_callback:
                await event_callback("video_generation_rendering_complete", {"message": "Video rendering complete!"})
            print(stdout.decode())
            if stderr:
                print("STDERR:")
                print(stderr.decode())

            print(f"Video should be saved as: {scene_class_name}.mp4")
            print(f"Video UUID: {video_uuid}")

            return video_uuid, scene_class_name

        except subprocess.CalledProcessError as e:
            last_error = e.stderr if e.stderr else str(e)
            error_type = "runtime"
            print(f"Runtime error on attempt {attempt}: {last_error}")
            if event_callback:
                await event_callback("video_generation_retry", {
                    "message": f"Fixing runtime error (attempt {attempt}/{max_retries})...",
                    "error": last_error
                })
            # Continue to next attempt

    # All attempts failed
    print(f"Failed to generate valid code after {max_retries} attempts")
    if event_callback:
        await event_callback("error", {
            "message": f"Failed after {max_retries} attempts: {last_error}",
            "error_type": error_type,
            "error": last_error
        })
    return None, None


def _extract_python_error(stderr: str) -> str:
    """Extract the most relevant Python error from stderr output."""
    lines = stderr.strip().split('\n')

    # Look for common Python error patterns
    error_lines = []
    capture = False
    for line in lines:
        # Start capturing at Traceback
        if 'Traceback (most recent call last):' in line:
            capture = True
            error_lines = [line]
        elif capture:
            error_lines.append(line)

    if error_lines:
        # Return last few lines which usually contain the actual error
        return '\n'.join(error_lines[-10:])

    # Fallback: return last 500 chars
    return stderr[-500:] if len(stderr) > 500 else stderr
