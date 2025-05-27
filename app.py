import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

REPO_DIR = "crawler_repo"
OUTPUT_FILE = os.path.join(REPO_DIR, "urls.txt")
visited = set()
queue = asyncio.Queue()
semaphore = asyncio.Semaphore(30)

def save_url(url):
    if not os.path.exists(OUTPUT_FILE):
        os.makedirs(REPO_DIR, exist_ok=True)
        with open(OUTPUT_FILE, "w"): pass

    with open(OUTPUT_FILE, "r+", encoding="utf-8") as f:
        lines = set([line.strip() for line in f.readlines()])
        if url not in lines:
            f.write(url + "\n")

async def fetch(session, url):
    try:
        async with semaphore:
            async with session.get(url, timeout=10) as response:
                if response.content_type == 'text/html':
                    return await response.text()
    except:
        return None

async def worker():
    async with aiohttp.ClientSession() as session:
        while True:
            url = await queue.get()
            if url in visited:
                queue.task_done()
                continue
            visited.add(url)
            print(f"[{len(visited)}] {url}")
            save_url(url)
            html = await fetch(session, url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                for a in soup.find_all('a', href=True):
                    link = urljoin(url, a['href'])
                    if urlparse(link).scheme in ['http', 'https']:
                        await queue.put(link)
            queue.task_done()

async def main(seed_url):
    await queue.put(seed_url)
    tasks = [asyncio.create_task(worker()) for _ in range(30)]
    await queue.join()
    for t in tasks:
        t.cancel()

if __name__ == "__main__":
    import random
    try:
        if os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, encoding="utf-8") as f:
                urls = [line.strip() for line in f.readlines() if line.strip()]
                seed = random.choice(urls) if urls else "https://example.com"
        else:
            seed = "https://example.com"

        asyncio.run(main(seed))
    except KeyboardInterrupt:
        print("Arrêt")
