import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_spacenet():
    base_url = "https://spacenet.tn/18-ordinateur-portable?page="
    products = []
    
    print("Starting Spacenet Turbo Scrape (Fixed Selectors)...")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for page in range(1, 6):
        url = f"{base_url}{page}"
        print(f"Scraping {url}...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, 'html.parser')
            items = soup.select('.product-miniature')
            
            print(f"Found {len(items)} items on page {page}")
            
            for item in items:
                try:
                    # Name - Selector fixed based on debug artifact: .product_name a
                    name = "Unknown"
                    link = ""
                    
                    name_tag = item.select_one('.product_name a')
                    if name_tag:
                        name = name_tag.get_text(strip=True)
                        link = name_tag.get('href', '')
                    
                    # Fallback if product_name not found (try product-title just in case user meant that)
                    if name == "Unknown":
                        name_tag = item.select_one('.product-title a')
                        if name_tag:
                            name = name_tag.get_text(strip=True)
                            link = name_tag.get('href', '')

                    # Price
                    price_tag = item.select_one('.current-price') or item.select_one('.price')
                    price = price_tag.get_text(strip=True) if price_tag else "0"
                    
                    # Image
                    img_tag = item.select_one('.product-thumbnail img')
                    image_url = ""
                    if img_tag:
                        image_url = img_tag.get('data-full-size-image-url') or img_tag.get('src')
                    
                    products.append({
                        "name": name,
                        "price": price,
                        "image": image_url,
                        "link": link
                    })
                except Exception as e:
                    print(f"Error parsing item: {e}")
                    
        except Exception as e:
            print(f"Error requesting page {page}: {e}")
    
    # Ensure directory exists
    os.makedirs('src/data', exist_ok=True)
    
    output_path = 'src/data/spacenet_products.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    
    print(f"Mission Completed: Saved {len(products)} products to {output_path}")

if __name__ == "__main__":
    scrape_spacenet()
