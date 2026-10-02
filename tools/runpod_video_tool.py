"""RunPod On-Demand GPU Controller & Cartoon Video Generator.
يقوم بتشغيل كارت الشاشة RTX 4090 عند طلب المستخدم تلقائياً،
وتوليد حلقة الكارتون الطويلة، ثم إطفاء كارت الشاشة فوراً لتوفير الرصيد (0$/ساعة عند التوقف).
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
POD_ID = os.getenv("RUNPOD_POD_ID", "f53aof6nipckaw")
GRAPHQL_URL = f"https://api.runpod.io/graphql?api_key={RUNPOD_API_KEY}"

def run_graphql(query: str, variables: dict = None) -> dict:
    resp = requests.post(
        f"https://api.runpod.io/graphql?api_key={RUNPOD_API_KEY}",
        json={"query": query, "variables": variables or {}},
        timeout=30
    )
    if resp.status_code != 200:
        raise RuntimeError(f"RunPod GraphQL Error ({resp.status_code}): {resp.text}")
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"RunPod GraphQL Error: {json.dumps(data['errors'])}")
    return data.get("data", {})

def get_pod_status() -> dict:
    """إرجاع حالة كارت الشاشة الحالية ومنافذ الاتصال."""
    q = """
    query GetPodStatus {
      myself {
        pods {
          id
          name
          desiredStatus
          costPerHr
          runtime {
            uptimeInSeconds
            ports {
              ip
              isIpPublic
              privatePort
              publicPort
              type
            }
          }
        }
      }
    }
    """
    res = run_graphql(q)
    pods = res.get("myself", {}).get("pods", [])
    for p in pods:
        if p.get("id") == POD_ID:
            return p
    return {}

def resume_pod(on_progress=None) -> bool:
    """تشغيل كارت الشاشة (Start/Resume)."""
    if on_progress:
        on_progress("⚡ تشغيل كارت الشاشة RTX 4090 من وضع السكون...")
    mutation = f"""
    mutation ResumePod {{
      podResume(input: {{
        podId: "{POD_ID}"
      }}) {{
        id
        desiredStatus
      }}
    }}
    """
    res = run_graphql(mutation)
    return True

def stop_pod(on_progress=None) -> bool:
    """إطفاء كارت الشاشة فوراً لحفظ الرصيد (Stop Pod)."""
    if on_progress:
        on_progress("🛑 إطفاء كارت الشاشة لحفظ الرصيد فوراً (0$/ساعة)...")
    mutation = f"""
    mutation StopPod {{
      podStop(input: {{
        podId: "{POD_ID}"
      }}) {{
        id
        desiredStatus
      }}
    }}
    """
    res = run_graphql(mutation)
    logger.info("Pod %s stopped successfully.", POD_ID)
    return True

def wait_until_ready(timeout_sec: int = 180, on_progress=None) -> dict:
    """الانتظار حتى يصبح كارت الشاشة جاهزاً للاتصال."""
    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        pod = get_pod_status()
        status = pod.get("desiredStatus", "")
        runtime = pod.get("runtime")
        
        if status == "RUNNING" and runtime is not None:
            if on_progress:
                on_progress("✅ كارت الشاشة جاهز وبدأ العمل!")
            return pod
        
        if on_progress:
            on_progress("⏳ جاري تهيئة كارت الشاشة للإنتاج (ثواني معدودة)...")
        time.sleep(5)
        
    raise TimeoutError("استغرق إقلاع كارت الشاشة وقتاً طويلاً.")
