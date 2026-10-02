"""أداة توليد المشاهد الكارتونية بنفس الستايل السحري الخارق (Enchanted Magical Forest 3D Pixar Style)."""
import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger(__name__)

from config import GROQ_API_KEY, GEMINI_API_KEY

_groq_client = None
_gemini_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client

def get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client

def generate_text(prompt: str, temperature: float = 0.7) -> str:
    client = get_groq_client()
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return completion.choices[0].message.content.strip()

def generate_json(prompt: str) -> dict | list:
    client = get_groq_client()
    full_prompt = (
        prompt
        + "\n\nIMPORTANT: Return ONLY valid, raw JSON. Do not wrap in markdown. Start directly with { or [."
    )
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.3,
    )
    raw = completion.choices[0].message.content.strip()

    if "```" in raw:
        for block in raw.split("```"):
            block = block.strip()
            if block.startswith("json"):
                block = block[4:].strip()
            try:
                return json.loads(block)
            except Exception:
                continue

    return json.loads(raw)

def generate_cartoon_image(prompt: str, output_path: Path, scene_index: int = 0) -> Path:
    """توليد صورة بنفس ستايل الغابة السحرية والأسد والثعلب الخارق (Pixar Enchanted Forest)."""
    client = get_gemini_client()
    
    # القالب البصري الدقيق المستوحى من صورتك الأصلية بالمليم:
    master_style_prompt = (
        f"Masterpiece 3D animated scene of {prompt}. "
        "Pixar Disney 3D animation style, extremely detailed fluffy fur on the characters, "
        "enchanted magical fantasy forest background, ancient giant mossy oak tree with hanging glowing lantern lights, "
        "magical glowing yellow fireflies floating in the air, lush vibrant wildflowers and ferns on the ground, "
        "cinematic golden hour warm sunlight rays filtering through tree branches, volumetric rim lighting, "
        "cute expressive facial features, Octane 3D CGI rendering, hyper-detailed, 8k resolution, widescreen 16:9, crystal clear focus"
    )

    logger.info(f"Generating Masterpiece Scene {scene_index+1} with Enchanted 3D Style...")

    response = client.models.generate_content(
        model="gemini-3.1-flash-image",
        contents=master_style_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            output_path.write_bytes(part.inline_data.data)
            logger.info(f"Scene {scene_index+1} saved with exact master style! ({len(part.inline_data.data)//1024} KB)")
            return output_path

    raise RuntimeError("Failed to generate image from Gemini 3.1 Flash Image.")

def generate_larva_image(prompt: str, output_path: Path, shot_index: int = 0) -> Path:
    """توليد لقطة كارتونية ثلاثية الأبعاد بستايل كارتون لارفا الكوميدي (3D Slapstick Larva Style)."""
    client = get_gemini_client()
    
    larva_style_prompt = (
        f"Masterpiece 3D CGI animated slapstick cartoon shot: {prompt}. "
        "Original characters: ZOOMY (a super cute goofy cartoon cockroach with warm shiny golden-amber shell, huge round googly eyes, long flexible springy antennae) "
        "and BAZZOUZ (a chubby round metallic sapphire-blue fat fly with tiny buzzing wings, big magenta-red goggle eyes). "
        "Pixar & Larva slapstick 3D animation style, glossy vinyl textures, hilarious exaggerated comedic facial expressions, "
        "underground city storm drain and sewer gutter setting, metal street grate ceiling with dramatic volumetric sunlight shafts, "
        "damp concrete surfaces with moss, pebbles, discarded giant soda bottle caps, rich ambient occlusion, "
        "Octane 3D render, ultra-vivid colors, slapstick humor, vertical 9:16 mobile composition, 8k resolution, crystal clear focus"
    )

    logger.info(f"Generating 3D Larva Shot {shot_index+1}...")

    response = client.models.generate_content(
        model="gemini-3.1-flash-image",
        contents=larva_style_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            output_path.write_bytes(part.inline_data.data)
            logger.info(f"Shot {shot_index+1} saved with 3D Larva style! ({len(part.inline_data.data)//1024} KB)")
            return output_path

    raise RuntimeError("Failed to generate Larva 3D image from Gemini.")


def generate_universal_character_image(plan: dict, output_path: Path) -> Path:
    """توليد صورة الشخصيات المرجعية ثلاثية الأبعاد لتثبيت هويتهم وملامحهم في جميع المشاهد."""
    client = get_gemini_client()
    
    chars_desc = ". ".join([
        f"{c.get('name_en', c.get('name_ar', 'Character'))}: {c.get('visual_identity', '')}"
        for c in plan.get("characters", [])
    ])
    setting = plan.get("setting_en", "a colorful vibrant 3D animated world")
    
    prompt = (
        f"Masterpiece 3D Pixar character concept reference art: {chars_desc}. "
        f"Characters standing together in {setting}. "
        "Pixar Disney 3D animation style, adorable expressive faces, full body shot, "
        "extremely detailed textures, rich volumetric studio lighting, vibrant cheerful colors, "
        "Octane 3D CGI rendering, 8k resolution, crystal clear focus."
    )

    logger.info("Generating 3D Universal Character Reference Image...")

    for model_name in ["gemini-2.5-flash-image", "gemini-3.1-flash-image"]:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    output_path.write_bytes(part.inline_data.data)
                    logger.info(f"Character reference image saved! ({len(part.inline_data.data)//1024} KB)")
                    return output_path
        except Exception as e:
            logger.warning(f"Model {model_name} failed: {e}")
            continue

    raise RuntimeError("Failed to generate character reference image.")


