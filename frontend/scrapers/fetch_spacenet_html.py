
import requests
from bs4 import BeautifulSoup

url = "https://spacenet.tn/130-smartphone-tunisie"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"Fetching {url}...")
res = requests.get(url, headers=headers)
with open("spacenet_debug.html", "w", encoding="utf-8") as f:
    f.write(res.text)
print("Saved spacenet_debug.html")
