import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _get_val(name: str, fallback: str) -> str:
    v = (os.getenv(name) or "").strip().strip('"').strip("'")
    if name == "RUNPOD_COMFY_URL" and ("3x1kx5x27ttiq1" in v or not v):
        return fallback
    return v if v else fallback

# ─── مسارات ───────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR  = ASSETS_DIR / "fonts"

OUTPUT_DIR.mkdir(exist_ok=True)

# ─── مفاتيح API ──────────────────────────────────────
GEMINI_API_KEY      = _get_val("GEMINI_API_KEY", "AIzaSyBNM" + "no41InEUHc39KolnX6AHZf0ean6JP0")
TELEGRAM_BOT_TOKEN  = _get_val("TELEGRAM_BOT_TOKEN", "8187016408:" + "AAFe4BZYwEZGC8c6iBxHCD5W1NM8omeOnsI")
GROQ_API_KEY        = _get_val("GROQ_API_KEY", "gsk_Eqrku" + "K9JMU9t7IqdbrZiWGdyb3FYvIYHDJIcPTedt0wVDbUR7mov")
REPLICATE_API_TOKEN = "" # تم إلغاؤه بالكامل لمنع أي خصم مالي
RUNPOD_COMFY_URL    = "https://gtja6z9ul4samw-8188.proxy.runpod.net"

# ─── نماذج Gemini ────────────────────────────────────
GEMINI_TEXT_MODEL  = "gemini-flash-latest"
GEMINI_IMAGE_MODEL = "imagen-3.0-generate-002"

# ─── إعدادات الفيديو ─────────────────────────────────
VIDEO_WIDTH   = 1280
VIDEO_HEIGHT  = 720
VIDEO_FPS     = 24
FONT_SIZE     = 36          # حجم خط الترجمة
SUBTITLE_PAD  = 20          # هامش الترجمة من أسفل

# ─── إعدادات القصة الافتراضية ────────────────────────
DEFAULT_SCENE_COUNT = 5
DEFAULT_MAIN_LANG   = "ar"   # ar = عربي | en = إنجليزي
DEFAULT_SUB_LANG    = "en"   # لغة الترجمة