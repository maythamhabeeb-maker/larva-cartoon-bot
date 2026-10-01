"""Cartoon Pipeline - خط الإنتاج والمونتاج الكارتوني الكامل فائق الوضوح."""
import re
from pathlib import Path
from config import OUTPUT_DIR, DEFAULT_MAIN_LANG, DEFAULT_SUB_LANG
from agents import director_agent, script_agent, artist_agent, narrator_agent, editor_agent

def _safe_name(text: str) -> str:
    text = re.sub(r"[^\w\u0600-\u06FF\s-]", "", text)
    return text.strip().replace(" ", "_")[:35]

def run(
    idea: str,
    scene_count: int = 4,
    main_lang: str = DEFAULT_MAIN_LANG,
    sub_lang: str = DEFAULT_SUB_LANG,
    on_progress=None,
) -> Path:
    def progress(msg: str):
        print(f"  {msg}")
        if on_progress:
            on_progress(msg)

    # 1. المخرج يحلل الفكرة
    plan = director_agent.run(
        idea=idea,
        scene_count=scene_count,
        main_lang=main_lang,
        sub_lang=sub_lang,
        on_progress=progress,
    )

    story_dir = OUTPUT_DIR / _safe_name(plan.get("title_ar", idea))
    story_dir.mkdir(parents=True, exist_ok=True)

    # 2. كاتب السيناريو يكتب المشاهد
    scenes = script_agent.run(plan=plan, on_progress=progress)

    # 3. الرسام يولد صور 3D فائقة الوضوح من جيمني
    scenes = artist_agent.run(
        scenes=scenes,
        output_dir=story_dir,
        on_progress=progress,
    )

    # 4. المؤدي الصوتي يسجل الصوت العربي
    scenes = narrator_agent.run(
        scenes=scenes,
        output_dir=story_dir,
        main_lang=main_lang,
        on_progress=progress,
    )

    # 5. المونتير يدمج كل المشاهد وينتج فيديو MP4 كامل
    video_filename = f"{_safe_name(plan.get('title_ar', idea))}.mp4"
    video_path = story_dir / video_filename
    final_video = editor_agent.run(
        scenes=scenes,
        output_path=video_path,
        main_lang=main_lang,
        on_progress=progress,
    )

    progress(f"🎉 تم اكتمال مونتاج الفيديو بنجاح! المسار: {final_video}")
    return final_video
