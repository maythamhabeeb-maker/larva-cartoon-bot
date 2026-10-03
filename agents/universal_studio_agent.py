"""Universal Studio Agent - العقل المدبر ومخرج الاستوديو الكارتوني الشامل بالذكاء الاصطناعي.
يقوم بتحويل أي فكرة (كارتون صامت، مغامرات، عوالم أفاتار، قصص دينية أو تاريخية، كارتون أطفال)
إلى إنتاج سينمائي ثلاثي المراحل:
المرحلة 1: خلق وتثبيت هوية الشخصيات (Character Design & Consistency).
المرحلة 2: تأليف وتوزيع المشاهد المتسلسلة (Storyboard & Visual Prompts).
المرحلة 3: إعداد هندسة الصوت والمؤثرات المتناسقة مع النمط (Audio & Foley Directing).
"""
import sys
import io
import json
import logging
from typing import Dict, Any
from tools.gemini_tool import generate_json

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

SYSTEM_DIRECTOR_PROMPT = """
You are an Executive Animation Director and Showrunner at an Elite Global 3D Animation Studio (Pixar, Disney, DreamWorks, Illumination).
Your mission is to transform any user idea into a complete, professional 3-Tier Production Plan for an animated short episode.

The user idea may be:
- Slapstick Silent Cartoon (like Larva, Tom & Jerry, Mr. Bean) with physical gags, funny Foley sounds, and zero dialogue.
- Fantasy & Adventure (like Dragon & Owl, magical quest, forest journeys).
- Avatar & Sci-Fi (alien worlds, glowing bioluminescent fauna, flying creatures).
- Moral, Religious or Historic Tales (reverent lighting, desert or ancient cities, inspiring narrative).
- Cute Animal & Kids Cartoon (Pixar puppies, kittens, charming playful characters).

Analyze the user's idea and generate a strictly valid JSON response with the following structure:
{
  "title_ar": "عنوان الحلقة أو القصة بالعربي",
  "synopsis_ar": "ملخص القصة في سطرين",
  "genre": "slapstick | adventure | fantasy_avatar | historical_moral | cute_cartoon",
  "audio_mood": "funny_slapstick | whimsical_adventure | epic_fantasy | calm_inspiring",
  "characters": [
    {
      "name_ar": "اسم الشخصية بالعربي",
      "name_en": "English Name",
      "visual_identity": "Extremely detailed physical 3D Pixar description: exact species/nature, scale, skin/fur/scales texture, color palette, eye shape and color, clothing or accessories, distinctive cute quirks to maintain 100% visual consistency across all scenes."
    }
  ],
  "setting_en": "Cinematic visual description of the world, architecture/nature, color temperature, atmospheric lighting (e.g. golden hour, bioluminescent night, bright sunlit sewer).",
  "scenes": [
    {
      "scene_num": 1,
      "act": "المقدمة والافتتاحية",
      "action_ar": "وصف ما تفعله الشخصيات في هذا المشهد بالعربي",
      "visual_prompt_en": "Masterpiece 3D CGI animated shot in Pixar/Disney style: (combine the exact character visual identities above, the environment, dynamic action, facial expressions, camera movement, and volumetric lighting)",
      "dialogue_ar": "الحوار أو الجملة التي تنطق بها الشخصية بالعربي، أو تركه فارغاً إذا كان المشهد صامت ومقلب",
      "sfx_cue": "whoosh / boing / bonk / splat / flutter / spark / gasp / whistle",
      "duration": 5.0
    }
  ]
}

Rules:
1. When generating a full movie or episode, generate exactly 5 continuous scenes that tell an engaging, complete story arc (1: Opening & meeting heroes, 2: Discovery, 3: Rising curiosity & gag, 4: Climax action, 5: Celebration & happy ending).
2. Character consistency: Every scene's `visual_prompt_en` must explicitly repeat the exact character traits established in `characters`.
3. If it's a silent slapstick cartoon (like Larva / Tom & Jerry), leave `dialogue_ar` empty and emphasize funny physical squash-and-stretch comedy and SFX cues. If dialogue/story is requested, write warm, natural Arabic dialogue in `dialogue_ar`.
4. Output ONLY valid JSON, no markdown outside or explanatory text.
"""

