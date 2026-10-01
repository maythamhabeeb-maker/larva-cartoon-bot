"""AI Cartoon Studio - بوت تيليجرام لإنتاج كارتون لارفا الكوميدي الصامت ثلاثي الأبعاد مع المؤثرات الصوتية الكاملة."""
import sys
import io
import asyncio
import logging
from pathlib import Path

# إعداد UTF-8 للكونسول في ويندوز
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TELEGRAM_BOT_TOKEN
from pipeline import slapstick_pipeline

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🎥 توليد حلقة فيديو 3D متحركة")],
        [KeyboardButton("💡 اكتب أي فكرة من عندك"), KeyboardButton("ℹ️ عن الشخصيات")]
    ],
    resize_keyboard=True
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎬✨ **أهلاً بك في استوديو الرسوم المتحركة الكوميدية (زوومي وبزّوز - Slapstick Studio)!**\n\n"
        "أبطال سلسلتنا الحصرية الخاصة بينا:\n"
        "🪳 **زوومي (Zoomy):** الصرصور الذهبي الأهبل والفضولي وعاشق الأكل.\n"
        "🪰 **بزّوز (Bazzouz):** الذبابة الزرقاء الدبدوبة والعصبية مع نظاراتها الحمر.\n\n"
        "⭐ **كوميديا صامتة 100% بدون أي كلام** (عالمية تناسب الجميع).\n"
        "⭐ **مؤثرات صوتية كارتونية مضحكة** (Boing, Splat, Bonk, Whistle).\n"
        "⭐ **مونتاج خاطف وسريع عمودي (9:16)** جاهز للريلز وتيك توك وشورتس.\n\n"
        "👇 اضغط الزر أدناه لتوليد حلقة مقلب فورية، أو اكتب فكرة من عندك!"
    )
    await update.message.reply_text(welcome_text, reply_markup=MAIN_KEYBOARD, parse_mode="Markdown")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info_text = (
        "ℹ️ **عالم وأبطال السلسلة:**\n\n"
        "📍 **المكان:** فتحة مجاري الشارع تحت الشباك الحديدي بين قواطي البيبسي وأغطية القناني الملونة.\n"
        "🪳 **زوومي:** صرصور سريع وغبي، يركض ويتزحلق ويحب المقالب.\n"
        "🪰 **بزّوز:** ذبابة سمينة زرقاء تطير وتزنّ وتتعصب بسرعة.\n\n"
        "⚡ كل الحلقات سريعة وخاطفة، مع هزات صدمات وزووم كوميدي ومؤثرات صوتية بدون أي كلام!"
    )
    await update.message.reply_text(info_text, reply_markup=MAIN_KEYBOARD, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.strip()
    
    if user_text in ["ℹ️ كيف يعمل النظام؟", "ℹ️ عن الشخصيات والنظام"]:
        await info_command(update, context)
        return
        
    if user_text in ["💡 اكتب فكرة مقلب كارتوني", "💡 اكتب فكرة مقلب من عندك"]:
        await update.message.reply_text(
            "💡 اكتب فكرة المقلب الآن في رسالة (مثلاً: *شجار على حبة فستق*، *علكة لاصقة*، *غطاء بيبسي طائر*)...",
            parse_mode="Markdown"
        )
        return

    # أي برومبت أو رسالة يكتبها المستخدم تولد مباشرة فيديو 3D متحرك بالكامل
    is_random = (user_text in [
        "🐛 حلقة لارفا جديدة (مقلب مضحك)", 
        "🪰🐛 حلقة جديدة: مقلب زوومي وبزّوز",
        "🪰🐛 حلقة زوومي وبزّوز (سريعة وخاطفة)",
        "🎥 فيديو حركة 3D حقيقية (MiniMax Video)",
        "🎥 توليد حلقة فيديو 3D متحركة"
    ])
    idea = None if is_random else user_text
    
    status_msg = await update.message.reply_text("🎬 بدأت عملية توليد **فيديو أنيميشن 3D متحرك بالذكاء الاصطناعي**... دقيقة من فضلك...")

    progress_history = []

    async def update_status(text: str):
        progress_history.append(text)
        current_display = "🎬 **مراحل الإنتاج السينمائي:**\n\n" + "\n".join(progress_history[-5:])
        try:
            await status_msg.edit_text(current_display, parse_mode="Markdown")
        except Exception:
            pass

    loop = asyncio.get_event_loop()

    try:
        from tools.replicate_video_tool import produce_full_motion_slapstick
        video_path = await loop.run_in_executor(
            None,
            lambda: produce_full_motion_slapstick(
                idea=idea,
                on_progress=lambda msg: asyncio.run_coroutine_threadsafe(
                    update_status(msg), loop
                ).result()
            )
        )

        await status_msg.edit_text("✅ اكتمل المونتاج بنجاح! جاري رفع الفيديو الآن إلى تليجرام... 🚀")

        # إرسال الفيديو النهائي
        with open(video_path, "rb") as vf:
            await update.message.reply_video(
                video=vf,
                caption=(
                    f"🎬 **حلقة كارتون لارفا جاهزة!**\n"
                    f"🐛 العنوان: {video_path.stem.replace('_', ' ')}\n\n"
                    "🔊 فيديو كوميدي صامت مع المؤثرات الصوتية والموسيقى الكارتونية بدون أي كلام.\n"
                    "📲 جاهز للنشر والمشاركة فوراً!"
                ),
                supports_streaming=True,
                read_timeout=300,
                write_timeout=300,
            )

    except Exception as e:
        logger.exception("Production error")
        await update.message.reply_text(f"❌ حدث خطأ أثناء الإنتاج:\n{str(e)[:250]}")

def _start_health_check_server():
    """خادم HTTP خفيف في الخلفية لإرضاء فحص Render Web Service."""
    import os
    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK - Larva Bot Alive & Running")

        def log_message(self, format, *args):
            pass

    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        print(f"✅ Health check server listening on port {port} for Render")
    except Exception as e:
        print(f"Health server error: {e}")

def main() -> None:
    _start_health_check_server()

    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN is missing in .env!")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", info_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🚀 Larva 3D Slapstick Studio Telegram Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

