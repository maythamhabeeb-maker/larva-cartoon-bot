"""سكريبت التحكم بـ Google Flow عبر المتصفح."""
import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright

FLOW_PROJECT_URL = "https://flow.google.com/project/d8310a85-fae3-4fa5-8a68-a08abc9e82cb"

async def test_connect_flow():
    print("Connecting to Chrome on port 9222...")
    async with async_playwright() as p:
        try:
            # محاولة الاتصال بالكروم المفتوح بـ remote debugging
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            print("Connected to Chrome successfully!")
            
            contexts = browser.contexts
            if not contexts:
                print("No open contexts found.")
                return
            
            context = contexts[0]
            pages = context.pages
            print(f"Found {len(pages)} open tabs:")
            flow_page = None
            for page in pages:
                title = await page.title()
                url = page.url
                print(f" - Tab: {title} | {url[:60]}")
                if "flow.google.com" in url:
                    flow_page = page
            
            if flow_page:
                print(">>> Found Google Flow Tab! Ready to automate Nano Banana 2! <<<")
            else:
                print("Google Flow tab is not open or needs to be navigated.")
                
        except Exception as e:
            print(f"Connection failed: {e}")
            print("\nTo connect to your existing Chrome, run this command:")
            print(r'& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222')

if __name__ == "__main__":
    asyncio.run(test_connect_flow())
