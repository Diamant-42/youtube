import asyncio
import aiohttp
import uvloop
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import random

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

URLS_FILE = "urls.txt"
CONCURRENCY = 10000
QUEUE = asyncio.Queue()
SEEN = set()
HEADERS_LIST = [
    "Mozilla/5.0", "Mozilla/5.0 (Windows NT 10.0; Win64)",
    "Mozilla/5.0 (X11; Linux x86_64)", "Mozilla/5.0 (Macintosh)"
]

all_found = 0
all_added = 0
last_found = 0
last_added = 0
BUFFER = []

# Charger les URLs déjà connues
if os.path.exists(URLS_FILE):
    with open(URLS_FILE) as f:
        for line in f:
            url = line.strip()
            if url:
                SEEN.add(url)
else:
    with open(URLS_FILE, "w") as f:
        f.write("https://www.wikipedia.org\n")
    SEEN.add("https://www.wikipedia.org")

async def fetch(session, url):
    try:
        headers = {"User-Agent": random.choice(HEADERS_LIST)}
        async with session.get(url, timeout=10, headers=headers) as resp:
            if resp.status == 200 and 'text/html' in resp.headers.get('Content-Type', ''):
                return await resp.text()
    except:
        return None

def extract_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.scheme in ["http", "https"]:
            links.add(full_url)
    return links

async def worker(session):
    global all_found, all_added, last_found, last_added, BUFFER
    while True:
        url = await QUEUE.get()
        html = await fetch(session, url)
        if html:
            links = extract_links(html, url)
            for link in links:
                all_found += 1
                last_found += 1
                if link not in SEEN:
                    SEEN.add(link)
                    all_added += 1
                    last_added += 1
                    BUFFER.append(link)
                    await QUEUE.put(link)

            if len(BUFFER) >= 100:
                with open(URLS_FILE, "a") as f:
                    f.write("\n".join(BUFFER) + "\n")
                BUFFER = []

        QUEUE.task_done()

async def stats():
    global last_found, last_added
    while True:
        await asyncio.sleep(5)
        print(f"✅ {all_found} trouvés | 🆕 {all_added} nouveaux | ⏱️+{last_found} / +{last_added} depuis 5s")
        last_found = 0
        last_added = 0

async def main():
    for url in SEEN:
        await QUEUE.put(url)

    async with aiohttp.ClientSession() as session:
        workers = [asyncio.create_task(worker(session)) for _ in range(CONCURRENCY)]
        printer = asyncio.create_task(stats())
        await QUEUE.join()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Arrêt demandé.")