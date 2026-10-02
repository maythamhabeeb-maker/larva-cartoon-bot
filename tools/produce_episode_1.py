"""Produce Episode 1: مقلب العلكة اللاصقة بين زوومي وبزّوز
فيديو حركة 3D حقيقية كاملة عبر محرك MiniMax / Hailuo مع تركيب المؤثرات الصوتية والموسيقى الكارتونية.
"""
import sys
import io
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.replicate_video_tool import generate_video_minimax
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx import MultiplyVolume

def produce_bubblegum_episode():
    prompt = (
        "Masterpiece 3D CGI animated slapstick cartoon scene in Pixar and Larva style: "
        "Zoomy, a cute goofy golden cartoon cockroach with big round googly eyes, discovers a sticky gooey pink bubblegum "
        "on the damp concrete sewer floor next to giant soda cans. He pulls the pink gum, stretching it like an elastic rubber band. "
        "The gum violently snaps back, slapping Zoomy squarely on the face and launching him backwards flying through the air into "
        "Bazzouz the chubby metallic blue fly hovering nearby, hilarious physical comedy, fluid 3D character animation, vivid colors."
    )
    
    print("🚀 بدء إنتاج الحلقة 1: «مقلب العلكة اللاصقة» عبر محرك MiniMax...")
    raw_video = generate_video_minimax(prompt=prompt, on_progress=print)
    
    print("✂️ تركيب هندسة الصوت الكارتونية (موسيقى + بويينغ + طراااخ)...")
    clip = VideoFileClip(str(raw_video))
    dur = clip.duration
    
    sfx_dir = PROJECT_ROOT / "assets" / "sfx"
    bgm = AudioFileClip(str(sfx_dir / "funny_bgm.wav")).subclipped(0, min(dur, 12.0)).with_effects([MultiplyVolume(0.4)])
    
    # أصوات متزامنة مع حركات المقلب
    stretch_boing = AudioFileClip(str(sfx_dir / "boing.wav")).with_start(1.2)
    snap_splat = AudioFileClip(str(sfx_dir / "splat.wav")).with_start(3.2)
    bonk_crash = AudioFileClip(str(sfx_dir / "bonk.wav")).with_start(4.5)
    
    composite_audio = CompositeAudioClip([bgm, stretch_boing, snap_splat, bonk_crash])
    final_video = clip.with_audio(composite_audio)
    
    out_path = PROJECT_ROOT / "output" / "episode_1_bubblegum_slapstick.mp4"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("🎬 جاري رندر وتصدير الفيديو النهائي عالي الدقة...")
    final_video.write_videofile(
        str(out_path),
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )
    
    try:
        final_video.close()
        clip.close()
    except Exception:
        pass
        
    print(f"🎉 اكتمل إنتاج الحلقة بنجاح! المسار:\n{out_path}")
    return out_path

if __name__ == "__main__":
    produce_bubblegum_episode()
