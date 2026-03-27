import requests
from bs4 import BeautifulSoup
import json
import time
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def extract_specs(description_text):
    specs = {"description": description_text}
    
    # Define regex patterns for key specs based on user examples
    patterns = {
        "gpu": [r"(?:GPU|Processeur Graphique)\s*[:]\s*(.*?)(?:📦|🌀|📈|🔌|🔋|🖥️|🎮|📏|🌈|💾|📐|⚡|🎥|🧩|$)", 
                r"Processeur graphique\s*[:]\s*(.*?)(?:$|\n)"],
        "memory": [r"(?:Mémoire|Mémoire Vidéo)\s*[:]\s*(.*?)(?:🧠|📦|🌀|📈|🔌|🔋|🖥️|🎮|📏|🌈|💾|📐|⚡|🎥|🧩|$)", 
                   r"Mémoire\s*[:]\s*(.*?)(?:$|\n)"],
        "cuda": [r"(?:Cœurs CUDA|Cœurs)\s*[:]\s*(.*?)(?:🧠|📦|🌀|📈|🔌|🔋|🖥️|🎮|📏|🌈|💾|📐|⚡|🎥|🧩|$)",
                 r"Cœurs CUDA\s*[:]\s*(.*?)(?:$|\n)"],
        "boost_clock": [r"(?:Fréquence Boost|Boost Clock)\s*[:]\s*(.*?)(?:🧠|📦|🌀|📈|🔌|🔋|🖥️|🎮|📏|🌈|💾|📐|⚡|🎥|🧩|$)",
                        r"Fréquence Boost\s*[:]\s*(.*?)(?:$|\n)"],
        "psu": [r"(?:Conso. Énergie|Alimentation recommandée)\s*[:]\s*(.*?)(?:🧠|📦|🌀|📈|🔌|🔋|🖥️|🎮|📏|🌈|💾|📐|⚡|🎥|🧩|$)",
                r"Alimentation recommandée\s*[:]\s*(.*?)(?:$|\n)"],
        "connectors": [r"(?:Connectique|Sorties vidéo)\s*[:]\s*(.*?)(?:🧠|📦|🌀|📈|🔌|🔋|🖥️|🎮|📏|🌈|💾|📐|⚡|🎥|🧩|$)",
                       r"Connectique\s*[:]\s*(.*?)(?:$|\n)"]
    }
    
    for key, regex_list in patterns.items():
        for regex in regex_list:
            match = re.search(regex, description_text, re.IGNORECASE | re.DOTALL)
            if match:
                val = clean_text(match.group(1))
                # Cleanup common trailing garbage if regex over-matched
                val = re.split(r'(?:🧠|📦|🌀|📈|🔌|🔋|🖥️|🎮|📏|🌈|💾|📐|⚡|🎥|🧩)', val)[0].strip()
                specs[key] = val
                break
                
    return specs

def scrape_skymil_gpus():
    base_url = "https://skymil-informatique.com/29-carte-graphique-tunisie"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    products = []
    page = 1
    
    while True:
        url = f"{base_url}?page={page}"
        print(f"Scraping {url}...")
        
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=20)
            if response.status_code != 200:
                print(f"Failed to load page {page}. Status: {response.status_code}")
                break
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Select product items (check specific class for Skymil)
            items = soup.select('.product-miniature')
            
            if not items:
                print("No items found or end of pagination.")
                break
            
            for item in items:
                try:
                    title_elem = item.select_one('.product-title a')
                    if not title_elem: 
                        continue
                        
                    title = clean_text(title_elem.get_text())
                    link = title_elem['href']
                    
                    # FETCH PRODUCT PAGE FIRST (Stock Check is ONLY here)
                    # print(f"  Checking {title}...") # Verbose
                    try:
                        prod_resp = requests.get(link, headers=headers, verify=False, timeout=15)
                        if prod_resp.status_code != 200:
                            print(f"  Failed to load product page for {title}")
                            continue
                        prod_soup = BeautifulSoup(prod_resp.content, 'html.parser')
                    except Exception as e:
                         print(f"  Error fetching {title}: {e}")
                         continue

                    # CHECK STOCK on Product Page
                    avail_elem = prod_soup.select_one('#product-availability')
                    if not avail_elem:
                         avail_elem = prod_soup.select_one('.product-availability')
                    
                    stock_text = avail_elem.get_text().strip().lower() if avail_elem else ""
                    
                    if "en stock" not in stock_text:
                        # print(f"  Skipping {title} (Not in stock: {stock_text})")
                        continue

                    print(f"  Scraping: {title}")

                    price_elem = item.select_one('.price')
                    price_text = clean_text(price_elem.get_text()) if price_elem else "0"
                    price = float(re.sub(r'[^\d.]', '', price_text.replace(',', '.')))
                    
                    img_elem = item.select_one('.thumbnail-container img')
                    image = img_elem['src'] if img_elem else ""
                    
                    description_div = prod_soup.select_one('.product-description')
                    description_text = ""
                    if description_div:
                        # Get text with separators for easier regex
                        description_text = description_div.get_text(separator="\n")
                    
                    specs = extract_specs(description_text)
                    
                    # Add raw description for future fallback
                    specs['description'] = description_text

                    products.append({
                        "id": f"skymil-gpu-{len(products) + 1}",
                        "title": title,
                        "price": price,
                        "image": image,
                        "link": link,
                        "source": "Skymil",
                        "category": "gpu",
                        "specs": specs,
                        "availability": "in-stock"
                    })
                    
                except Exception as e:
                    print(f"  Error parsing item: {e}")
                    continue
            
            # Pagination check - look for 'next' button disabled or missing
            next_btn = soup.select_one('a.next')
            if not next_btn or 'disabled' in next_btn.get("class", []):
                break
                
            page += 1
            time.sleep(1) # Be polite
            
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            break

    # Save to JSON
    output_path = 'src/data/skymil_gpus.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"Scraping complete. Found {len(products)} in-stock GPUs. Saved to {output_path}")

if __name__ == "__main__":
    scrape_skymil_gpus()
