import os
import time
import requests
import json
import logging
from pathlib import Path
from PIL import Image, ImageSequence
import imageio

logger = logging.getLogger(__name__)

# RunPod ComfyUI Settings
RUNPOD_COMFY_URL = os.environ.get("RUNPOD_COMFY_URL", "https://3x1kx5x27ttiq1-8188.proxy.runpod.net")

def is_runpod_available(url: str = None) -> bool:
    """Check if RunPod ComfyUI server is reachable and active."""
    target_url = url or RUNPOD_COMFY_URL
    try:
        r = requests.get(f"{target_url}/system_stats", timeout=4)
        return r.status_code == 200
    except Exception:
        return False

def generate_character_on_runpod(prompt_text: str, output_path: str, url: str = None) -> str:
    """Generate high quality 3D Pixar character concept using DreamShaper on RTX 4090."""
    target_url = url or RUNPOD_COMFY_URL
    
    prompt = {
        "1": {
            "inputs": {
                "ckpt_name": "DreamShaper_8_pruned.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "2": {
            "inputs": {
                "text": f"3D Pixar Disney style character, {prompt_text}, cute expressive eyes, soft studio lighting, octane render, 8k masterpiece",
                "clip": ["1", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "3": {
            "inputs": {
                "text": "ugly, blurry, bad anatomy, deformed, disfigured, poor quality, watermark, text",
                "clip": ["1", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "4": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "5": {
            "inputs": {
                "seed": int(time.time() * 1000) % 10000000,
                "steps": 25,
                "cfg": 7.5,
                "sampler_name": "euler_ancestral",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            },
            "class_type": "KSampler"
        },
        "6": {
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2]
            },
            "class_type": "VAEDecode"
        },
        "7": {
            "inputs": {
                "filename_prefix": "RunPod_Char",
                "images": ["6", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    r = requests.post(f"{target_url}/prompt", json={"prompt": prompt}, timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"RunPod ComfyUI error: {r.text}")
        
    prompt_id = r.json().get("prompt_id")
    
    # Wait for completion
    for _ in range(60):
        time.sleep(1)
        hr = requests.get(f"{target_url}/history/{prompt_id}", timeout=5)
        hdata = hr.json()
        if prompt_id in hdata:
            outputs = hdata[prompt_id].get("outputs", {})
            for nid, out in outputs.items():
                if "images" in out:
                    for img in out["images"]:
                        fn = img["filename"]
                        sub = img.get("subfolder", "")
                        typ = img.get("type", "output")
                        res = requests.get(f"{target_url}/view?filename={fn}&subfolder={sub}&type={typ}", timeout=20)
                        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(res.content)
                        return output_path
    raise TimeoutError("RunPod image generation timed out")

def upload_image_to_runpod(local_image_path: str, url: str = None) -> str:
    """Upload an image to RunPod ComfyUI input folder."""
    target_url = url or RUNPOD_COMFY_URL
    with open(local_image_path, "rb") as f:
        files = {"image": (os.path.basename(local_image_path), f, "image/png")}
        r = requests.post(f"{target_url}/upload/image", files=files, timeout=15)
        if r.status_code == 200:
            return r.json().get("name", os.path.basename(local_image_path))
        raise RuntimeError(f"Failed to upload image to ComfyUI: {r.text}")

def generate_video_on_runpod(image_path: str, output_mp4_path: str, url: str = None) -> str:
    """Animate a character reference image into video using SVD on RTX 4090."""
    target_url = url or RUNPOD_COMFY_URL
    
    # 1. Upload init image
    server_image_name = upload_image_to_runpod(image_path, target_url)
    
    # 2. Build SVD workflow
    workflow = {
        "1": {
            "inputs": {
                "image": server_image_name,
                "upload": "image"
            },
            "class_type": "LoadImage"
        },
        "2": {
            "inputs": {
                "ckpt_name": "svd_xt.safetensors"
            },
            "class_type": "ImageOnlyCheckpointLoader"
        },
        "3": {
            "inputs": {
                "width": 512,
                "height": 512,
                "video_frames": 25,
                "motion_bucket_id": 127,
                "fps": 12,
                "augmentation_level": 0.0,
                "clip_vision": ["2", 1],
                "init_image": ["1", 0],
                "vae": ["2", 2]
            },
            "class_type": "SVD_img2vid_Conditioning"
        },
        "4": {
            "inputs": {
                "seed": int(time.time() * 1000) % 10000000,
                "steps": 20,
                "cfg": 2.5,
                "sampler_name": "euler",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["3", 1],
                "latent_image": ["3", 2]
            },
            "class_type": "KSampler"
        },
        "5": {
            "inputs": {
                "samples": ["4", 0],
                "vae": ["2", 2]
            },
            "class_type": "VAEDecode"
        },
        "6": {
            "inputs": {
                "filename_prefix": "RunPod_SVD",
                "fps": 12.0,
                "lossless": False,
                "quality": 85,
                "method": "default",
                "images": ["5", 0]
            },
            "class_type": "SaveAnimatedWEBP"
        }
    }
    
    r = requests.post(f"{target_url}/prompt", json={"prompt": workflow}, timeout=10)
    if r.status_code != 200:
        raise RuntimeError(f"RunPod SVD error: {r.text}")
        
    prompt_id = r.json().get("prompt_id")
    
    # Poll for completion (usually 20-30s on RTX 4090)
    webp_bytes = None
    for _ in range(120):
        time.sleep(2)
        hr = requests.get(f"{target_url}/history/{prompt_id}", timeout=5)
        hdata = hr.json()
        if prompt_id in hdata:
            outputs = hdata[prompt_id].get("outputs", {})
            for nid, out in outputs.items():
                if "images" in out:
                    for img in out["images"]:
                        fn = img["filename"]
                        sub = img.get("subfolder", "")
                        typ = img.get("type", "output")
                        res = requests.get(f"{target_url}/view?filename={fn}&subfolder={sub}&type={typ}", timeout=30)
                        webp_bytes = res.content
                        break
            break
            
    if not webp_bytes:
        raise TimeoutError("RunPod SVD video generation timed out")
        
    # Convert webp to MP4
    temp_webp = str(Path(output_mp4_path).with_suffix(".temp.webp"))
    Path(temp_webp).parent.mkdir(parents=True, exist_ok=True)
    with open(temp_webp, "wb") as f:
        f.write(webp_bytes)
        
    im = Image.open(temp_webp)
    frames = [frame.copy().convert("RGB") for frame in ImageSequence.Iterator(im)]
    imageio.mimsave(output_mp4_path, frames, fps=12)
    
    if os.path.exists(temp_webp):
        try:
            os.remove(temp_webp)
        except Exception:
            pass
            
    return output_mp4_path

def add_cartoon_audio(video_path: str, output_path: str) -> str:
    """Add cartoon BGM to generated video."""
    import imageio_ffmpeg
    import subprocess
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    bgm_file = Path(__file__).resolve().parent.parent / "assets" / "sfx" / "funny_bgm.wav"
    if bgm_file.exists():
        cmd = [
            ffmpeg_exe, "-y",
            "-i", str(video_path),
            "-stream_loop", "-1",
            "-i", str(bgm_file),
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(output_path)
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return output_path
        except Exception:
            return video_path
    return video_path
