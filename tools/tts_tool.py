"""أداة تحويل النص إلى صوت باستخدام gTTS."""
from pathlib import Path
from gtts import gTTS


LANG_MAP = {
    "ar": "ar",   # عربي
    "en": "en",   # إنجليزي
}


def text_to_speech(text: str, lang: str, output_path: Path) -> Path:
    """حوّل نصاً إلى ملف صوتي MP3.
    
    Args:
        text:        النص المراد تحويله
        lang:        رمز اللغة: 'ar' أو 'en'
        output_path: مسار حفظ ملف MP3
    
    Returns:
        مسار الملف الصوتي المحفوظ
    """
    gtts_lang = LANG_MAP.get(lang, "ar")
    tts = gTTS(text=text, lang=gtts_lang, slow=False)
    tts.save(str(output_path))
    return output_path
