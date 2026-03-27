import requests
from bs4 import BeautifulSoup

def debug_bs4():
    url = "https://megapc.tn/shop/category/ordinateur-portable"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {r.status_code}")
        
        soup = BeautifulSoup(r.content, 'html.parser')
        
        # Check for articles
        articles = soup.select("article")
        print(f"Articles found: {len(articles)}")
        
        # Check for common product classes
        cards = soup.select(".product-card")
        print(f".product-card found: {len(cards)}")
        
        items = soup.select(".product-item")
        print(f".product-item found: {len(items)}")

        # Print distinct class names of divs inside the first main container to guess
        # Look for a grid
        print("--- Finding Grid ---")
        grids = soup.select(".grid")
        print(f"Grids found: {len(grids)}")
        
        if len(cards) > 0:
            print("--- First Card HTML ---")
            print(cards[0].prettify()[:500])
        elif len(articles) > 0:
            print("--- First Article HTML ---")
            print(articles[0].prettify()[:500])
        else:
             print("--- Body Snapshot ---")
             print(soup.prettify()[:1000])

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_bs4()
