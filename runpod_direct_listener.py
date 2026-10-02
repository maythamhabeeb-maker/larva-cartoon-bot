import requests
import time
import json
import sys
import io
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from tools.runpod_comfy_tool import generate_character_on_runpod, generate_video_on_runpod, add_cartoon_audio

token = "8187016408:AAFe4BZYwEZGC8c6iBxHCD5W1NM8omeOnsI"
base_api = f"https://api.telegram.org/bot{token}"

def send_msg(chat_id, text):
    try:
        requests.post(f"{base_api}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        print("send_msg error:", e)

def send_photo(chat_id, photo_path, caption):
    try:
        with open(photo_path, "rb") as f:
            requests.post(f"{base_api}/sendPhoto", data={"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}, files={"photo": f})
    except Exception as e:
        print("send_photo error:", e)

def send_video(chat_id, video_path, caption):
    try:
        with open(video_path, "rb") as f:
            requests.post(f"{base_api}/sendVideo", data={"chat_id": chat_id, "caption": caption, "supports_streaming": True, "parse_mode": "Markdown"}, files={"video": f}, timeout=120)
    except Exception as e:
        print("send_video error:", e)

print("⚡ Starting direct RunPod RTX 4090 Telegram listener...", flush=True)
offset = None

while True:
    try:
        url = f"{base_api}/getUpdates?timeout=5"
        if offset:
            url += f"&offset={offset}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for u in data.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message")
                if not msg or not msg.get("text"):
                    continue
                chat_id = msg["chat"]["id"]
                user_text = msg["text"].strip()
                print(f"📥 Received from {chat_id}: {user_text}")
                
                # Acknowledge immediately
                send_msg(chat_id, "⚡ **تم استلام طلبك مباشرة على كارت الشاشة RunPod RTX 4090!**\n\n🎨 جاري الآن رسم شخصيات المشهد بأسلوب بيكسار 3D...")
                
                # Clean prompt
                clean_idea = user_text.replace("/gpu", "").replace("/GPU", "").replace("/start", "").strip()
                if not clean_idea:
                    clean_idea = "تنين صغير وبومة في غابة ساحرة"
                
                run_id = int(time.time())
                Path("output").mkdir(parents=True, exist_ok=True)
                
                # 1. Generate character on 4090
                char_path = f"output/runpod_char_{run_id}.png"
                print(f"Generating character on RTX 4090: {clean_idea}...")
                generate_character_on_runpod(clean_idea, char_path)
                
                # Send photo
                send_photo(chat_id, char_path, "🎨 **تم تصميم بطل المشهد بدقة Ultra-HD 4K بيكسار 3D!**\n🎬 جاري الآن إنتاج حركة سينمائية فائقة الوضوح عبر موديل **Wan 2.1** الحديث...")
                
                # 2. Generate video on 4090 using Wan 2.1
                raw_video = f"output/runpod_raw_{run_id}.mp4"
                print("Generating Wan 2.1 video on RTX 4090...")
                generate_video_on_runpod(char_path, raw_video, prompt_text=clean_idea)
                
                # 3. Add cartoon BGM
                final_video = f"output/runpod_video_{run_id}.mp4"
                add_cartoon_audio(raw_video, final_video)
                
                # Send video
                caption = (
                    "🔥 **فيديو سينمائي فائق الوضوح مُنتج عبر موديل Wan 2.1 الحديث!**\n\n"
                    "🎮 **البطاقة:** NVIDIA GeForce RTX 4090 (24GB VRAM)\n"
                    "🧠 **الموديل:** Wan 2.1 + 4x-UltraSharp 4K\n"
                    "✨ جودة سينمائية خالية تماماً من التشويش أو التمويه، تم التوليد بنسبة 100% على بطاقتك المستأجرة بدون أي خصم خارجي!"
                )
                print(f"Sending video to chat {chat_id}...")
                send_video(chat_id, final_video, caption)
                print("✅ Successfully delivered to Telegram!")
        elif r.status_code == 409:
            time.sleep(1)
    except Exception as e:
        print("Loop error:", e)
        time.sleep(2)