def create_universal_production_plan(idea: str = None, on_progress=None) -> Dict[str, Any]:
    """تأليف خطة إنتاج الحلقة الكارتونية المتكاملة بمراحلها الثلاث (الشخصيات 👈 المشاهد 👈 الصوتيات)."""
    clean_idea = (idea or "مقلب كارتوني مضحك بين شخصيتين كارتونيتين").strip()
    
    if on_progress:
        on_progress("🧠 المخرج السينمائي يحلل الفكرة ويصمم هوية الشخصيات وعالم القصة...")

    full_prompt = f"{SYSTEM_DIRECTOR_PROMPT}\n\nUser Idea to produce:\n{clean_idea}"
    
    try:
        data = generate_json(full_prompt)
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
            
        # Basic validation
        if not data.get("scenes") or not data.get("characters"):
            raise ValueError("Incomplete production plan received.")
            
        logger.info(f"Generated universal plan: {data.get('title_ar')} ({data.get('genre')})")
        return data

    except Exception as e:
        logger.error(f"Error generating universal production plan: {e}")
        # Default fallback plan (Zoomy & Bazzouz slapstick)
        return {
            "title_ar": "مغامرة زوومي وبزّوز الكوميدية",
            "synopsis_ar": "شجار هزلي مضحك ومقالب في المجاري بين الصرصور الذهبي والذبابة الزرقاء",
            "genre": "slapstick",
            "audio_mood": "funny_slapstick",
            "characters": [
                {
                    "name_ar": "زوومي",
                    "name_en": "Zoomy",
                    "visual_identity": "Goofy glossy amber-golden cartoon cockroach, oversized round googly eyes, springy antennae, silly toothy grin, shiny shell."
                },
                {
                    "name_ar": "بزّوز",
                    "name_en": "Bazzouz",
                    "visual_identity": "Chubby metallic electric-blue fly, oversized comic red aviator goggles, tiny fluttering translucent wings, chubby round body."
                }
            ],
            "setting_en": "A damp concrete urban sewer floor illuminated by golden sunbeams piercing through an overhead iron grate, scattered with shiny soda cans and colorful bottle caps.",
            "scenes": [
                {
                    "scene_num": 1,
                    "act": "البداية واكتشاف الكنز",
                    "action_ar": "زوومي يكتشف قطعة طعام كبيرة تلمع تحت أشعة الشمس في المجاري ويفرح بها",
                    "visual_prompt_en": "Masterpiece 3D CGI Pixar cartoon animation: goofy golden cockroach Zoomy with oversized bulging eyes discovering a huge glowing slice of food on sunlit sewer concrete, smiling excitedly with bouncing springy antennae.",
                    "sfx_cue": "gasp",
                    "duration": 6.0
                },
                {
                    "scene_num": 2,
                    "act": "هجوم المنافس وبدء الصراع",
                    "action_ar": "بزّوز الذبابة الزرقاء تهجم بسرعة البرق وتخطف طرف الطعام ويبدأ الشجار",
                    "visual_prompt_en": "Masterpiece 3D CGI cartoon: chubby blue fly Bazzouz with red goggles dive-bombing fast from above like a tiny fighter jet, grabbing the edge of the food, fast funny slapstick flight motion.",
                    "sfx_cue": "whoosh",
                    "duration": 6.0
                },
                {
                    "scene_num": 3,
                    "act": "ذروة المقلب والمفارقة",
                    "action_ar": "شد وجذب مضحك والجبن يمتد كالمطاط وينقطع فجأة وتتطاير الشخصيات وتصطدم بقواطي البيبسي",
                    "visual_prompt_en": "Masterpiece 3D slapstick physical comedy: Zoomy and Bazzouz pulling opposite sides, cheese stretches elastic like rubber, snaps back launching both characters crashing into soda tin cans with denting impacts.",
                    "sfx_cue": "bonk",
                    "duration": 6.0
                },
                {
                    "scene_num": 4,
                    "act": "النهاية الكوميدية",
                    "action_ar": "كلاهما ينظران للكاميرا بوجه مضحك ومصدوم بعد فوات الأوان",
                    "visual_prompt_en": "Masterpiece 3D Pixar Larva cartoon: Zoomy the cockroach and Bazzouz the blue fly sitting dizzy with swirling stars around heads, staring blankly at camera with hilarious shocked expressions.",
                    "sfx_cue": "whistle",
                    "duration": 6.0
                }
            ]
        }
