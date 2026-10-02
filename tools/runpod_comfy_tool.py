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
try:
    from config import RUNPOD_COMFY_URL
except Exception:
    RUNPOD_COMFY_URL = os.environ.get("RUNPOD_COMFY_URL", "https://gtja6z9ul4samw-8188.proxy.runpod.net")

def is_runpod_available(url: str = None) -> bool:
    """Check if RunPod ComfyUI server is reachable and active."""
    target_url = url or RUNPOD_COMFY_URL
    try:
        r = requests.get(f"{target_url}/system_stats", timeout=4)
        return r.status_code == 200
    except Exception:
        return False

def translate_and_enhance_prompt(arabic_text: str) -> str:
    """Translate and expand Arabic ideas into rich English 3D Pixar prompts."""
    # If text is already mostly English, return it
    if not any('\u0600' <= char <= '\u06FF' for char in arabic_text):
        return arabic_text
    try:
        from config import GEMINI_API_KEY
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
        instruction = (
            f"You are an expert prompt engineer. Convert this Arabic cartoon idea into a rich English prompt for 3D Pixar cartoon style: '{arabic_text}'. "
            "Output ONLY the final English prompt, no quotes, no markdown, no other words."
        )
        resp = client.models.generate_content(model="gemini-3.8-flash", contents=instruction)
        text = resp.text.strip().strip('"').strip("'").strip("`").strip("*")
        if ":" in text and len(text.split(":")[0]) < 30:
            text = text.split(":", 1)[1].strip().strip('"').strip("*")
        return text if text else arabic_text
    except Exception as e:
        logger.warning(f"Translation error: {e}")
        return arabic_text

