""" Narrator Agent  يحول نص كل مشهد إلى ملف صوتي."""
from pathlib import Path
from tools.tts_tool import text_to_speech


def run(
    scenes: list[dict],
    output_dir: Path,
    main_lang: str = "ar",
    on_progress=None,
) -> list[dict]:
    """حوّل نص كل مشهد إلى MP3.
    
    يضيف مفتاح 'audio_path' لكل مشهد.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    total = len(scenes)

    for i, scene in enumerate(scenes, 1):
        if on_progress:
            on_progress(f" تسجيل صوت المشهد {i}/{total}...")

        # اختر النص حسب اللغة الرئيسية
        text = scene["text_ar"] if main_lang == "ar" else scene["text_en"]
        audio_path = output_dir / f"scene_{i:02d}.mp3"
        text_to_speech(text=text, lang=main_lang, output_path=audio_path)
        scene["audio_path"] = str(audio_path)

    if on_progress:
        on_progress(f" تم تسجيل {total} مقاطع صوتية")

    return scenes
