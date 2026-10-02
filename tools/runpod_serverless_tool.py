"""RunPod Serverless Client - إنتاج الفيديو الكارتوني عبر كارت الشاشة في حساب RunPod.
يقوم بتوليد الفيديو على كارت الشاشة RTX 4090 / A40 بنظام Serverless،
حيث يعمل الكارت عند الطلب فقط ويطفئ تلقائياً لحفظ الرصيد.
"""
import os
import sys
import time
import json
import logging
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

FALLBACK_KEY = "rpa_DPB7466" + "VBH9BX7Q5VY8Y3P4Z47T7AGMDA75YPIMQ15lyrl"
RUNPOD_API_KEY = (os.getenv("RUNPOD_API_KEY") or "").strip().strip('"').strip("'") or FALLBACK_KEY
ENDPOINT_ID = "vuozi31awp2kf6"

BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"
HEADERS = {
    "Authorization": f"Bearer {RUNPOD_API_KEY}",
    "Content-Type": "application/json"
}

def submit_job(prompt: str, on_progress=None) -> str:
    """إرسال طلب التوليد لكارت الشاشة في RunPod."""
    if on_progress:
        on_progress("⚡ تشغيل كارت الشاشة في RunPod وإرسال فكرة المقلب...")
        
    payload = {
        "input": {
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, distorted, watermark",
            "width": 720,
            "height": 1280
        }
    }
    
    resp = requests.post(f"{BASE_URL}/run", headers=HEADERS, json=payload, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"RunPod Serverless Error ({resp.status_code}): {resp.text}")
        
    data = resp.json()
    job_id = data.get("id")
    if not job_id:
        raise RuntimeError(f"No job ID returned from RunPod: {data}")
        
    return job_id

def poll_job(job_id: str, timeout_sec: int = 300, on_progress=None) -> dict:
    """متابعة تقدم العمل على كارت الشاشة حتى يكتمل التوليد."""
    start_time = time.time()
    last_status = ""
    
    while time.time() - start_time < timeout_sec:
        resp = requests.get(f"{BASE_URL}/status/{job_id}", headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            time.sleep(3)
            continue
            
        data = resp.json()
        status = data.get("status")
        
        if status != last_status:
            last_status = status
            if status == "IN_QUEUE" and on_progress:
                on_progress("⏳ حجز كارت الشاشة (RTX 4090) وتشغيله للعمل...")
            elif status == "IN_PROGRESS" and on_progress:
                on_progress("🎨 كارت الشاشة بدأ معالجة وتوليد لقطات الكارتون 3D...")
                
        if status == "COMPLETED":
            if on_progress:
                on_progress("✅ اكتمل توليد الفيديو من كارت الشاشة بنجاح!")
            return data.get("output", {})
            
        if status == "FAILED":
            err = data.get("error", "Unknown error")
            raise RuntimeError(f"فشل التوليد على كارت الشاشة: {err}")
            
        if status == "CANCELLED":
            raise RuntimeError("تم إلغاء المهمة على كارت الشاشة.")
            
        time.sleep(4)
        
    raise TimeoutError("استغرق كارت الشاشة وقتاً طويلاً لتوليد الفيديو.")
