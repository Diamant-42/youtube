import time
import random
import requests

def keepalive():
    while True:
        try:
            with open("urls.txt", "r") as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if not urls:
                print("[KEEPALIVE] Aucun URL trouvé.")
            else:
                url = random.choice(urls)
                print(f"[KEEPALIVE] Ping {url}")
                try:
                    requests.head(url, timeout=5)
                except Exception as e:
                    print(f"[KEEPALIVE] Échec ping {url} → {e}")
        
        except FileNotFoundError:
            print("[KEEPALIVE] Fichier urls.txt introuvable.")
        
        time.sleep(6)  # 1 ping toutes les 60 secondes

if __name__ == "__main__":
    keepalive()
