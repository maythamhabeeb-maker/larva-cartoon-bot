"""Slapstick Agent - وكيل الكوميديا الكارتونية الصامتة (أسلوب كارتون لارفا Larva).
يبتكر مقالب كوميدية صامتة وسريعة تعتمد بالكامل على الحركة والمؤثرات الصوتية بدون أي كلام.
"""
import sys
import io
import json
import logging
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.gemini_tool import generate_json

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

DEFAULT_CHARACTERS = (
    "ZOOMY (الصرصور زوومي): a super cute, goofy cartoon cockroach with warm shiny golden-amber vinyl shell, "
    "huge round bulging cartoon googly eyes, two long springy flexible antennae, silly wide grin, six tiny adorable legs. Clumsy, curious, food-obsessed, running and slipping on the floor.\n"
    "BAZZOUZ (الذبابة بزّوز): a chubby spherical fat cartoon fly with iridescent metallic sapphire-blue body, "
    "tiny translucent buzzing wings, big expressive magenta-red goggle eyes, hilarious cranky pout expression. Easily annoyed, hovers and buzzes around with erratic funny flight."
)

WORLD_SETTING = (
    "Underground concrete storm drain and sewer gutter, metal street grate ceiling with golden daylight shafts streaming down, "
    "giant discarded soda bottle caps used as shields or bowls, rusty colorful tin cans, mossy concrete floor, water puddles, "
    "food crumbs and snacks dropped from the street above. 3D Pixar & Larva slapstick claymation aesthetic, "
    "vibrant saturated colors, glossy vinyl textures, cinematic studio lighting."
)

def create_slapstick_episode(idea: str = None, shot_count: int = 7, on_progress=None) -> dict:
    if on_progress:
        on_progress(f"🧠 تأليف سيناريو مقلب طويل ومتكامل ({shot_count} لقطات خاطفة)...")
        
    prompt = f"""
أنت مخرج ومؤلف حلقات الرسوم المتحركة الكوميدية الصامتة الهزلية المشهورة مثل كارتون لارفا (Larva) ومستر بين وتوم وجيري.
الشخصيات الرئيسية:
{DEFAULT_CHARACTERS}
البيئة:
{WORLD_SETTING}

المطلوب:
ابتكار حلقة كارتونية كوميدية صامتة سريعة كاملة الأحداث والمقالب بين (الصرصور زوومي) و(الذبابة بزّوز)، مقسمة إلى {shot_count} لقطات سريعة وخاطفة (كل لقطة من 0.8 إلى 1.3 ثانية).
{"الفكرة المقترحة: " + idea if idea else "ابتكر مقلباً عشوائياً مضحكاً جداً بين زوومي وبزّوز (مثلاً: شجار على حبة فستق، علكة لاصقة، غطاء بيبسي طائر، كبريت يشتعل، قطرة ليمون حامضة)."}

تسلسل الأحداث الكوميدي المضحك ({shot_count} لقطات):
1. البداية: زوومي أو بزّوز يعثر على كنز (أكل أو أداة غريبة).
2. التحدي: محاولة خطف الشيء والتنافس الهزلي.
3. المطاردة: قفزة زنبركية أو طيران سريع.
4. المفاجأة والمقلب: فخ أو حركة تنقلب بالعكس.
5. الارتطام القوي: صدمة عنيفة مضحكة (بقوطية، حائط، أو أرضية).
6. السقوط المتدحرج: انزلاق أو تدحرج الاثنين معاً.
7. النهاية الهزلية: نظرة ذهول ودوخة مع نجوم تدور وعيون مضحكة.

قوانين الحلقة الصامتة:
1. ممنوع أي كلام أو حوار نهائياً (No talking or dialogue).
2. الضحك يعتمد 100% على الحركة السريعة (Slapstick physics) والمؤثرات الصوتية.
3. كل لقطة ترتبط بمؤثر صوتي كارتوني: "boing", "splat", "bonk", "whistle_fall", "pop", "gasp".

أعد النتيجة حصراً بصيغة JSON بالتنسيق التالي:
{{
  "title_ar": "عنوان مضحك للحلقة بالعربي",
  "shots": [
    {{
      "shot_index": 1,
      "duration": 1.1,
      "camera_motion": "punch",
      "action_summary": "وصف دقيق للحركة الكوميدية في هذه اللقطة",
      "sfx_cue": "gasp",
      "sfx_time": 0.1,
      "image_prompt": "Ultra-detailed 3D Pixar Larva cartoon style shot of Zoomy the cute goofy golden cockroach and Bazzouz the chubby blue fly in the wet sewer gutter, looking shocked at a shiny golden potato chip, cinematic lighting, glossy textures, expressive wide open eyes, vertical 9:16 composition"
    }}
  ]
}}
"""
    result = generate_json(prompt)
    if on_progress:
        title = result.get("title_ar", "مقلب كارتوني")
        shots_count = len(result.get("shots", []))
        on_progress(f"✅ تم تأليف الحلقة: «{title}» ({shots_count} لقطات كوميدية)")
    return result

if __name__ == "__main__":
    ep = create_slapstick_episode("شجار على قطعة شيبس مقرمشة")
    print(json.dumps(ep, ensure_ascii=False, indent=2))
