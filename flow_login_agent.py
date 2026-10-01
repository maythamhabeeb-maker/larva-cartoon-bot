"""Flow Agent Browser Session Launcher."""
import sys
import io
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

USER_DATA_DIR = Path(r"C:\Users\Mayth\.gemini\antigravity\scratch\flow_user_data")

async def login_and_save():
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("Launching Flow Agent Browser...")
    
    async with async_playwright() as p:
        browser_context = await p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA_DIR),
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = await browser_context.new_page()
        await page.goto("https://flow.google.com/project/d8310a85-fae3-4fa5-8a68-a08abc9e82cb")
        
        print(">>> Browser is now open on your screen! <<<")
        print("1. Please login to your Google account in this opened window.")
        print("2. Once you see the Google Flow project page, keep it or tell me 'Done'.")
        
        while True:
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(login_and_save())
