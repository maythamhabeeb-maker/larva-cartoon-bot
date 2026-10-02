"""Replicate Video Tool - محرك توليد الفيديو الحقيقي بالذكاء الاصطناعي (MiniMax / Hailuo Video-01).
يولد فيديو MP4 كامل مدته 6 ثوانٍ مع حركة فيزيائية حقيقية للشخصيات.
"""
import sys
import io
import os
import time
import base64
import logging
from pathlib import Path
import requests
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv()
logger = logging.getLogger(__name__)

from config import REPLICATE_API_TOKEN

def get_replicate_token() -> str:
    token = (os.getenv("REPLICATE_API_TOKEN") or "").strip().strip('"').strip("'")
    return token if token else REPLICATE_API_TOKEN

def _image_to_data_uri(image_path: Path) -> str:
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    ext = image_path.suffix.lower().replace(".", "")
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{encoded}"

def generate_video_minimax(prompt: str, first_frame_image: Path = None, output_path: Path = None, on_progress=None) -> Path:
    token = get_replicate_token()
    if not token:
        raise ValueError("REPLICATE_API_TOKEN is not set!")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "wait"
    }

    input_payload = {
        "prompt": prompt,
        "prompt_optimizer": True
    }

    if first_frame_image and Path(first_frame_image).exists():
        input_payload["first_frame_image"] = _image_to_data_uri(Path(first_frame_image))

    if on_progress:
        on_progress("🎬 إرسال طلب الفيديو إلى محرك MiniMax / Hailuo العالمي...")

    url = "https://api.replicate.com/v1/models/minimax/video-01/predictions"
    resp = requests.post(url, headers=headers, json={"input": input_payload}, timeout=30)
    
    if resp.status_code not in [200, 201, 202]:
        raise RuntimeError(f"Replicate API error ({resp.status_code}): {resp.text}")

    prediction = resp.json()
    prediction_id = prediction.get("id")
    poll_url = prediction.get("urls", {}).get("get", f"https://api.replicate.com/v1/predictions/{prediction_id}")

    logger.info(f"Video prediction started: {prediction_id}")

    # Polling until done
    start_time = time.time()
    last_report_time = start_time
    while True:
        try:
            poll_resp = requests.get(poll_url, headers={"Authorization": f"Bearer {token}"}, timeout=25)
        except Exception as e:
            logger.warning(f"Poll request network retry: {e}")
            time.sleep(3)
            continue

        if poll_resp.status_code != 200:
            time.sleep(4)
            continue

        p_data = poll_resp.json()
        status = p_data.get("status")

        now = time.time()
        if on_progress and (now - last_report_time >= 15):
            elapsed = int(now - start_time)
            on_progress(f"⏳ معالجة حركة الفيديو بالذكاء الاصطناعي... ({elapsed} ثانية)")
            last_report_time = now

        if status == "succeeded":
            video_url = p_data.get("output")
            if isinstance(video_url, list):
                video_url = video_url[0]

            if not video_url:
                raise RuntimeError("No video URL returned in output.")

            if on_progress:
                on_progress("📥 اكتمل التوليد! جاري تحميل الفيديو المتحرك...")

            # Download MP4
            if output_path is None:
                output_path = Path("output") / f"minimax_{prediction_id}.mp4"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            v_resp = requests.get(video_url, stream=True)
            with open(output_path, "wb") as f:
                for chunk in v_resp.iter_content(chunk_size=8192):
                    f.write(chunk)

            if on_progress:
                on_progress(f"✅ تم تحميل الفيديو المتحرك بنجاح ({output_path.stat().st_size//1024} KB)")

            return output_path

        elif status == "failed":
            err = p_data.get("error", "Unknown error")
            raise RuntimeError(f"Video generation failed: {err}")

        elif status == "canceled":
            raise RuntimeError("Video generation was canceled.")

        time.sleep(5)

