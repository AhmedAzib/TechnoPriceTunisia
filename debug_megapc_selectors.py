import requests
from bs4 import BeautifulSoup

def debug():
    url = "https://megapc.tn/shop/COMPOSANTS/CARTE%20M%C3%88RE?page=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    print(f"Fetching {url}...")
    r = requests.get(url, headers=headers)
    print(f"Status: {r.status_code}")
    
    soup = BeautifulSoup(r.content, 'html.parser')
    articles = soup.select("article.product-card")
    print(f"Found {len(articles)} articles.")
    
    if len(articles) > 0:
        art = articles[0]
        print("\n--- HTML of first card ---")
        print(art.prettify())
        print("\n--- Analysis ---")
        
        # Link
        a = art.select_one("a")
        print(f"First <a> tag: {a}")
        if a: print(f"Href: {a.get('href')}")
        
        # Title
        p = art.select_one("p.text-skin-base")
        print(f"Title <p>: {p}")
        
        a_title = art.select_one("a[title]")
        print(f"Title <a>: {a_title}")
        
if __name__ == "__main__":
    debug()
