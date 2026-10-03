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
        [KeyboardButton("⚡ كارت شاشة RunPod RTX 4090"), KeyboardButton("📺 حلقة يوتيوب كاملة (قصة طويلة)")],
        [KeyboardButton("🐛 مقلب سريع (ريلز وشورتس)"), KeyboardButton("🐱 كارتون حيوانات وبيكسار 3D")],
        [KeyboardButton("🎬 فيديو سينمائي واقعي (Cinematic)"), KeyboardButton("⚔️ أنميشن وأنيمي ياباني (Anime)")],
        [KeyboardButton("ℹ️ عن الاستوديو والأنماط")]
    ],
    resize_keyboard=True
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎬✨ **أهلاً بك في استوديو الفيديو والأنيميشن الشامل بالذكاء الاصطناعي!**\n\n"
        "اختر النمط الذي تريده من الأزرار بالأسفل للبدء فوراً:\n\n"
        "⚡ **كارت شاشة RunPod RTX 4090:** توليد مباشر وسريع باستخدام كارت الشاشة الخاص بك (صور + فيديو مجاناً وبدون استهلاك رصيد خارجي).\n"
        "1️⃣ **📺 حلقة يوتيوب كاملة:** قصة كارتونية متكاملة من عدة مشاهد مع المونتاج والمؤثرات.\n"
        "2️⃣ **🐛 مقلب سريع (ريلز وشورتس):** فيديو كارتون 3D خاطف جاهز للمشاركة السريعة.\n"
        "3️⃣ **🎬 فيديو سينمائي واقعي:** لقطات أفلام 4K، سيارات، مدن، وفضاء.\n"
        "4️⃣ **⚔️ أنميشن وأنيمي ياباني:** معارك نينجا وأساطير يابانية مذهلة.\n"
        "5️⃣ **🐱 كارتون حيوانات وبيكسار:** شخصيات كارتونية لطيفة ومتحركة.\n\n"
        "👇 اضغط على الزر الذي تريده أدناه للبدء أو اكتب الأمر `/gpu <فكرتك>`:"
    )
    await update.message.reply_text(welcome_text, reply_markup=MAIN_KEYBOARD, parse_mode="Markdown")

