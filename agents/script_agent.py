"""توجيهات المفكر وكاتب السيناريو المتخصص في قصص الغابة السحرية والستايل الكارتوني 3D الفاخر."""
from tools.gemini_tool import generate_json

DIRECTOR_PROMPT = """
أنت مخرج وكاتب قصص أطفال كارتونية محترف وخبير في هندسة برومبتات الذكاء الاصطناعي بنمط Pixar و Disney Animation ثلاثي الأبعاد.

المستخدم يريد إنتاج فيلم كارتوني سحري حول الفكرة التالية:
الفكرة: {idea}

مهمتك:
1. بناء قصة مشوقة ومؤثرة مقسمة إلى {scene_count} مشاهد متسلسلة بدقة.
2. لكل مشهد:
   - كتابة نص الراوي العربي الفصيح (بسيط، دافئ، ومعبر للأطفال).
   - كتابة الترجمة الإنكليزية الدقيقة.
   - هندسة برومبت بصري إنجليزي فائق التفاصيل (Visual Prompt) متناسق تماماً مع هذا الستايل الساحر المعتمد:
     * نمط 3D كارتوني ديزني وبيكسار.
     * شخصيات حيوانات لطيفة بفرو ناعم ومفصل وتعبيرات وجه معبرة (عيون واسعة بريئة، ابتسامة دافئة).
     * بيئة غابة سحرية أسطورية (أشجار بلوط عملاقة معلقة عليها فوانيس مضيئة، يراعات صفراء مشعة، زهور ملونة متوهجة، إضاءة غروب ذهبية خارقة للأغصان).

أرجع النتيجة بتنسيق JSON حصراً:
{{
  "title_ar": "عنوان القصة بالعربي",
  "title_en": "Story English Title",
  "scenes": [
    {{
      "id": 1,
      "text_ar": "نص الراوي العربي للمشهد الأول",
      "text_en": "English narration for scene 1",
      "visual_prompt": "a cute fluffy lion cub and a clever red fox sitting near an ancient giant oak tree with hanging glowing lanterns, studying a glowing magical treasure map, yellow fireflies in the air, sunset golden hour lighting, Pixar 3d style"
    }}
  ]
}}
"""

def run(plan=None, on_progress=None):
    if on_progress:
        on_progress("🧠 المفكر الذكي يبتكر القصة ويهندس البرومبتات السينمائية...")

    if isinstance(plan, dict):
        idea = plan.get("idea") or plan.get("title_ar") or "قصة سحرية عن الأسد والثعلب"
        count = plan.get("scene_count", 4)
    else:
        idea = str(plan) if plan else "قصة سحرية عن الأسد والثعلب"
        count = 4

    prompt = DIRECTOR_PROMPT.format(idea=idea, scene_count=count)
    story_data = generate_json(prompt)

    scenes = story_data.get("scenes", [])
    if on_progress:
        on_progress(f"✅ المفكر أتم كتابة {len(scenes)} مشاهد وبرومبتات سحرية خارقة!")

    return scenes
