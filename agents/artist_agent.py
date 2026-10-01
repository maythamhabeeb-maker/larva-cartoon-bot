"""Artist Agent - توليد صور كارتونية سينمائية فائقة الوضوح 3D مشهد بمشهد."""
from pathlib import Path
from tools.gemini_tool import generate_cartoon_image

def run(
    scenes: list[dict],
    output_dir: Path,
    on_progress=None,
) -> list[dict]:
    """توليد صور 3D فائقة الوضوح والنقاء لكل مشهد."""
    output_dir.mkdir(parents=True, exist_ok=True)
    total = len(scenes)

    for i, scene in enumerate(scenes, 1):
        if on_progress:
            on_progress(f"🎨 جاري رسم المشهد {i}/{total} بجودة سينمائية 3D فائقة...")

        img_path = output_dir / f"scene_{i:02d}.png"
        generate_cartoon_image(
            prompt=scene["visual_prompt"],
            output_path=img_path,
            scene_index=i - 1,
        )
        scene["image_path"] = str(img_path)

    if on_progress:
        on_progress(f"✅ تم الانتهاء من رسم {total} مشاهد فائقة النقاء والوضوح!")

    return scenes
