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
    resp = requests.post(url, headers=headers, json={"input": input_payload})
    
    if resp.status_code not in [200, 201, 202]:
        raise RuntimeError(f"Replicate API error ({resp.status_code}): {resp.text}")

    prediction = resp.json()
    prediction_id = prediction.get("id")
    poll_url = prediction.get("urls", {}).get("get", f"https://api.replicate.com/v1/predictions/{prediction_id}")

    logger.info(f"Video prediction started: {prediction_id}")

    # Polling until done
    start_time = time.time()
    while True:
        poll_resp = requests.get(poll_url, headers={"Authorization": f"Bearer {token}"})
        if poll_resp.status_code != 200:
            time.sleep(4)
            continue

        p_data = poll_resp.json()
        status = p_data.get("status")

        elapsed = int(time.time() - start_time)
        if on_progress and elapsed % 15 == 0:
            on_progress(f"⏳ معالجة حركة الفيديو بالذكاء الاصطناعي... ({elapsed} ثانية)")

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

def produce_full_motion_slapstick(idea: str = None, mode: str = "larva", on_progress=None) -> Path:
    """توليد فيديو حركة 3D بالذكاء الاصطناعي مع دعم الأنماط المختلفة (لارفا، سينمائي واقعي، أنمي، بيكسار)."""
    from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
    from moviepy.audio.fx import MultiplyVolume
    
    clean_idea = (idea or "").strip()
    
    if mode == "cinematic":
        prompt = (
            f"Masterpiece 4K ultra-realistic cinematic movie footage: {clean_idea if clean_idea else 'A luxury sports car speeding on a neon-lit wet Tokyo highway at night under rain'}. "
            "Hyper-realistic, dramatic volumetric lighting, shot on 35mm anamorphic lens, IMAX quality, photorealistic reflections, smooth camera tracking."
        )
    elif mode == "anime":
        prompt = (
            f"Masterpiece Japanese anime animation scene, Studio Ghibli and Makoto Shinkai aesthetic: {clean_idea if clean_idea else 'A brave young ninja warrior with glowing katana standing on a pagoda rooftop during cherry blossom storm'}. "
            "High quality anime art, vibrant colors, fluid expressive motion, atmospheric cinematic lighting."
        )
    elif mode == "custom_cartoon":
        prompt = (
            f"Masterpiece 3D Pixar Disney style animated cartoon scene: {clean_idea if clean_idea else 'A cute fluffy baby kitten and puppy playing together and sliding on a kitchen floor'}. "
            "Adorable expressive characters, fluid 3D character movement, vibrant cheerful colors, rich studio lighting."
        )
    else:  # larva mode
        prompt = (
            f"Masterpiece 3D CGI cartoon slapstick animation scene: {clean_idea if clean_idea else 'A cute goofy golden cartoon cockroach named Zoomy slipping and fast-running in a sewer drain, elastic legs, slapstick funny movements, shiny textures'}. "
            "Pixar & Larva 3D animation style, extremely fluid character movement, funny physical comedy, high framerate, rich volumetric lighting."
        )
    
    raw_video = generate_video_minimax(prompt=prompt, on_progress=on_progress)
    
    if on_progress:
        on_progress("✂️ معالجة وتركيب الصوت والمونتاج النهائي على الفيديو...")
        
    clip = VideoFileClip(str(raw_video))
    dur = clip.duration
    
    sfx_dir = Path(__file__).resolve().parent.parent / "assets" / "sfx"
    
    if mode in ["larva", "custom_cartoon"]:
        bgm = AudioFileClip(str(sfx_dir / "funny_bgm.wav")).subclipped(0, min(dur, 12.0)).with_effects([MultiplyVolume(0.4)])
        boing = AudioFileClip(str(sfx_dir / "boing.wav")).with_start(1.0)
        splat = AudioFileClip(str(sfx_dir / "splat.wav")).with_start(max(0.5, dur - 1.5))
        mixed_audio = CompositeAudioClip([bgm, boing, splat])
        final_video = clip.with_audio(mixed_audio)
    else:
        final_video = clip
    
    out_final = raw_video.parent / f"final_{raw_video.name}"
    final_video.write_videofile(
        str(out_final),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )
    
    try:
        final_video.close()
        clip.close()
    except Exception:
        pass
        
    return out_final


if __name__ == "__main__":
    test_prompt = "3D cartoon slapstick scene of a cute goofy golden cockroach slipping and running around in a sewer drain, fast funny motion"
    out = generate_video_minimax(test_prompt, on_progress=print)
    print("Done:", out)
