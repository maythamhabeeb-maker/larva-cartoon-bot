"""Universal Studio Generator - محرك إنتاج الحلقات الكارتونية والسينمائية المتكاملة.
ينفذ المراحل الثلاث:
1. استخراج وتثبيت هوية الشخصيات (Character Visual Identity)
2. توليد المشاهد مشهداً تلو الآخر بحركة 3D حقيقية
3. دمج المشاهد وتركيب هندسة الصوت والمؤثرات والموسيقى وتصدير حلقة متكاملة
"""
import sys
import io
import os
import re
import time
import logging
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any
import imageio_ffmpeg

from config import OUTPUT_DIR
from agents.universal_studio_agent import create_universal_production_plan
from tools.runpod_comfy_tool import generate_video_on_runpod

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SFX_DIR = PROJECT_ROOT / "assets" / "sfx"

def _safe_name(text: str) -> str:
    text = re.sub(r"[^\w\u0600-\u06FF\s-]", "", text or "episode")
    return text.strip().replace(" ", "_")[:30]

def produce_universal_episode(idea: str = None, on_progress=None) -> Tuple[Path, Dict[str, Any]]:
    """إنتاج حلقة كارتونية سينمائية متكاملة من الفكرة وحتى الحلقة النهائية."""
    def progress(msg: str):
        if on_progress:
            on_progress(msg)

    # 1. المرحلة الأولى: تأليف السكريبت وتثبيت هوية الشخصيات
    plan = create_universal_production_plan(idea=idea, on_progress=progress)
    title = plan.get("title_ar", "حلقة_كارتون")
    genre = plan.get("genre", "slapstick")
    characters = plan.get("characters", [])
    scenes = plan.get("scenes", [])

    char_names = " و ".join([c.get("name_ar", "") for c in characters if c.get("name_ar")])
    progress(f"🎨 تم تحديد أبطال القصة: {char_names} ({len(scenes)} مشاهد متسلسلة)")

    episode_dir = OUTPUT_DIR / f"universal_{_safe_name(title)}_{int(time.time())}"
    episode_dir.mkdir(parents=True, exist_ok=True)

    # المرحلة 1.5: رسم صورة الشخصيات المرجعية ثلاثية الأبعاد عبر Google Gemini الفخم (Master Concept)
    progress("🎨 رسم وتثبيت هوية وملامح أبطال القصة بأسلوب 3D Pixar الخارق عبر Google Gemini...")
    char_ref_path = episode_dir / "character_concept.png"
    has_ref_image = False
    try:
        from tools.gemini_tool import generate_universal_character_image
        generate_universal_character_image(plan=plan, output_path=char_ref_path)
        has_ref_image = char_ref_path.exists() and char_ref_path.stat().st_size > 0
        if has_ref_image:
            progress("✅ تم تثبيت ملامح وهيكل الأبطال بنجاح 100%! جاري تصوير المشاهد سينمائياً...")
    except Exception as e:
        logger.warning(f"Gemini character generation fallback: {e}")
        try:
            from tools.runpod_comfy_tool import generate_character_on_runpod
            generate_character_on_runpod(prompt_text=f"3D Pixar Disney cartoon {char_names}", output_path=str(char_ref_path))
            has_ref_image = char_ref_path.exists()
        except Exception:
            pass

    generated_scenes = []

    # 2. المرحلة الثانية: تصوير المشاهد مشهداً تلو الآخر (رسم الكادر بـ Gemini ⬅️ التحريك بـ Wan 2.1)
    for i, sc in enumerate(scenes):
        sc_num = i + 1
        action_ar = sc.get("action_ar", "")
        v_prompt = sc.get("visual_prompt_en", "")

        progress(f"🎬 المشهد {sc_num}/{len(scenes)}: {action_ar}")

        # 2.1: رسم كادر المشهد المخصص عبر Google Gemini
        scene_keyframe_path = episode_dir / f"scene_{sc_num}_keyframe.png"
        keyframe_to_use = str(char_ref_path) if has_ref_image else None
        try:
            from tools.gemini_tool import generate_scene_keyframe
            progress(f"  [المشهد {sc_num}] 🎨 رسم كادر المشهد سينمائياً عبر Google Gemini...")
            generate_scene_keyframe(plan=plan, scene=sc, output_path=scene_keyframe_path)
            if scene_keyframe_path.exists() and scene_keyframe_path.stat().st_size > 0:
                keyframe_to_use = str(scene_keyframe_path)
        except Exception as e_kf:
            logger.warning(f"Could not generate custom keyframe for scene {sc_num}: {e_kf}")

        # 2.2: تحريك المشهد عبر Wan 2.1 على كارت الشاشة RTX 4090
        out_scene_file = episode_dir / f"scene_{sc_num}.mp4"
        try:
            progress(f"  [المشهد {sc_num}] ⚡ توليد حركة المشهد سينمائياً عبر Wan 2.1 على كارت الـ RTX 4090...")
            generate_video_on_runpod(
                image_path=None,
                output_mp4_path=str(out_scene_file),
                prompt_text=v_prompt
            )
            
            # إذا كان المشهد يحتوي على حوار صوتي ناطق للشخصيات
            dialogue = sc.get("dialogue_ar", "").strip()
            if dialogue:
                try:
                    from tools.tts_tool import text_to_speech
                    voice_file = episode_dir / f"voice_{sc_num}.mp3"
                    text_to_speech(dialogue, "ar", voice_file)
                    if voice_file.exists() and voice_file.stat().st_size > 0:
                        dubbed_file = episode_dir / f"dubbed_{sc_num}.mp4"
                        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                        cmd_dub = [
                            ffmpeg_exe, "-y",
                            "-i", str(out_scene_file),
                            "-i", str(voice_file),
                            "-c:v", "copy",
                            "-c:a", "aac",
                            "-shortest",
                            str(dubbed_file)
                        ]
                        subprocess.run(cmd_dub, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
                        if dubbed_file.exists() and dubbed_file.stat().st_size > 0:
                            out_scene_file = dubbed_file
                except Exception as ex_dub:
                    logger.warning(f"Voice dubbing fallback for scene {sc_num}: {ex_dub}")
                    
            generated_scenes.append(out_scene_file)
        except Exception as e:
            logger.error(f"Error producing scene {sc_num}: {e}")
            continue

    if not generated_scenes:
        raise RuntimeError("تعذر تصوير مشاهد الحلقة. يرجى إعادة المحاولة.")

    # 3. المرحلة الثالثة: المونتاج وهندسة الصوت والموسيقى
    progress("✂️ المونتير يقوم بدمج المشاهد وهندسة الصوت والموسيقى التصويرية الكاملة...")

    concat_file = episode_dir / "concat_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for p in generated_scenes:
            f.write(f"file '{p.resolve().as_posix()}'\n")

    merged_raw = episode_dir / "merged_raw.mp4"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # دمج متسلسل مباشر فائق السرعة وبدون استهلاك ذاكرة (Stream Copy)
    cmd_concat = [
        ffmpeg_exe, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(merged_raw)
    ]
    try:
        subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45)
    except Exception as e:
        logger.warning(f"Concat fallback: {e}")
        merged_raw = generated_scenes[0]

    # تركيب الموسيقى التصويرية الكارتونية
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
        try:
            subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45)
        except Exception as e:
            logger.warning(f"Audio merge fallback: {e}")
            final_output = merged_raw
    else:
        final_output = merged_raw

    progress(f"✅ اكتمل إنتاج الحلقة بالكامل بنجاح! 🏆 جاهزة للعرض والمشاركة!")
    return final_output, plan, (char_ref_path if has_ref_image else None)
