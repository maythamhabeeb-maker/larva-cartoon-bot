"""Cartoon SFX Generator & Manager
ينشئ ويوفر مؤثرات صوتية كارتونية مضحكة (Boing, Splat, Bonk, Whistle, Pop, Giggle, Funny BGM)
"""
import sys
import io
import math
import struct
import wave
from pathlib import Path

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SFX_DIR = Path(__file__).resolve().parent.parent / "assets" / "sfx"
SFX_DIR.mkdir(parents=True, exist_ok=True)

def write_wav(filename: Path, samples: list[float], sample_rate: int = 44100):
    with wave.open(str(filename), "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        packed_frames = bytearray()
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            val = int(clamped * 32767)
            packed_frames.extend(struct.pack("<h", val))
        wav_file.writeframes(packed_frames)

def generate_boing(sample_rate=44100, duration=0.6) -> list[float]:
    """صوت قفز كارتوني زمبركي Boing!"""
    total_samples = int(sample_rate * duration)
    samples = []
    phase = 0.0
    for i in range(total_samples):
        t = i / sample_rate
        # Frequency sweeps up from 180Hz to 600Hz with fast wobble vibrato
        f = 180 + (t / duration) * 450 + math.sin(2 * math.pi * 35 * t) * 60
        phase += 2 * math.pi * f / sample_rate
        # Decay envelope
        env = math.exp(-3.5 * t)
        # Add slight harmonics
        s = (math.sin(phase) + 0.3 * math.sin(2 * phase)) * env
        samples.append(s)
    return samples

def generate_splat(sample_rate=44100, duration=0.5) -> list[float]:
    """صوت ارتطام أو سحق مضحك Splat / Slap!"""
    import random
    total_samples = int(sample_rate * duration)
    samples = []
    phase = 0.0
    for i in range(total_samples):
        t = i / sample_rate
        # Low frequency thump that quickly drops
        f = 120 * math.exp(-15 * t)
        phase += 2 * math.pi * f / sample_rate
        # Noise burst for squishy wet impact
        noise = (random.random() * 2 - 1) * math.exp(-12 * t)
        thump = math.sin(phase) * math.exp(-8 * t)
        s = 0.6 * thump + 0.5 * noise
        samples.append(s)
    return samples

def generate_bonk(sample_rate=44100, duration=0.4) -> list[float]:
    """صوت ضربة كارتونية على الرأس Bonk!"""
    total_samples = int(sample_rate * duration)
    samples = []
    phase1 = 0.0
    phase2 = 0.0
    for i in range(total_samples):
        t = i / sample_rate
        # Resonant bell-like frequencies
        f1 = 520 * (1 - 0.2 * t)
        f2 = 1180 * (1 - 0.2 * t)
        phase1 += 2 * math.pi * f1 / sample_rate
        phase2 += 2 * math.pi * f2 / sample_rate
        env = math.exp(-14 * t)
        s = (0.7 * math.sin(phase1) + 0.3 * math.sin(phase2)) * env
        samples.append(s)
    return samples

def generate_whistle_fall(sample_rate=44100, duration=1.2) -> list[float]:
    """صوت صفارة سقوط من مكان عالي Slide Whistle Fall!"""
    total_samples = int(sample_rate * duration)
    samples = []
    phase = 0.0
    for i in range(total_samples):
        t = i / sample_rate
        # Drops from 1500Hz down to 200Hz
        f = 1500 - (t / duration) * 1300 + math.sin(2 * math.pi * 12 * t) * 20
        phase += 2 * math.pi * f / sample_rate
        env = math.sin(math.pi * t / duration) ** 0.5
        s = math.sin(phase) * env * 0.8
        samples.append(s)
    return samples

def generate_pop(sample_rate=44100, duration=0.15) -> list[float]:
    """صوت فقع أو خروج كارتوني Pop!"""
    total_samples = int(sample_rate * duration)
    samples = []
    phase = 0.0
    for i in range(total_samples):
        t = i / sample_rate
        f = 750 * math.exp(-25 * t)
        phase += 2 * math.pi * f / sample_rate
        env = math.exp(-30 * t)
        s = math.sin(phase) * env
        samples.append(s)
    return samples

def generate_funny_gasp(sample_rate=44100, duration=0.4) -> list[float]:
    """صوت شهقة صدمة كارتونية مضحكة Gasp!"""
    total_samples = int(sample_rate * duration)
    samples = []
    phase = 0.0
    for i in range(total_samples):
        t = i / sample_rate
        f = 400 + (t / duration) * 350
        phase += 2 * math.pi * f / sample_rate
        env = math.sin(math.pi * t / duration)
        s = (math.sin(phase) + 0.2 * math.sin(3 * phase)) * env * 0.7
        samples.append(s)
    return samples

def generate_funny_bgm(sample_rate=44100, duration=12.0) -> list[float]:
    """موسيقى كارتونية هزلية سريعة ومرحة (Pizzicato / Ragtime Slapstick Loop)"""
    total_samples = int(sample_rate * duration)
    samples = [0.0] * total_samples
    
    # Bouncy cartoon bassline and pizzicato melody
    # Notes in Hz: C4=261.63, E4=329.63, G4=392.00, A4=440.00, C5=523.25, D5=587.33
    bpm = 140
    beat_dur = 60.0 / bpm  # ~0.428s
    
    melody_notes = [
        (261.63, 0.5), (329.63, 0.5), (392.00, 0.5), (523.25, 0.5),
        (587.33, 0.25), (523.25, 0.25), (392.00, 0.5), (329.63, 1.0),
        (220.00, 0.5), (293.66, 0.5), (349.23, 0.5), (440.00, 0.5),
        (392.00, 0.5), (329.63, 0.5), (261.63, 1.0)
    ]
    
    current_time = 0.0
    while current_time < duration:
        for freq, beats in melody_notes:
            note_dur = beats * beat_dur
            start_sample = int(current_time * sample_rate)
            end_sample = min(total_samples, int((current_time + note_dur) * sample_rate))
            
            phase = 0.0
            for i in range(start_sample, end_sample):
                t = (i - start_sample) / sample_rate
                phase += 2 * math.pi * freq / sample_rate
                # Plucky pizzicato envelope
                env = math.exp(-8 * t)
                val = (math.sin(phase) + 0.3 * math.sin(2 * phase) + 0.1 * math.sin(3 * phase)) * env * 0.35
                samples[i] += val
                
            # Add bass thump on downbeats
            if beats >= 0.5:
                bass_freq = freq / 2
                bass_phase = 0.0
                bass_samples = int(0.2 * sample_rate)
                for bi in range(start_sample, min(total_samples, start_sample + bass_samples)):
                    bt = (bi - start_sample) / sample_rate
                    bass_phase += 2 * math.pi * bass_freq / sample_rate
                    bass_env = math.exp(-12 * bt)
                    samples[bi] += math.sin(bass_phase) * bass_env * 0.3
                    
            current_time += note_dur
            if current_time >= duration:
                break
                
    # Normalize
    max_val = max(abs(s) for s in samples) if samples else 1.0
    if max_val > 0.95:
        samples = [s * (0.95 / max_val) for s in samples]
        
    return samples

def build_all_sfx():
    sfx_map = {
        "boing.wav": generate_boing(),
        "splat.wav": generate_splat(),
        "bonk.wav": generate_bonk(),
        "whistle_fall.wav": generate_whistle_fall(),
        "pop.wav": generate_pop(),
        "gasp.wav": generate_funny_gasp(),
        "funny_bgm.wav": generate_funny_bgm(),
    }
    
    for name, samples in sfx_map.items():
        path = SFX_DIR / name
        write_wav(path, samples)
        print(f"✅ Generated SFX: {name} ({len(samples)/44100:.1f}s)")
        
    return SFX_DIR

if __name__ == "__main__":
    build_all_sfx()
