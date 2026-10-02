"""Long Episode Generator - محرك إنتاج حلقات الكارتون الطويلة لليوتيوب (Larva 3D Series).
يقوم بإنتاج حلقة متكاملة متعددة المشاهد مع المونتاج والمؤثرات الصوتية والموسيقى الممتدة.
"""
import sys
import io
import os
import re
import time
import logging
import subprocess
from pathlib import Path
import imageio_ffmpeg

from config import OUTPUT_DIR
from agents import long_story_agent
from tools.replicate_video_tool import generate_video_minimax

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SFX_DIR = PROJECT_ROOT / "assets" / "sfx"

def _safe_name(text: str) -> str:
    text = re.sub(r"[^\w\u0600-\u06FF\s-]", "", text)
    return text.strip().replace(" ", "_")[:30]

def produce_long_cartoon_episode(idea: str = None, scene_count: int = 6, on_progress=None) -> Path:
    """إنتاج حلقة يوتيوب كارتونية طويلة متكاملة المشاهد والمؤثرات الصوتية."""
    def progress(msg: str):
        if on_progress:
            on_progress(msg)

    # 1. تأليف القصة والسيناريو الكامل
    script_data = long_story_agent.create_long_episode_script(idea=idea, scene_count=scene_count, on_progress=progress)
    title = script_data.get("title_ar", "حلقة_كارتون_طويلة")
    scenes = script_data.get("scenes", [])
    
    progress(f"🎬 عنوان الحلقة: «{title}» ({len(scenes)} مشاهد كارتونية)")
    
    episode_dir = OUTPUT_DIR / f"long_{_safe_name(title)}_{int(time.time())}"
    episode_dir.mkdir(parents=True, exist_ok=True)
    
    generated_scene_files = []
    
    # 2. توليد المشاهد مشهد تلو الآخر
    for i, sc in enumerate(scenes):
        sc_num = i + 1
        summary = sc.get("action_summary_ar", "")
        prompt = sc.get("visual_prompt_en", "")
        
        progress(f"🎥 تصوير المشهد {sc_num}/{len(scenes)}: {summary}...")
        
        out_scene_path = episode_dir / f"scene_{sc_num}.mp4"
        try:
            # نولد مشهد حركة 3D حقيقي
            generate_video_minimax(
                prompt=f"{prompt}. Pixar & Larva 3D slapstick cartoon animation style, fluid physical comedy, rich lighting.",
                output_path=out_scene_path,
                on_progress=lambda m: progress(f"  [المشهد {sc_num}] {m}")
            )
            generated_scene_files.append(out_scene_path)
        except Exception as e:
            logger.error(f"Error generating scene {sc_num}: {e}")
            # إذا فشل مشهد لسبب ما، نستمر بالمشاهد المتبقية
            continue

    if not generated_scene_files:
        raise RuntimeError("لم يتم توليد أي مشهد بنجاح.")

    progress("✂️ المونتير يقوم بدمج المشاهد وتركيب الموسيقى والمؤثرات الصوتية لكامل الحلقة...")

    # 3. دمج المشاهد باستخدام FFmpeg السريع والخفيف (0% ضغط ذاكرة)
    concat_list_file = episode_dir / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for p in generated_scene_files:
            f.write(f"file '{p.resolve().as_posix()}'\n")

    merged_raw = episode_dir / "merged_raw.mp4"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # دمج متسلسل مباشر دون إعادة ضغط (Lossless Stream Copy)
    cmd_concat = [
        ffmpeg_exe, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(merged_raw)
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. تركيب الموسيقى التصويرية الكارتونية والمؤثرات
    final_output = episode_dir / f"{_safe_name(title)}_كاملة.mp4"
    bgm_file = SFX_DIR / "funny_bgm.wav"

    if bgm_file.exists():
        cmd_audio = [
            ffmpeg_exe, "-y",
            "-i", str(merged_raw),
            "-stream_loop", "-1",
            "-i", str(bgm_file),
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(final_output)
        ]
        subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        final_output = merged_raw

    progress(f"✅ اكتمل إنتاج الحلقة الطويلة بنجاح! جاهزة للنشر على يوتيوب! 🏆")
    return final_output
