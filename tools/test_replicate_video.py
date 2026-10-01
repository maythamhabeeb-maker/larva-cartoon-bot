import sys
import io
import os
import requests
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv()
token = os.getenv("REPLICATE_API_TOKEN")
headers = {"Authorization": f"Bearer {token}"}

models_to_check = [
    "minimax/video-01",
    "kwaivgi/kling-v1.6-standard",
    "wan-video/wan-2.1-t2v-480p",
    "luma/ray",
    "bytedance/animatediff-lightning-4-step"
]

for m in models_to_check:
    res = requests.get(f"https://api.replicate.com/v1/models/{m}", headers=headers)
    if res.status_code == 200:
        data = res.json()
        print(f"✅ {m}: Available! (Description: {data.get('description', '')[:60]})")
    else:
        print(f"❌ {m}: Status {res.status_code}")
