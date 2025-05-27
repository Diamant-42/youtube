import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import random

visited = set()
queue = asyncio.Queue()
semaphore = asyncio.Semaphore(30)
OUTPUT_FILE = "crawler_repo/urls.txt"
REPO_DIR = "crawler_repo"
SCRIPT_NAME = "crawler.py"

crawler_code = '''
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

visited = set()
queue = asyncio.Queue()
semaphore = asyncio.Semaphore(30)
OUTPUT_FILE = "urls.txt"

def save_url(url):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\\n")

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
    try:
        open(OUTPUT_FILE, "w").close()
        seed = "https://example.com"
        asyncio.run(main(seed))
    except KeyboardInterrupt:
        print("Arrêt")
'''

def save_script_locally():
    os.makedirs(REPO_DIR, exist_ok=True)
    with open(os.path.join(REPO_DIR, SCRIPT_NAME), "w", encoding="utf-8") as f:
        f.write(crawler_code)
    print(f"✅ Fichier {SCRIPT_NAME} généré dans le dossier {REPO_DIR}")

def pick_random_url():
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            lines = f.readlines()
            if lines:
                return random.choice(lines).strip()
    return None

if __name__ == "__main__":
    save_script_locally()
    url = pick_random_url()
    if url:
        print(f"🎯 URL aléatoire depuis urls.txt : {url}")
    else:
        print("⚠️ Aucun site encore crawlé.")
