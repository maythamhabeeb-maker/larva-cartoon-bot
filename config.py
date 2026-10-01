"""إعدادات المشروع المركزية."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─── مسارات ───────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR  = ASSETS_DIR / "fonts"

OUTPUT_DIR.mkdir(exist_ok=True)

# ─── مفاتيح API ──────────────────────────────────────
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY", "")
TELEGRAM_BOT_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN", "")

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