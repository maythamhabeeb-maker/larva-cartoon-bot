"""أداة المونتاج السينمائي - دمج صور المشاهد الـ 3D فائقة الوضوح مع الصوت والترجمة."""
from pathlib import Path
from typing import List

from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    TextClip,
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, FONT_SIZE, SUBTITLE_PAD

def _make_scene_clip(
    image_path: Path,
    audio_path: Path,
    text_ar: str,
    text_en: str,
    main_lang: str,
) -> CompositeVideoClip:
    """بناء مقطع المشهد بصورة 3D واضحة مع الصوت والترجمة."""
    audio = AudioFileClip(str(audio_path))
    duration = audio.duration

    # الصورة الكارتونية 3D فائقة الدقة
    image_clip = (
        ImageClip(str(image_path))
        .with_duration(duration)
        .resized((VIDEO_WIDTH, VIDEO_HEIGHT))
    )

    layers: list = [image_clip]

    # الترجمة العربية
    try:
        sub_ar = (
            TextClip(
                text=text_ar,
                font_size=FONT_SIZE,
                color="white",
                stroke_color="black",
                stroke_width=2,
                method="caption",
                size=(VIDEO_WIDTH - 100, None),
                text_align="center",
            )
            .with_duration(duration)
            .with_position(("center", VIDEO_HEIGHT - FONT_SIZE * 2 - SUBTITLE_PAD))
        )
        layers.append(sub_ar)
    except Exception:
        pass

    # الترجمة الإنكليزية
    try:
        sub_en = (
            TextClip(
                text=text_en,
                font_size=FONT_SIZE - 4,
                color="yellow",
                stroke_color="black",
                stroke_width=1,
                method="caption",
                size=(VIDEO_WIDTH - 100, None),
                text_align="center",
            )
            .with_duration(duration)
            .with_position(("center", SUBTITLE_PAD))
        )
        layers.append(sub_en)
    except Exception:
        pass

    composite = CompositeVideoClip(layers, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    composite = composite.with_audio(audio)
    return composite

def assemble_video(
    scenes: List[dict],
    output_path: Path,
    main_lang: str = "ar",
) -> Path:
    """دمج كل مشاهد الصور الـ 3D مع الأصوات في فيديو MP4 متكامل."""
    clips = []
    for scene in scenes:
        clip = _make_scene_clip(
            image_path=Path(scene["image_path"]),
            audio_path=Path(scene["audio_path"]),
            text_ar=scene["text_ar"],
            text_en=scene["text_en"],
            main_lang=main_lang,
        )
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        str(output_path),
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(output_path.parent / "temp_audio.m4a"),
        remove_temp=True,
        logger=None,
    )
    return output_path