def enrich_video_prompt(idea: str = None, mode: str = "larva", on_progress=None) -> str:
    """تحويل فكرة المستخدم (بالعربي أو الإنجليزي) إلى وصف بصري إخراجي هوليوودي فائق الدقة بالإنجليزية."""
    clean_idea = (idea or "").strip()
    if on_progress:
        on_progress("🧠 المخرج الذكي يصيغ المشهد السينمائي وأبعاد الحركة والإضاءة ثلاثية الأبعاد...")

    try:
        from tools.gemini_tool import generate_text
        prompt_instruction = f"""
You are a World-Class Hollywood Animation Director and Master Visual Prompt Engineer for AI Video Generators (MiniMax / Hailuo Video-01).
Transform the user's idea into ONE single, highly-detailed, cinematic English prompt for a 3D motion video.

User Idea: {clean_idea if clean_idea else 'A hilarious slapstick gag between Zoomy and Bazzouz'}
Target Mode: {mode}

Guidelines per mode:
1. 'larva':
   - Focus on Zoomy (an adorable goofy glossy amber-golden cartoon cockroach with giant round bulging googly eyes and springy antennae) and/or Bazzouz (a chubby metallic electric-blue fly with comic red goggles).
   - Setting: realistic sunlit urban sewer drain concrete floor with soda cans and colorful bottle caps.
   - Action: funny high-speed physical slapstick comedy, elastic squash-and-stretch body deformation, cartoon reactions, vivid colors, fluid 3D character animation in Pixar and Larva style.
2. 'cinematic':
   - 8K ultra-photorealistic cinematic movie shot, anamorphic 35mm lens, dramatic volumetric lighting, IMAX scale realism, ray-traced reflections, smooth cinematic gimbal movement.
3. 'anime':
   - Masterpiece anime animation scene, Studio Ufotable & Makoto Shinkai aesthetic, vibrant anime colors, dynamic sakuga motion, dramatic anime lighting.
4. 'custom_cartoon':
   - 3D Pixar & Disney animation style, lovable cute expressive characters, soft subsurface scattering fur/skin, bright cheerful colors, vibrant lighting, smooth 3D motion.

Output ONLY the final English visual prompt in 2 to 3 detailed descriptive sentences. Do NOT include markdown, quotes, or preambles.
"""
        enriched = generate_text(prompt_instruction).strip().strip('"').strip("'")
        if enriched and len(enriched) > 20:
            return enriched
    except Exception as e:
        logger.warning(f"Error enriching prompt with LLM: {e}")

    # Fallback if LLM unavailable
    if mode == "cinematic":
        return f"Masterpiece 4K ultra-realistic cinematic movie footage: {clean_idea if clean_idea else 'A luxury sports car speeding on a neon-lit wet Tokyo highway at night under rain'}. Hyper-realistic, dramatic volumetric lighting, shot on 35mm anamorphic lens, IMAX quality, photorealistic reflections, smooth camera tracking."
    elif mode == "anime":
        return f"Masterpiece Japanese anime animation scene, Studio Ghibli and Makoto Shinkai aesthetic: {clean_idea if clean_idea else 'A brave young ninja warrior with glowing katana standing on a pagoda rooftop during cherry blossom storm'}. High quality anime art, vibrant colors, fluid expressive motion, atmospheric cinematic lighting."
    elif mode == "custom_cartoon":
        return f"Masterpiece 3D Pixar Disney style animated cartoon scene: {clean_idea if clean_idea else 'A cute fluffy baby kitten and puppy playing together and sliding on a kitchen floor'}. Adorable expressive characters, fluid 3D character movement, vibrant cheerful colors, rich studio lighting."
    else:
        return f"Masterpiece 3D CGI cartoon slapstick animation scene: {clean_idea if clean_idea else 'A cute goofy golden cartoon cockroach named Zoomy slipping and fast-running in a sewer drain, elastic legs, slapstick funny movements, shiny textures'}. Pixar & Larva 3D animation style, extremely fluid character movement, funny physical comedy, high framerate, rich volumetric lighting."


def produce_full_motion_slapstick(idea: str = None, mode: str = "larva", on_progress=None) -> Path:
    """توليد فيديو حركة 3D بالذكاء الاصطناعي مع دعم الأنماط المختلفة (لارفا، سينمائي واقعي، أنمي، بيكسار)."""
    clean_idea = (idea or "").strip()
    prompt = enrich_video_prompt(idea=clean_idea, mode=mode, on_progress=on_progress)
    logger.info(f"Generated enriched prompt for mode [{mode}]: {prompt}")

    raw_video = generate_video_minimax(prompt=prompt, on_progress=on_progress)
    
    if on_progress:
        on_progress("✂️ تركيب الصوت والمونتاج النهائي على الفيديو (فوري)...")
        
    sfx_dir = Path(__file__).resolve().parent.parent / "assets" / "sfx"
    out_final = raw_video.parent / f"final_{raw_video.name}"
    
    if mode in ["larva", "custom_cartoon"]:
        import subprocess
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        bgm_file = sfx_dir / "funny_bgm.wav"
        if bgm_file.exists():
            cmd = [
                ffmpeg_exe, "-y",
                "-i", str(raw_video),
                "-i", str(bgm_file),
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(out_final)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            out_final = raw_video
    else:
        out_final = raw_video
        
    return out_final


if __name__ == "__main__":
    test_prompt = "3D cartoon slapstick scene of a cute goofy golden cockroach slipping and running around in a sewer drain, fast funny motion"
    out = generate_video_minimax(test_prompt, on_progress=print)
    print("Done:", out)
