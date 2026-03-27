import requests
from bs4 import BeautifulSoup

def debug_scraper():
    url = "https://megapc.tn/shop/COMPOSANTS/CARTE%20M%C3%88RE?page=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching {url}...")
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    
    articles = soup.select("article.product-card")
    print(f"Found {len(articles)} articles.")
    
    if articles:
        art = articles[0]
        print("\n--- Article 0 HTML ---")
        print(str(art)[:500])
        print("\n--- Extraction Test ---")
        
        link_el = art.select_one("a")
        print(f"Link Element: {link_el}")
        if link_el:
            print(f"Href: {link_el.get('href')}")
            
        title_el = art.select_one("p.text-skin-base") or art.select_one("a[title]")
        print(f"Title Element: {title_el}")
        
    else:
        print("No articles found!")

if __name__ == "__main__":
    debug_scraper()
