""" Editor Agent  يجمع الصور والصوت والترجمة في فيديو نهائي."""
from pathlib import Path
from tools.video_tool import assemble_video


def run(
    scenes: list[dict],
    output_path: Path,
    main_lang: str = "ar",
    on_progress=None,
) -> Path:
    """ادمج كل المشاهد في فيديو MP4 نهائي."""
    if on_progress:
        on_progress(" المونتير يجمع المشاهد...")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = assemble_video(
        scenes=scenes,
        output_path=output_path,
        main_lang=main_lang,
    )

    if on_progress:
        on_progress(f" الفيديو جاهز! ({result.stat().st_size // 1024} KB)")

    return result