def generate_character_on_runpod(prompt_text: str, output_path: str, url: str = None) -> str:
    """Generate high quality 3D Pixar character concept using DreamShaper on RTX 4090."""
    target_url = url or RUNPOD_COMFY_URL
    
    # Automatically translate any Arabic to detailed English prompt
    final_prompt = translate_and_enhance_prompt(prompt_text)
    
    prompt = {
        "1": {
            "inputs": {
                "ckpt_name": "DreamShaper_8_pruned.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "2": {
            "inputs": {
                "text": f"3D Pixar Disney style character, {final_prompt}, cute expressive eyes, soft studio lighting, octane render, 8k masterpiece",
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
                "model_name": "4x-UltraSharp.pth"
            },
            "class_type": "UpscaleModelLoader"
        },
        "8": {
            "inputs": {
                "upscale_model": ["7", 0],
                "image": ["6", 0]
            },
            "class_type": "ImageUpscaleWithModel"
        },
        "9": {
            "inputs": {
                "filename_prefix": "RunPod_Char_4K",
                "images": ["8", 0]
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

def generate_video_on_runpod(image_path: str, output_mp4_path: str, prompt_text: str = None, url: str = None) -> str:
    """Generate high-definition cinematic cartoon video using Wan 2.1 on RTX 4090."""
    from config import RUNPOD_COMFY_URL
    target_url = url or RUNPOD_COMFY_URL
    
    # 1. Translate & enhance prompt if provided
    final_prompt = "3D Pixar Disney animation of cute cartoon character, vivid colors, expressive lively motion, 8k masterpiece"
    if prompt_text:
        final_prompt = translate_and_enhance_prompt(prompt_text)
    
    # 2. Build Wan 2.1 workflow
    workflow = {
        "1": {
            "inputs": {
                "unet_name": "wan2.1_t2v_1.3B_bf16.safetensors",
                "weight_dtype": "default"
            },
            "class_type": "UNETLoader"
        },
        "2": {
            "inputs": {
                "clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                "type": "wan"
            },
            "class_type": "CLIPLoader"
        },
        "3": {
            "inputs": {
                "vae_name": "wan_2.1_vae.safetensors"
            },
            "class_type": "VAELoader"
        },
        "4": {
            "inputs": {
                "text": f"3D Pixar Disney animation, {final_prompt}, highly expressive movement, octane render, Disney Pixar studio quality",
                "clip": ["2", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "5": {
            "inputs": {
                "text": "color artifacts, low quality, blurry, deformed, bad anatomy, text, watermark, static, frozen",
                "clip": ["2", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "6": {
            "inputs": {
                "positive": ["4", 0],
                "negative": ["5", 0],
                "vae": ["3", 0],
                "width": 832,
                "height": 480,
                "length": 33, # 33 frames at 16fps (~2s smooth loop)
                "batch_size": 1
            },
            "class_type": "WanImageToVideo"
        },
        "7": {
            "inputs": {
                "seed": int(time.time() * 1000) % 10000000,
                "steps": 25,
                "cfg": 6.0,
                "sampler_name": "uni_pc",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["6", 0],
                "negative": ["6", 1],
                "latent_image": ["6", 2]
            },
            "class_type": "KSampler"
        },
        "8": {
            "inputs": {
                "samples": ["7", 0],
                "vae": ["3", 0]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "Wan21_HD",
                "fps": 16.0,
                "lossless": False,
                "quality": 95,
                "method": "default",
                "images": ["8", 0]
            },
            "class_type": "SaveAnimatedWEBP"
        }
    }
    
    # If a character image is provided, link it to guide Wan
    if image_path and os.path.exists(image_path):
        try:
            server_img_name = upload_image_to_runpod(image_path, target_url)
            workflow["10"] = {
                "inputs": {
                    "image": server_img_name,
                    "upload": "image"
                },
                "class_type": "LoadImage"
            }
            workflow["6"]["inputs"]["start_image"] = ["10", 0]
        except Exception as e:
            logger.warning(f"Could not attach start_image to Wan: {e}")
    
    r = requests.post(f"{target_url}/prompt", json={"prompt": workflow}, timeout=15)
    if r.status_code != 200:
        raise RuntimeError(f"RunPod Wan 2.1 error: {r.text}")
        
    prompt_id = r.json().get("prompt_id")
    
    # Poll for completion (Wan 2.1 takes ~30-40s on RTX 4090)
    webp_bytes = None
    for _ in range(120):
        time.sleep(2)
        try:
            hr = requests.get(f"{target_url}/history/{prompt_id}", timeout=10)
            hdata = hr.json()
            if prompt_id in hdata:
                outputs = hdata[prompt_id].get("outputs", {})
                for nid, out in outputs.items():
                    if "images" in out and out["images"]:
                        fn = out["images"][0]["filename"]
                        sub = out["images"][0].get("subfolder", "")
                        typ = out["images"][0].get("type", "output")
                        res = requests.get(f"{target_url}/view?filename={fn}&subfolder={sub}&type={typ}", timeout=30)
                        if res.status_code == 200:
                            webp_bytes = res.content
                            break
                if webp_bytes:
                    break
        except Exception as e:
            logger.warning(f"Error checking history: {e}")
            
    if not webp_bytes:
        raise TimeoutError("RunPod Wan 2.1 video generation timed out")
        
    # Convert webp to 1080p High Definition MP4
    temp_webp = str(Path(output_mp4_path).with_suffix(".temp.webp"))
    Path(temp_webp).parent.mkdir(parents=True, exist_ok=True)
    with open(temp_webp, "wb") as f:
        f.write(webp_bytes)
        
    im = Image.open(temp_webp)
    raw_frames = [frame.copy().convert("RGB") for frame in ImageSequence.Iterator(im)]
    
    # Upscale every frame to crisp Full HD (1920x1088 divisible by 16)
    hd_frames = [f.resize((1920, 1088), Image.Resampling.LANCZOS) for f in raw_frames]
    imageio.mimsave(output_mp4_path, hd_frames, fps=16)
    
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
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=25)
            return output_path
        except Exception:
            return video_path
    return video_path
