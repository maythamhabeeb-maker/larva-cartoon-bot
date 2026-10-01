"""Slapstick Pipeline - خط إنتاج كارتون لارفا الكوميدي الصامت ثلاثي الأبعاد مع المؤثرات الصوتية الكاملة."""
import sys
import io
import re
import logging
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import OUTPUT_DIR
from agents import slapstick_agent
from tools.gemini_tool import generate_larva_image
from tools.slapstick_editor import build_slapstick_video

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

def _safe_name(text: str) -> str:
    text = re.sub(r"[^\w\u0600-\u06FF\s-]", "", text)
    return text.strip().replace(" ", "_")[:35]

def run_slapstick_pipeline(idea: str = None, shot_count: int = 7, on_progress=None) -> Path:
    """
    إنتاج حلقة كارتونية كوميدية صامتة بأسلوب لارفا (Larva) مع المؤثرات الصوتية وبدون أي كلام.
    """
    def progress(msg: str):
        print(f"  {msg}")
        if on_progress:
            on_progress(msg)

    # 1. تأليف السيناريو الهزلي والمقالب الكوميدية
    episode_plan = slapstick_agent.create_slapstick_episode(idea=idea, shot_count=shot_count, on_progress=progress)
    title = episode_plan.get("title_ar", "مقلب_لارفا")
    shots = episode_plan.get("shots", [])

    episode_dir = OUTPUT_DIR / f"larva_{_safe_name(title)}"
    episode_dir.mkdir(parents=True, exist_ok=True)

    # 2. توليد لقطات الرسوم المتحركة 3D لستايل لارفا
    shots_data = []
    for i, shot in enumerate(shots):
        prompt = shot.get("image_prompt", "")
        img_path = episode_dir / f"shot_{i+1}.png"
        progress(f"🎨 رسم وتجسيد اللقطة {i+1}/{len(shots)}: 3D Larva...")
        
        try:
            generate_larva_image(prompt=prompt, output_path=img_path, shot_index=i)
        except Exception as e:
            logger.error(f"Error generating shot {i+1}: {e}")
            # إذا فشل، إعادة المحاولة بصيغة مبسطة
            fallback_prompt = f"3D Pixar cartoon of yellow and red caterpillar in sewer, comedic action: {shot.get('action_summary', '')}"
            generate_larva_image(prompt=fallback_prompt, output_path=img_path, shot_index=i)

        shots_data.append({
            "image_path": img_path,
            "duration": shot.get("duration", 2.5),
            "sfx_cue": shot.get("sfx_cue", "boing"),
            "sfx_time": shot.get("sfx_time", 0.4),
            "camera_motion": shot.get("camera_motion", "zoom_in"),
        })

    # 3. المونتاج وتركيب المؤثرات الصوتية والموسيقى بدون أي كلام
    video_filename = f"{_safe_name(title)}.mp4"
    final_video_path = episode_dir / video_filename
    
    final_video = build_slapstick_video(
        shots_data=shots_data,
        output_path=final_video_path,
        on_progress=progress
    )

    return final_video

if __name__ == "__main__":
    vid = run_slapstick_pipeline("شجار مضحك على علكة لاصقة")
    print(f"🎬 Video produced at: {vid}")
