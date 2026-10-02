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
        [KeyboardButton("🐛 كارتون ومقالب لارفا 3D"), KeyboardButton("🎬 فيديو سينمائي واقعي (Cinematic)")],
        [KeyboardButton("🐱 كارتون حيوانات وأبطال بيكسار"), KeyboardButton("⚔️ أنميشن وأنيمي ياباني (Anime)")],
        [KeyboardButton("💡 اكتب أي فكرة حرة من عندك"), KeyboardButton("ℹ️ عن الاستوديو والأنماط")]
    ],
    resize_keyboard=True
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎬✨ **أهلاً بك في استوديو الفيديو والأنيميشن الشامل بالذكاء الاصطناعي!**\n\n"
        "اختر النمط الذي تريده من الأزرار بالأسفل للبدء فوراً:\n\n"
        "1️⃣ **🐛 كارتون ومقالب لارفا 3D:** كوميديا صامتة هزلية مع زوومي وبزّوز.\n"
        "2️⃣ **🎬 فيديو سينمائي واقعي:** لقطات أفلام 4K، سيارات، مدن، طبيعة، وفضاء.\n"
        "3️⃣ **🐱 كارتون حيوانات وأبطال بيكسار:** شخصيات ديزني وبيكسار 3D.\n"
        "4️⃣ **⚔️ أنميشن وأنيمي ياباني:** معارك نينجا وأساطير يابانية مذهلة.\n"
        "5️⃣ **💡 فكرة حرة:** اكتب أي شيء يخطر ببالك ليتحول إلى فيديو فوراً!\n\n"
        "👇 اضغط على الزر الذي يعجبك أدناه للبدء:"
    )
    await update.message.reply_text(welcome_text, reply_markup=MAIN_KEYBOARD, parse_mode="Markdown")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info_text = (
        "ℹ️ **أنماط استوديو الفيديو بالذكاء الاصطناعي:**\n\n"
        "🔹 **كارتون لارفا 3D:** مقالب الصرصور زوومي والذبابة بزّوز بدون كلام مع المؤثرات الصوتية والموسيقى.\n"
        "🔹 **سينمائي 4K:** مشاهد واقعية فائقة الدقة بأسلوب هوليوود وإعلانات السيارات والماركات.\n"
        "🔹 **بيكسار وديزني:** كارتون عائلي لطيف للحيوانات والأبطال الخياليين.\n"
        "🔹 **الأنمي الياباني:** رسوم يابانية ملحمية بأسلوب ستوديو غيبلي وماكوتو شينكاي.\n\n"
        "⚡ كل الفيديوهات يتم توليدها بجودة عالية جاهزة للمشاركة والنشر فوراً!"
    )
    await update.message.reply_text(info_text, reply_markup=MAIN_KEYBOARD, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.strip()
    
    if user_text in ["ℹ️ عن الاستوديو والأنماط", "ℹ️ كيف يعمل النظام؟", "ℹ️ عن الشخصيات", "ℹ️ عن الشخصيات والنظام"]:
        await info_command(update, context)
        return
        
    if user_text in ["🐛 كارتون ومقالب لارفا 3D", "🪰🐛 حلقة جديدة: مقلب زوومي وبزّوز", "🪰🐛 حلقة زوومي وبزّوز (سريعة وخاطفة)"]:
        await update.message.reply_text(
            "🐛 **نمط كارتون ومقالب لارفا 3D:**\n\n"
            "اكتب فكرة المقلب الآن (مثلاً: *زوومي وبزّوز يتعاركون على قطعة جبن* أو *زوومي يتزحلق بقشرة موزة*)... أو اكتب كلمة *مقلب عشوائي* لتوليد فكرة فورية!",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    if user_text == "🎬 فيديو سينمائي واقعي (Cinematic)":
        await update.message.reply_text(
            "🎬 **نمط الفيديو السينمائي الواقعي 4K:**\n\n"
            "اكتب المشهد السينمائي الذي تريده (مثلاً: *سيارة رياضية سوداء مسرعة في شوارع طوكيو ليلاً تحت المطر وضوء النيون* أو *صقر يطير فوق جبال مغطاة بالثلوج*)...",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    if user_text == "🐱 كارتون حيوانات وأبطال بيكسار":
        await update.message.reply_text(
            "🐱 **نمط كارتون بيكسار وديزني 3D:**\n\n"
            "اكتب فكرة الكارتون (مثلاً: *قطة صغيرة ناعمة وكلب صغير يلعبون بالكرة في المطبخ ويتزحلقون*)...",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    if user_text == "⚔️ أنميشن وأنيمي ياباني (Anime)":
        await update.message.reply_text(
            "⚔️ **نمط الأنمي الياباني الأسطوري:**\n\n"
            "اكتب فكرة مشهد الأنمي (مثلاً: *فارس نينجا يقاتل بسيف متوهج على سطح قلعة وسط عاصفة أزهار الكرز*)...",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    if user_text in ["💡 اكتب أي فكرة حرة من عندك", "💡 اكتب فكرة مقلب من عندك", "💡 اكتب فكرة مقلب كارتوني"]:
        await update.message.reply_text(
            "💡 اكتب أي فكرة أو مشهد يخطر ببالك الآن وسيقوم الذكاء الاصطناعي بإنتاجها فيديو فوراً...",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    # تحديد نمط الفيديو بذكاء
    mode = "larva"
    if any(k in user_text for k in ["سينمائي", "واقعي", "سيارة", "طبيعة", "فيلم", "طوكيو", "دبي", "ساعة", "عطر", "فضاء"]):
        mode = "cinematic"
    elif any(k in user_text for k in ["أنمي", "انمي", "نينجا", "سيف", "تنين", "ساموراي", "ياباني"]):
        mode = "anime"
    elif any(k in user_text for k in ["بيكسار", "ديزني", "قطة", "بزونة", "كلب", "أرنب", "ديناصور"]):
        mode = "custom_cartoon"

    is_random = user_text in ["مقلب عشوائي", "حلقة جديدة", "عشوائي"]
    idea = None if is_random else user_text
    
    mode_names = {
        "larva": "كارتون لارفا 3D",
        "cinematic": "فيديو سينمائي واقعي 4K",
        "anime": "أنمي ياباني أسطوري",
        "custom_cartoon": "كارتون بيكسار وديزني 3D"
    }
    current_mode_name = mode_names.get(mode, "فيديو ذكاء اصطناعي")

    status_msg = await update.message.reply_text(f"🎬 بدأت عملية إنتاج **{current_mode_name}**... دقيقة من فضلك...")

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
                mode=mode,
                on_progress=lambda msg: asyncio.run_coroutine_threadsafe(
                    update_status(msg), loop
                ).result()
            )
        )

        await status_msg.edit_text("✅ اكتمل المونتاج بنجاح! جاري رفع الفيديو الآن إلى تليجرام... 🚀")

        # إرسال الفيديو النهائي مع كابشن مخصص للنمط
        captions = {
            "larva": "🎬 **حلقة كارتون لارفا 3D المتحركة جاهزة!**\n🐛 أبطال الحلقة: زوومي وبزّوز\n🔊 كوميديا صامتة بالأصوات والموسيقى الكارتونية.",
            "cinematic": "🎬 **المشهد السينمائي الواقعي 4K جاهز!**\n🍿 دقة سينمائية فائقة وحركة كاميرا احترافية.",
            "anime": "⚔️ **مشهد الأنمي الياباني الأسطوري جاهز!**\n🌸 أسلوب أنيميشن ياباني ناعم ومميز.",
            "custom_cartoon": "🐱 **كارتون بيكسار 3D جاهز!**\n🎨 شخصيات كارتونية لطيفة ومتحركة بالكامل."
        }
        chosen_caption = captions.get(mode, "🎬 **الفيديو جاهز بالذكاء الاصطناعي!**")

        with open(video_path, "rb") as vf:
            await update.message.reply_video(
                video=vf,
                caption=f"{chosen_caption}\n\n📲 جاهز للمشاركة والنشر فوراً!",
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

