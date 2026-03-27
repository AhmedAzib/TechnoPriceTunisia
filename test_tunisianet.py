import requests
from bs4 import BeautifulSoup

def debug_tunisianet():
    print("📸  Robot is taking a snapshot of Tunisianet...")
    
    url = "https://www.tunisianet.com.tn/recherche?controller=search&s=iphone"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        
        # 1. Print the Page Title (First Clue)
        soup = BeautifulSoup(response.content, 'html.parser')
        page_title = soup.title.string.strip() if soup.title else "No Title Found"
        print(f"📄  Page Title says: '{page_title}'")
        
        # 2. Try Alternative Selectors (Maybe they changed the name?)
        # Strategy A: The old way
        count_a = len(soup.find_all('div', class_='product-miniature'))
        # Strategy B: Finding the title directly
        count_b = len(soup.find_all('h2', class_='product-title'))
        # Strategy C: Finding the price directly
        count_c = len(soup.find_all('span', class_='price'))
        
        print(f"📊  Diagnostics:")
        print(f"   - Found {count_a} items using 'product-miniature'")
        print(f"   - Found {count_b} items using 'product-title'")
        print(f"   - Found {count_c} items using 'price'")

        # 3. SAVE THE EVIDENCE (The Snapshot)
        # We will save the HTML so you can open it in Chrome
        filename = "snapshot_tunisianet.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(soup.prettify())
            
        print("-" * 40)
        print(f"✅  Snapshot saved to '{filename}'")
        print(f"👉  ACTION: Go to your folder and open '{filename}' in your browser.")
        print("    Does it look like a normal search page, or a 'Verify you are human' page?")

    except Exception as e:
        print(f"❌ Error: {e}")

debug_tunisianet()