"""Generate Official Character Design Sheet for Zoomy & Bazzouz."""
import sys
import io
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.gemini_tool import get_gemini_client
from google.genai import types

CHAR_DIR = PROJECT_ROOT / "assets" / "characters"
CHAR_DIR.mkdir(parents=True, exist_ok=True)

def generate_official_character_sheet():
    client = get_gemini_client()
    
    prompt = (
        "Official 3D CGI Animation Character Design Sheet, Pixar and Larva slapstick cartoon style. "
        "Two main original insect characters posing together in an underground city street sewer gutter: "
        "1. ZOOMY (on the ground): a super cute, goofy cartoon cockroach with warm shiny golden-amber vinyl shell, "
        "huge round bulging cartoon googly eyes, two long springy flexible antennae, silly wide grin, six tiny adorable legs. "
        "2. BAZZOUZ (hovering beside him): a chubby spherical fat cartoon fly with iridescent metallic sapphire-blue body, "
        "tiny translucent buzzing wings, big expressive magenta-red goggle eyes, hilarious cranky pout expression. "
        "Setting: underground concrete storm drain under a metal street grate with shafts of golden daylight, "
        "giant discarded soda bottle caps, tin can, lush green moss on damp concrete. "
        "Octane 3D render, raytracing, vibrant saturated colors, crisp studio lighting, 8k resolution, cinematic widescreen."
    )
    
    out_path = CHAR_DIR / "zoomy_and_bazzouz_sheet.png"
    print("🎨 جاري رسم لوحة تصميم الشخصيات الرسمية (زوومي وبزّوز)...")
    
    response = client.models.generate_content(
        model="gemini-3.1-flash-image",
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
    )
    
    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            out_path.write_bytes(part.inline_data.data)
            print(f"✅ تم حفظ لوحة الشخصيات بنجاح: {out_path} ({len(part.inline_data.data)//1024} KB)")
            return out_path
            
    raise RuntimeError("Failed to generate character design sheet.")

if __name__ == "__main__":
    generate_official_character_sheet()
