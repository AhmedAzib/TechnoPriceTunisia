
from curl_cffi import requests
import xml.etree.ElementTree as ET

def fetch_sitemap_index():
    url = "https://www.mytek.tn/media/sitemap/sitemap.xml"
    print(f"Fetching Sitemap: {url}")
    try:
        response = requests.get(url, impersonate="chrome110", timeout=30)
        return response.content
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    content = fetch_sitemap_index()
    if not content: return

    try:
        root = ET.fromstring(content)
        urls = []
        for url in root:
             loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
             urls.append(loc)
        
        print(f"Total URLs: {len(urls)}")
        
        # Filter for "Flat" URLs (likely products) containing laptop keywords
        keywords = ["pc-portable", "pc-gamer", "macbook", "ecran-portable", "ordinateur-portable"] # 'pc-portable' is very common in slugs
        
        # Also check for specific brands combined with "pc" or something generic
        # But 'pc-portable' usually covers it like 'pc-portable-lenovo...'
        
        candidates = []
        for u in urls:
            # Count slashes after domain (https://www.mytek.tn/ = 25 chars approx)
            # easier: split by /
            parts = u.replace("https://www.mytek.tn/", "").split("/")
            
            if len(parts) == 1: # Flat URL
                slug = parts[0].lower()
                if any(k in slug for k in keywords):
                    candidates.append(u)
                    
        print(f"Found {len(candidates)} Candidate Laptop URLs.")
        
        # Save to file
        with open("mytek_product_urls.txt", "w", encoding="utf-8") as f:
            for c in candidates:
                f.write(c + "\n")
                
        print("First 10 candidates:")
        for c in candidates[:10]:
            print(c)
            
    except Exception as e:
        print(f"Error parsing: {e}")

if __name__ == "__main__":
    main()
