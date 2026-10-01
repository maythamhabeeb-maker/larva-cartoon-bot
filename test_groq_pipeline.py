from pathlib import Path
from tools.gemini_tool import generate_json, generate_cartoon_image

print("1. Testing Groq JSON...")
res = generate_json('{"name": "test", "characters": ["lion", "cub"]}')
print("   Groq result:", res)

print("2. Testing 3D Cartoon image generation...")
out = Path("output/test_groq_lion.png")
img = generate_cartoon_image("cute baby lion wearing a tiny crown in a golden magical jungle", out, 0)
print(f"   Image Generated OK: {img.name} ({img.stat().st_size // 1024} KB)")
print("ALL TESTS PASSED!")
