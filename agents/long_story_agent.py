"""Long Story Agent - مؤلف السيناريو والحلقات الطويلة لكارتون لارفا (يوتيوب 3 إلى 5 دقائق).
يقسم الفكرة إلى سيناريو متكامل من مشاهد متعددة مترابطة درامياً وكوميدياً (مقدمة 👈 صراع 👈 مقالب 👈 ذروة 👈 نهاية).
"""
import sys
import io
import json
import logging
from tools.gemini_tool import generate_json

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

CHARACTERS_PROFILE = (
    "ZOOMY (الصرصور زوومي): صرصور كارتوني أهبل ذو لون كهرماني ذهبي لامع، عيون كروية جاحظة ومضحكة، قرون استشعار مرنة كالزنبرك، فضولي وعاشق للأكل ويتزحلق كثيراً.\n"
    "BAZZOUZ (الذبابة بزّوز): ذبابة زرقاء كروية دبدوبة وعصبية بنظارات حمراء، تطير بسرعة وتزنّ وتتعصب وتدخل في شجارات كوميدية."
)

SETTING_PROFILE = (
    "مجاري الشارع الأسمنتية تحت شباك حديدي تسقط منه أشعة الشمس وقواطي البيبسي الفارغة وأغطية القناني الملونة، بأسلوب أفلام بيكسار وكارتون لارفا 3D."
)

def create_long_episode_script(idea: str = None, scene_count: int = 8, on_progress=None) -> dict:
    """تأليف قصة حلقة يوتيوب كارتونية طويلة متكاملة المشاهد والمؤثرات الصوتية."""
    if on_progress:
        on_progress(f"🧠 المخرج يؤلف سيناريو حلقة يوتيوب كاملة ({scene_count} مشاهد كارتونية متسلسلة)...")

    prompt = f"""
أنت مخرج ومؤلف حلقات رسوم متحركة كارتونية عالمية مشهورة بأسلوب كارتون لارفا (Larva) ومستر بين وتوم وجيري.
المطلوب تأليف حلقة كارتونية كوميدية صامتة بدون أي كلام، مكونة من {scene_count} مشاهد متتالية ومترابطة تحكي قصة مقلب كامل من البداية للنهاية.

فكرة الحلقة الأساسية: {idea if idea else 'شجار كارتوني ضخم على قطعة بيتزا ساخنة سقطت من الشارع في المجاري'}

الشخصيات:
{CHARACTERS_PROFILE}

البيئة:
{SETTING_PROFILE}

أرجع نتيجة JSON صحيحة تماماً بهذا التنسيق حصراً:
{{
  "title_ar": "عنوان الحلقة بالعربي",
  "synopsis_ar": "ملخص قصة الحلقة الكوميدية",
  "scenes": [
    {{
      "scene_num": 1,
      "act": "المقدمة والبداية",
      "action_summary_ar": "وصف المشهد بالعربي",
      "visual_prompt_en": "Masterpiece 3D CGI Pixar Larva cartoon animation shot: (detailed English visual description of action)",
      "sfx_cue": "boing/splat/bonk/whistle/pop/gasp",
      "duration": 5.0
    }}
  ]
}}
"""
    try:
        data = generate_json(prompt)
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        return data
    except Exception as e:
        logger.error(f"Error generating long script: {e}")
        # سيناريو افتراضي متكامل
        return {
            "title_ar": "معركة الكنز الذهبي",
            "synopsis_ar": "زوومي وبزّوز يتنافسان على قطعة طعام في المجاري في سلسلة مقالب مضحكة",
            "scenes": [
                {
                    "scene_num": 1,
                    "act": "المقدمة",
                    "action_summary_ar": "زوومي يستيقظ ويكتشف قطعة طعام كبيرة تلمع تحت أشعة الشمس",
                    "visual_prompt_en": "3D Pixar Larva cartoon: cute goofy golden cockroach named Zoomy waking up in sewer, discovering a giant glowing pizza slice, eyes bulging with silly joy",
                    "sfx_cue": "gasp",
                    "duration": 5.0
                },
                {
                    "scene_num": 2,
                    "act": "ظهور الخصم",
                    "action_summary_ar": "بزّوز الذبابة الزرقاء تهجم كالطائرة النفاثة وتخطف طرف الطعام",
                    "visual_prompt_en": "3D Pixar Larva cartoon: chubby blue fly Bazzouz with red goggles dive-bombing fast from above like a jet fighter to steal the food",
                    "sfx_cue": "boing",
                    "duration": 5.0
                },
                {
                    "scene_num": 3,
                    "act": "الشد والجذب",
                    "action_summary_ar": "شد وجذب مضحك والجبن يمتد مترين بينهما",
                    "visual_prompt_en": "3D cartoon slapstick: Zoomy the cockroach pulling one side, Bazzouz the fly flying in reverse pulling the other side, cheese stretching elastic like rubber",
                    "sfx_cue": "boing",
                    "duration": 5.0
                },
                {
                    "scene_num": 4,
                    "act": "المقلب والانفلات",
                    "action_summary_ar": "الجبن ينقطع كالمنجنيق ويرتد بقوة وبزّوز يطير في قوطية بيبسي",
                    "visual_prompt_en": "3D cartoon slapstick impact: elastic food snaps back, Bazzouz gets launched through the air crashing right into an empty soda tin can with a funny dent",
                    "sfx_cue": "bonk",
                    "duration": 5.0
                },
                {
                    "scene_num": 5,
                    "act": "التزحلق الكوميدي",
                    "action_summary_ar": "زوومي يركض فرحان ويتزحلق بقشرة موزة ويطير مثل البولينج",
                    "visual_prompt_en": "3D cartoon comedy: Zoomy running celebrating, slipping wildly on a yellow banana peel, spinning 360 degrees, crashing into colorful bottle caps like bowling pins",
                    "sfx_cue": "splat",
                    "duration": 5.0
                },
                {
                    "scene_num": 6,
                    "act": "الضربة المشتركة",
                    "action_summary_ar": "كلاهما يقفزان بالهواء ويصطدمان وجهاً لوجه",
                    "visual_prompt_en": "3D cartoon: Zoomy and Bazzouz diving simultaneously towards the food, crashing head-to-head in mid-air with cartoon stars circling their heads",
                    "sfx_cue": "bonk",
                    "duration": 5.0
                },
                {
                    "scene_num": 7,
                    "act": "المفارقة غير المتوقعة",
                    "action_summary_ar": "قطرة ماء عملاقة تسقط من السقف وتغرق المكان وتهرب اللقمة مع الماء",
                    "visual_prompt_en": "3D cartoon physical comedy: a giant water droplet drips from sewer pipe above, huge comic splash, washing the food away into a drain hole",
                    "sfx_cue": "splat",
                    "duration": 5.0
                },
                {
                    "scene_num": 8,
                    "act": "النهاية المضحكة",
                    "action_summary_ar": "زوومي وبزّوز ينظران للكاميرا بوجوه مضحكة مصدومة بدون طعام",
                    "visual_prompt_en": "3D Pixar Larva cartoon: Zoomy the golden cockroach and Bazzouz the blue fly sitting drenched on wet concrete, staring blankly at camera with hilarious shocked expressions",
                    "sfx_cue": "whistle_fall",
                    "duration": 5.0
                }
            ]
        }