async def gpu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        update.message.text = " ".join(context.args)
        context.user_data["selected_mode"] = "runpod_gpu"
        await handle_message(update, context)
    else:
        context.user_data["selected_mode"] = "runpod_gpu"
        await update.message.reply_text(
            "⚡ **تم تفعيل نمط كارت الشاشة RunPod RTX 4090!**\n\n"
            "اكتب الآن فكرة المشهد (مثلاً: *تنين صغير وبومة في غابة ساحرة*) وسيقوم كارت الشاشة برسم الشخصيات أولاً ثم تحريكهم فيديو فوراً! 🚀",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    info_text = (
        "ℹ️ **أنماط استوديو الفيديو بالذكاء الاصطناعي:**\n\n"
        "📺 **حلقة يوتيوب كاملة:** قصة مقلب طويلة مكونة من عدة مشاهد متسلسلة مع الموسيقى والمؤثرات.\n"
        "🐛 **مقلب سريع (ريلز):** لقطات 3D سريعة وخاطفة لمواقع التواصل.\n"
        "🎬 **سينمائي 4K:** مشاهد واقعية فائقة الدقة بأسلوب هوليوود.\n"
        "⚔️ **أنمي ياباني:** رسوم أنمي يابانية ملحمية.\n"
        "🐱 **بيكسار 3D:** كارتون عائلي لطيف للحيوانات والأبطال.\n\n"
        "⚡ كل الفيديوهات جاهزة للنشر فوراً بدون أي علامة مائية!"
    )
    await update.message.reply_text(info_text, reply_markup=MAIN_KEYBOARD, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return
    user_text = update.message.text.strip()
    Path("output").mkdir(parents=True, exist_ok=True)
    
    # Check if /gpu is typed anywhere in the message (start, middle, or end)
    if "/gpu" in user_text.lower():
        user_text = user_text.replace("/gpu", "").replace("/GPU", "").strip()
        context.user_data["selected_mode"] = "runpod_gpu"
        if not user_text:
            await update.message.reply_text(
                "⚡ **تم تفعيل نمط كارت الشاشة RunPod RTX 4090!**\n\n"
                "اكتب الآن فكرة المشهد (مثلاً: *تنين صغير وبومة في غابة ساحرة*) وسيقوم كارت الـ 4090 بتوليد صورة الشخصيات وتحريكها فيديو فوراً وبدون أي تكلفة إضافية! 🚀",
                reply_markup=MAIN_KEYBOARD,
                parse_mode="Markdown"
            )
            return

    if user_text in ["ℹ️ عن الاستوديو والأنماط", "ℹ️ كيف يعمل النظام؟", "ℹ️ عن الشخصيات", "ℹ️ عن الشخصيات والنظام"]:
        await info_command(update, context)
        return

    if user_text in ["⚡ كارت شاشة RunPod RTX 4090", "كارت شاشة", "كارت الشاشة", "runpod", "4090", "gpu"]:
        context.user_data["selected_mode"] = "runpod_gpu"
        await update.message.reply_text(
            "⚡ **تم تفعيل نمط كارت الشاشة RunPod RTX 4090!**\n\n"
            "اكتب الآن فكرة المشهد (مثلاً: *تنين صغير وبومة في غابة ساحرة*) وسيقوم كارت الـ 4090 بتوليد صورة الشخصيات وتحريكها فيديو فوراً وبدون أي تكلفة إضافية! 🚀",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    if user_text in ["📺 حلقة يوتيوب كاملة (قصة طويلة)", "📺 حلقة كاملة (قصة متعددة المشاهد)", "حلقة كاملة"]:
        context.user_data["selected_mode"] = "long_episode"
        await update.message.reply_text(
            "📺 **نمط حلقة كارتون كاملة (متعددة المشاهد والمقالب):**\n\n"
            "اكتب فكرة الحلقة الآن (مثلاً: *شجار زوومي وبزّوز على شريحة بيتزا ساخنة في المجاري* أو *معركة قوطية البيبسي الطائرة*)... أو اكتب *حلقة عشوائية* وسيتولى المخرج تأليف وتصوير كافة المشاهد ودمجها لك!",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return
        
    if user_text in ["🐛 كارتون ومقالب لارفا 3D", "🐛 مقلب سريع (ريلز وشورتس)", "🪰🐛 حلقة جديدة: مقلب زوومي وبزّوز"]:
        context.user_data["selected_mode"] = "larva"
        await update.message.reply_text(
            "🐛 **نمط مقلب كارتون 3D سريع (مشهد واحد ريلز):**\n\n"
            "اكتب فكرة المقلب الآن (مثلاً: *زوومي يتزحلق بقشرة موزة*)... أو اكتب كلمة *مقلب عشوائي*!",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    if user_text == "🎬 فيديو سينمائي واقعي (Cinematic)":
        context.user_data["selected_mode"] = "cinematic"
        await update.message.reply_text(
            "🎬 **نمط الفيديو السينمائي الواقعي 4K:**\n\n"
            "اكتب المشهد السينمائي الذي تريده (مثلاً: *سيارة رياضية مسرعة في طوكيو تحت المطر*)...",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    if user_text in ["🐱 كارتون حيوانات وأبطال بيكسار", "🐱 كارتون حيوانات وبيكسار 3D"]:
        context.user_data["selected_mode"] = "custom_cartoon"
        await update.message.reply_text(
            "🐱 **نمط كارتون بيكسار وديزني 3D:**\n\n"
            "اكتب فكرة الكارتون (مثلاً: *قطة صغيرة وكلب يلعبون بالكرة ويتزحلقون*)...",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    if user_text == "⚔️ أنميشن وأنيمي ياباني (Anime)":
        context.user_data["selected_mode"] = "anime"
        await update.message.reply_text(
            "⚔️ **نمط الأنمي الياباني الأسطوري:**\n\n"
            "اكتب فكرة مشهد الأنمي (مثلاً: *فارس نينجا يقاتل بسيف متوهج على سطح قلعة*)...",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    if user_text in ["💡 اكتب أي فكرة حرة من عندك", "💡 اكتب فكرة مقلب من عندك"]:
        await update.message.reply_text(
            "💡 اكتب أي فكرة أو مشهد يخطر ببالك وسيقوم الذكاء الاصطناعي بإنتاجها فيديو فوراً...",
            reply_markup=MAIN_KEYBOARD,
            parse_mode="Markdown"
        )
        return

    # تحديد نمط الفيديو بذكاء
    saved_mode = context.user_data.get("selected_mode")
    is_gpu_kw = any(k in user_text.lower() for k in ["كارت", "4090", "runpod", "gpu", "شاشة", "شاشه"])
    is_long_kw = any(k in user_text for k in [
        "طويلة", "طويله", "يوتيوب", "كاملة", "كامله", "كاملى", "حلقة", "حلقه", "حلقى",
        "مشاهد", "مسلسل", "قصة", "قصه", "مغامرة", "مغامره", "فيلم", "فلم", "10", "عشر", "عشرة",
        "أفاتار", "افاتار", "رحلة", "رحله", "دين", "تاريخ"
    ])
    
    if saved_mode == "runpod_gpu" or (is_gpu_kw and len(user_text.split()) > 1):
        mode = "runpod_gpu"
    elif saved_mode == "long_episode" or is_long_kw:
        mode = "long_episode"
    elif saved_mode:
        mode = saved_mode
    elif any(k in user_text for k in ["سينمائي", "واقعي", "سيارة", "طبيعة", "فيلم", "طوكيو", "دبي", "فضاء"]):
        mode = "cinematic"
    elif any(k in user_text for k in ["أنمي", "انمي", "نينجا", "سيف", "تنين", "ساموراي", "ياباني"]):
        mode = "anime"
    elif any(k in user_text for k in ["بيكسار", "ديزني", "قطة", "بزونة", "كلب", "أرنب", "حيوانات", "بومة"]):
        mode = "custom_cartoon"
    else:
        mode = "larva"

    # Reset selected mode after use
    context.user_data["selected_mode"] = None

    is_random = user_text in ["مقلب عشوائي", "حلقة جديدة", "عشوائي", "حلقة عشوائية", "حلقة كاملة عشوائية"]
    idea = None if is_random else user_text
    
    mode_names = {
        "runpod_gpu": "⚡ كارت شاشة RunPod RTX 4090 (صور + فيديو)",
        "long_episode": "📺 حلقة كارتون كاملة متكاملة المشاهد والأبطال",
        "larva": "🐛 مقلب كارتون لارفا 3D",
        "cinematic": "🎬 فيديو سينمائي واقعي 4K",
        "anime": "⚔️ أنمي ياباني أسطوري",
        "custom_cartoon": "🐱 كارتون بيكسار وديزني 3D"
    }
    current_mode_name = mode_names.get(mode, "فيديو ذكاء اصطناعي")

    status_msg = await update.message.reply_text(f"🎬 بدأت عملية إنتاج **{current_mode_name}**... ثواني من فضلك...")

    progress_history = []

    async def update_status(text: str):
        progress_history.append(text)
        current_display = "🎬 **مراحل الإنتاج السينمائي:**\n\n" + "\n".join(progress_history[-5:])
        try:
            await status_msg.edit_text(current_display, parse_mode="Markdown")
        except Exception:
            pass

    loop = asyncio.get_event_loop()
    plan_data = None
    char_ref_path = None

    def safe_progress(msg: str):
        try:
            asyncio.run_coroutine_threadsafe(update_status(msg), loop)
        except Exception:
            pass

    try:
        if mode == "runpod_gpu":
            from tools.runpod_comfy_tool import generate_character_on_runpod, generate_video_on_runpod, add_cartoon_audio
            import time
            safe_progress("⚡ 1/3: جاري الاتصال بكارت الشاشة RTX 4090 ورسم شخصيات المشهد بدقة 4K بيكسار...")
            run_id = int(time.time())
            char_ref_path = f"output/runpod_char_{run_id}.png"
            char_prompt = idea if idea else "3D Pixar cartoon cute baby dragon and curious round owl"
            await loop.run_in_executor(
                None,
                lambda: generate_character_on_runpod(char_prompt, char_ref_path)
            )
            safe_progress("🎬 2/3: تم إنشاء هوية الشخصيات! جاري إنتاج حركة سينمائية فائقة الوضوح عبر موديل Wan 2.1...")
            raw_video_path = f"output/runpod_raw_{run_id}.mp4"
            await loop.run_in_executor(
                None,
                lambda: generate_video_on_runpod(char_ref_path, raw_video_path, prompt_text=char_prompt)
            )
            safe_progress("🔊 3/3: جاري إضافة المؤثرات الصوتية والموسيقى التصويرية الكارتونية...")
            final_video_path = f"output/runpod_video_{run_id}.mp4"
            video_path = await loop.run_in_executor(
                None,
                lambda: add_cartoon_audio(raw_video_path, final_video_path)
            )
        elif mode == "long_episode":
            from tools.universal_studio_generator import produce_universal_episode
            video_path, plan_data, char_ref_path = await loop.run_in_executor(
                None,
                lambda: produce_universal_episode(
                    idea=idea,
                    on_progress=safe_progress
                )
            )
        else:
            # كافة الأنماط الأخرى تعمل 100% على كارت الشاشة RTX 4090 وبدون أي تكلفة خارجية
            from tools.runpod_comfy_tool import generate_character_on_runpod, generate_video_on_runpod, add_cartoon_audio
            import time
            safe_progress("⚡ 1/3: جاري رسم وتصميم أبطال المشهد بدقة 4K على كارت الشاشة RTX 4090...")
            run_id = int(time.time())
            char_ref_path = f"output/runpod_char_{run_id}.png"
            char_prompt = idea if idea else "cute 3d cartoon character"
            await loop.run_in_executor(
                None,
                lambda: generate_character_on_runpod(char_prompt, char_ref_path)
            )
            safe_progress("🎬 2/3: جاري إنتاج حركة سينمائية فائقة الوضوح عبر موديل Wan 2.1 على كارت الـ RTX 4090...")
            raw_video_path = f"output/runpod_raw_{run_id}.mp4"
            await loop.run_in_executor(
                None,
                lambda: generate_video_on_runpod(char_ref_path, raw_video_path, prompt_text=char_prompt)
            )
            safe_progress("🔊 3/3: جاري تركيب المؤثرات الصوتية والموسيقى التصويرية...")
            final_video_path = f"output/runpod_video_{run_id}.mp4"
            video_path = await loop.run_in_executor(
                None,
                lambda: add_cartoon_audio(raw_video_path, final_video_path)
            )

        await status_msg.edit_text("✅ اكتمل المونتاج بنجاح! جاري رفع الحلقة الآن إلى تليجرام... 🚀")

        # إرسال صورة الشخصيات المرجعية أولاً إذا كانت متوفرة
        if char_ref_path and Path(char_ref_path).exists():
            try:
                with open(char_ref_path, "rb") as pf:
                    await update.message.reply_photo(
                        photo=pf,
                        caption="🎨 **التصميم المعتمد لأبطال القصة (Character Concept Art)**\nتم تثبيت ملامحهم وهويتهم ثلاثية الأبعاد وتحريك مشاهد الحلقة انطلاقاً من هذه الصورة لضمان تطابقهم 100%."
                    )
            except Exception as e:
                logger.warning(f"Error sending character photo: {e}")

        # إرسال الفيديو النهائي مع كابشن مخصص ومفصل
        if mode == "long_episode" and plan_data:
            title = plan_data.get("title_ar", "حلقة كارتون كاملة")
            chars = " و ".join([c.get("name_ar", "") for c in plan_data.get("characters", []) if c.get("name_ar")])
            scenes_count = len(plan_data.get("scenes", []))
            chosen_caption = (
                f"🎬 **«{title}» (حلقة كاملة متكاملة)**\n\n"
                f"👥 أبطال الحلقة: {chars if chars else 'أبطال الكارتون'}\n"
                f"🎞️ عدد المشاهد: {scenes_count} مشاهد كارتونية متسلسلة ومدمجة\n\n"
                "🍿 حركة 3D سينمائية حقيقية من نفس صورة الأبطال.\n"
                "🔊 هندسة أصوات الحركات والضربات + الموسيقى التصويرية الكارتونية."
            )
        elif mode == "runpod_gpu":
            chosen_caption = (
                "⚡ **فيديو كارتوني متحرك مُنتج مباشرة على كارت الشاشة RunPod RTX 4090 الخاص بك!**\n\n"
                "🎮 **البطاقة:** NVIDIA GeForce RTX 4090 (24GB VRAM)\n"
                "🎨 **النموذج:** DreamShaper 3D + Stable Video Diffusion\n"
                "✨ تم التوليد والتحريك بنسبة 100% على بطاقتك المستأجرة بدون أي وسيط خارجي!"
            )
        else:
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
    app.add_handler(CommandHandler("gpu", gpu_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    print("🚀 Larva 3D Slapstick Studio Telegram Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

