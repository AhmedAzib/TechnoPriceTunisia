import time
import json
import random
import os
from curl_cffi import requests
from bs4 import BeautifulSoup

def scrape_wiki():
    base_url = "https://wiki.tn/ordinateur-pc-portable/"
    products = []
    
    # Wiki.tn seems to have around 20-30 pages of laptops/products in this category
    # Let's try to scrape a reasonable number of pages
    start_page = 1
    max_pages = 50 

    print(f"Starting scrape for {base_url}...")

    for page in range(start_page, max_pages + 1):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}page/{page}/"
        
        print(f"Scraping page {page}...")
        
        try:
            # Impersonate a browser to avoid 403 Forbidden
            response = requests.get(
                url, 
                impersonate="chrome110", 
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Failed to retrieve page {page}. Status code: {response.status_code}")
                break

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Selector identified from debug HTML
            product_items = soup.select('div.product-card--grid')
            
            if not product_items:
                print(f"No products found on page {page}. Stopping.")
                # Save debug HTML only if it's the first page and we fail
                if page == 1:
                    with open("wiki_debug.html", "w", encoding="utf-8") as f:
                        f.write(soup.prettify())
                    print("Saved debug HTML to wiki_debug.html")
                break

            for item in product_items:
                try:
                    # Title & Link
                    title_tag = item.select_one('h3.product-card__title a')
                    if not title_tag:
                        continue
                    
                    title = title_tag.get_text(strip=True)
                    link = title_tag.get('href')

                    # Image
                    img_tag = item.select_one('figure.product-card__image img')
                    image = "https://wiki.tn/wp-content/uploads/2023/06/Logo-Wiki-blanc.svg" # Fallback
                    if img_tag:
                        # Prefer data-lazy-src, then src
                        image = img_tag.get('data-lazy-src') or img_tag.get('src') or image

                    # Price
                    # Price can be in <ins> (sale) or just <span class="amount">
                    price_container = item.select_one('.product-card__price .price')
                    price_text = "0"
                    
                    if price_container:
                        # Check for sale price first
                        ins_tag = price_container.select_one('ins .woocommerce-Price-amount bdi')
                        if ins_tag:
                            price_text = ins_tag.get_text(strip=True)
                        else:
                            # Normal price
                            amount_tag = price_container.select_one('.woocommerce-Price-amount bdi')
                            if amount_tag:
                                price_text = amount_tag.get_text(strip=True)

                    # Clean price string (remove TND, spaces, commas -> dots)
                    # Example: "1 250,500 TND" -> "1250.500"
                    price_clean = price_text.replace('TND', '').replace('DT', '').replace('\u00a0', '').strip()
                    price_clean = price_clean.replace(' ', '').replace(',', '.')
                    
                    products.append({
                        "title": title,
                        "price": price_clean,
                        "image": image,
                        "link": link,
                        "source": "Wiki"
                    })

                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue
            
            print(f"Found {len(product_items)} products on page {page}.")
            
            # Be nice to the server
            time.sleep(random.uniform(1, 3))

        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            break

    # Save to file
    output_file = 'src/data/wiki_raw.json'
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"Scraping completed. {len(products)} products saved to {output_file}")

if __name__ == "__main__":
    scrape_wiki()
