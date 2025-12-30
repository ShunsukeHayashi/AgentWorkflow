import asyncio
import os
import re
from datetime import datetime
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Configuration
CHANNEL_ID = "3577"
BASE_URL = f"https://voicy.jp/channel/{CHANNEL_ID}"
ALL_EPISODES_URL = f"{BASE_URL}/all"
OUTPUT_DIR = "drafts/voicy_history"

os.makedirs(OUTPUT_DIR, exist_ok=True)

async def auto_scroll(page):
    """Scrolls down the page until no new content loads."""
    print("Starting infinite scroll...")
    last_height = await page.evaluate("document.body.scrollHeight")
    while True:
        await page.mouse.wheel(0, 5000)
        await page.wait_for_timeout(2000)  # Wait for load
        new_height = await page.evaluate("document.body.scrollHeight")
        if new_height == last_height:
            # Try once more to be sure
            await page.wait_for_timeout(2000)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height
        print(f"Scrolled to height: {last_height}")

async def process_episode(page, episode_url):
    print(f"Processing: {episode_url}")
    await page.goto(episode_url)
    await page.wait_for_load_state("networkidle")

    # Expand transcription if available
    try:
        # Looking for "Show more" button. Selector might need adjustment based on actual site.
        # Based on typical Voicy structure, there is often a button to expand text.
        # We will try a generic approach or look for specific text.
        show_more_buttons = await page.locator("button:has-text('もっと見る')").all()
        for btn in show_more_buttons:
            if await btn.is_visible():
                await btn.click()
                await page.wait_for_timeout(500)
    except Exception as e:
        print(f"Notice: Could not click 'Show more' (might not exist): {e}")

    content = await page.content()
    soup = BeautifulSoup(content, 'html.parser')

    # Extract Metadata
    try:
        title = soup.select_one('h1').get_text(strip=True)
    except:
        title = "No Title"

    try:
        date_str = soup.select_one('time').get_text(strip=True)
        # Convert date format if necessary. Voicy often uses "2023/12/30" or similar.
        # Detailed parsing might be needed, but for now we keep the string or try simple normalization.
        # Example format: 2023年12月30日 or 2023/12/30
        date_match = re.search(r'(\d{4})[./年](\d{1,2})[./月](\d{1,2})', date_str)
        if date_match:
            date_obj = datetime(int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)))
            file_date = date_obj.strftime('%Y-%m-%d')
        else:
            file_date = datetime.now().strftime('%Y-%m-%d') # Fallback
    except:
        file_date = datetime.now().strftime('%Y-%m-%d')

    # Extract Transcript/Summary
    # This is highly dependent on DOM structure.
    # Assuming 'article' class or similar container for main text.
    main_text = ""
    
    # Strategy: Find the container that holds the text.
    # Often in Voicy: .story-comment or generic article body
    article_body = soup.select_one('article') or soup.body
    if article_body:
        main_text = article_body.get_text("\n", strip=True)

    # Clean up text
    # (Optional: specialized cleaning)

    # Format Markdown
    md_content = f"""# {title}

## 概要
(自動取得された日付: {date_str})

## AI書き起こし
{main_text}
"""
    
    # Save File
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title).replace(" ", "_")
    filename = f"{OUTPUT_DIR}/{file_date}_{safe_title}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved: {filename}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Fetch List
        print(f"Navigating to {ALL_EPISODES_URL}")
        await page.goto(ALL_EPISODES_URL)
        await auto_scroll(page)

        # Extract all episode links
        episode_links = await page.evaluate("""
            Array.from(document.querySelectorAll('a.story-item-container')).map(a => a.href)
        """)
        
        # Filter for unique links and ensuring they match pattern
        unique_links = sorted(list(set([l for l in episode_links if f"/channel/{CHANNEL_ID}/" in l])))
        print(f"Found {len(unique_links)} episodes.")

        # 2. Process Each Episode
        for url in unique_links:
            # Check if likely already processed (optional optimization could be added here)
            await process_episode(page, url)
            await page.wait_for_timeout(1000) # Polite delay

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
