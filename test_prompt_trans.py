import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from config import GEMINI_API_KEY
from google import genai

def translate_and_enhance_prompt(arabic_text: str) -> str:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = (
            f"You are an expert prompt engineer. Convert this Arabic cartoon idea into an English prompt for 3D Pixar cartoon style: '{arabic_text}'. "
            "Output ONLY the final English prompt, no quotes, no markdown, no other words."
        )
        resp = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
        text = resp.text.strip().strip('"').strip("'").strip("`").strip("*")
        if ":" in text and len(text.split(":")[0]) < 30:
            text = text.split(":", 1)[1].strip().strip('"').strip("*")
        return text
    except Exception as e:
        print("Translation error:", e)
        return arabic_text

for test in ["تنين", "تنين صغير وبومة", "سيارة سباق كارتونية", "قطة صغيرة"]:
    print(test, "->", translate_and_enhance_prompt(test))
