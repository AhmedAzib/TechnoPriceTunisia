
import requests
from bs4 import BeautifulSoup

url = "https://tunisiatech.tn/25-smartphones-tunisie"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    print(f"Fetching {url}...")
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {res.status_code}")
    soup = BeautifulSoup(res.content, 'html.parser')
    items = soup.select('.product-miniature')
    print(f"Found {len(items)} items.")
except Exception as e:
    print(f"Error: {e}")
