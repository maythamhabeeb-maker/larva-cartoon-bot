""" Director Agent  يحلل الطلب ويضع خطة الإنتاج."""
from tools.gemini_tool import generate_json


DIRECTOR_PROMPT = """
أنت مخرج قصص أطفال كرتونية محترف.
المستخدم يريد قصة كرتونية.

الطلب: {idea}
عدد المشاهد المطلوب: {scene_count}
اللغة الرئيسية: {main_lang}
لغة الترجمة: {sub_lang}

قم بتحليل الطلب وأعد JSON بهذا الشكل بالضبط:
{{
  "title_ar": "عنوان القصة بالعربية",
  "title_en": "Story title in English",
  "genre": "educational|adventure|comedy|moral",
  "characters": ["شخصية 1", "شخصية 2"],
  "setting": "وصف المكان والزمان",
  "moral": "الدرس أو القيمة من القصة",
  "visual_style": "وصف الأسلوب البصري الكرتوني بالإنجليزي",
  "scene_count": {scene_count},
  "main_lang": "{main_lang}",
  "sub_lang": "{sub_lang}"
}}
"""


def run(
    idea: str,
    scene_count: int = 5,
    main_lang: str = "ar",
    sub_lang: str = "en",
    on_progress=None,
) -> dict:
    """حلّل الفكرة وأعد خطة الإنتاج."""
    if on_progress:
        on_progress(" المخرج يحلل الفكرة...")

    prompt = DIRECTOR_PROMPT.format(
        idea=idea,
        scene_count=scene_count,
        main_lang=main_lang,
        sub_lang=sub_lang,
    )
    plan = generate_json(prompt)

    if on_progress:
        on_progress(f" خطة جاهزة: {plan.get('title_ar', '')}  {plan.get('scene_count', scene_count)} مشاهد")

    return plan
