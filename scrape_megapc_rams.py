import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json
import re

def clean_price(price_str):
    if not price_str: return 0.0
    # Strip non-breaking spaces before regex
    clean_str = price_str.replace('\u202f', '').replace('\xa0', '').replace(' ', '').upper()
    # Try finding the price near DT or TND using regex
    m = re.search(r'([\d,.]+)\s*(DT|TND)', clean_str)
    if m:
        clean = m.group(1).replace(',', '.')
    else:
        # Fallback
        clean = clean_str.replace('DT', '').replace('TND', '').replace(',', '.')
        clean = re.sub(r'[^\d.]', '', clean)

    try:
        return float(clean)
    except:
        return 0.0

def parse_specs_from_title(title):
    t_upper = title.upper()
    specs = {
        "memory_type": "Unknown",
        "ram_capacity": "Unknown",
        "format": "Unknown",
        "ram_speed": "Unknown",
        "hz": "Unknown"
    }
    
    # Capacity
    if "128GB" in t_upper or "128 GO" in t_upper or "128GO" in t_upper: specs["ram_capacity"] = "128 GB"
    elif "96GB" in t_upper or "96 GO" in t_upper or "96GO" in t_upper: specs["ram_capacity"] = "96 GB"
    elif "64GB" in t_upper or "64 GO" in t_upper or "64GO" in t_upper: specs["ram_capacity"] = "64 GB"
    elif "48GB" in t_upper or "48 GO" in t_upper or "48GO" in t_upper: specs["ram_capacity"] = "48 GB"
    elif "32GB" in t_upper or "32 GO" in t_upper or "32GO" in t_upper: specs["ram_capacity"] = "32 GB"
    elif "16GB" in t_upper or "16 GO" in t_upper or "16GO" in t_upper: specs["ram_capacity"] = "16 GB"
    elif "8GB" in t_upper or "8 GO" in t_upper or "8GO" in t_upper: specs["ram_capacity"] = "8 GB"
    elif "4GB" in t_upper or "4 GO" in t_upper or "4GO" in t_upper: specs["ram_capacity"] = "4 GB"
    
    # Type
    if "DDR5" in t_upper: specs["memory_type"] = "DDR5"
    elif "DDR4" in t_upper: specs["memory_type"] = "DDR4"
    elif "DDR3" in t_upper: specs["memory_type"] = "DDR3"
    
    # Format
    if "SODIMM" in t_upper or "SO-DIMM" in t_upper or "MAC" in t_upper: specs["format"] = "SO-DIMM"
    else: specs["format"] = "DIMM"
        
    # Speed
    m = re.search(r'(\d{3,4})\s*(MHZ)', t_upper)
    if m:
        specs["ram_speed"] = f"{m.group(1)} MHz"
        specs["hz"] = f"{m.group(1)} Hz"
        
    # --- MANUAL OVERRIDES ---
    if "SILICON POWER SP 16GB (1X16GB) 3200MHZ PCB" in t_upper or "SILICON POWER SP 16GB (1X16GB) 3200MHZ PCP" in t_upper:
        specs["memory_type"] = "DDR4"
    if "BARRETTE CRUCIAL PRO 128GB (64GBX2) DDR5-5600 UDIMM" in t_upper:
        specs["ram_speed"] = "5600 MHz"
        specs["hz"] = "5600 Hz"
        
    return specs

def scrape():
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")
    
    driver = uc.Chrome(options=options)
    
    products = []
    seen = set()
    
    try:
        url = "https://megapc.tn/shop/COMPOSANTS/BARETTE%20M%C3%89MOIRE"
        print(f"Loading {url}")
        driver.get(url)
        time.sleep(5)
        
        current_page = 1
        while True:
            # Scroll to load images lazily
            for _ in range(5):
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1)
            
            items = driver.find_elements(By.CSS_SELECTOR, ".border-gray-100") # Generic product container
            if not items:
                items = driver.find_elements(By.XPATH, "//a[contains(@href, '/shop/product/')]")
                
            print(f"Found {len(items)} items on current page.")
            
            # Extract from item containers directly
            for el in items:
                try:
                    # Scroll element into viewport to trigger Next.js lazy loading
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", el)
                    time.sleep(0.5)

                    # Find link
                    if el.tag_name.lower() == 'a':
                        a_tag = el
                    else:
                        a_tags = el.find_elements(By.TAG_NAME, "a")
                        if not a_tags: continue
                        a_tag = a_tags[0]
                        
                    href = a_tag.get_attribute("href")
                    if not href or href in seen: continue
                    seen.add(href)

                    # Extract text content block
                    text_content = el.text
                    lines = [ln.strip() for ln in text_content.split("\\n") if ln.strip()]
                    if not lines: continue

                    title = ""
                    # Title is usually the first or second line, or has DDR
                    for ln in lines:
                        if "DDR" in ln.upper() or "GB" in ln.upper() or "GO" in ln.upper() or "MHZ" in ln.upper() or "BARRETTE" in ln.upper():
                            title = ln
                            break
                    if not title: title = lines[0]
                    
                    if "New" in title and len(lines) > 1:
                        title = lines[1]
                        
                    if title.startswith("New\\n"): title = title[4:]
                    if title.startswith("New "): title = title[4:]

                    price = 0.0
                    for ln in lines:
                        if "DT" in ln.upper() or "TND" in ln.upper():
                            price = clean_price(ln)
                            break
                            
                    if price == 0.0: continue

                    img_url = ""
                    try:
                        # Grab the image AFTER scrolling
                        img = el.find_element(By.TAG_NAME, "img")
                        img_url = img.get_attribute("src")
                        
                        # Fallback to srcset if still lazy loading
                        if "data:image" in img_url or "placeholder" in img_url:
                            srcset = img.get_attribute("srcset")
                            if srcset:
                                urls = [p.strip().split(" ")[0] for p in srcset.split(",")]
                                if urls:
                                    img_url = urls[-1]
                                    
                        # Try noscript as last resort
                        if "data:image" in img_url or "placeholder" in img_url:
                            try:
                                noscript = el.find_element(By.TAG_NAME, "noscript")
                                noscript_html = noscript.get_attribute("innerHTML")
                                m = re.search(r'src="(.*?)"', noscript_html)
                                if m: img_url = m.group(1).replace("&amp;", "&")
                            except:
                                pass

                        # Ensure absolute URL
                        if img_url and img_url.startswith("/"):
                            img_url = "https://megapc.tn" + img_url
                        
                        # Fix encoding in URL
                        if img_url: img_url = img_url.replace("&amp;", "&")
                        
                        # If STILL placeholder, just make it empty so it falls back to default in UI
                        if "data:image" in img_url:
                            img_url = ""
                    except Exception as e:
                        print("Img error:", e)
                        pass
                        
                    specs = parse_specs_from_title(title)
                    specs["category"] = "RAM"
                    
                    products.append({
                        "id": f"megapc_ram_{len(products)}",
                        "title": title.strip(),
                        "price": price,
                        "link": href,
                        "image": img_url,
                        "source": "MegaPC",
                        "category": "RAM",
                        "specs": specs
                    })
                    print(f" + {title[:40]}... | {price} DT")
                except Exception as e:
                    print("Error parsing item:", e)
                    pass
            # Attempt pagination by looking for the next page number
            try:
                next_num = current_page + 1
                
                # Broad XPath to find pagination buttons by exact text
                next_page_btn = driver.find_elements(By.XPATH, f"//*[text()='{next_num}'] | //*[text()=' {next_num} ']")
                
                # Filter out elements that are too high up the tree (like the whole body)
                valid_btns = [b for b in next_page_btn if b.tag_name.lower() in ['a', 'button', 'li', 'span', 'div']]
                
                if valid_btns:
                    print(f"Clicking to page {next_num}...")
                    btn = valid_btns[-1] # Usually the innermost element
                    driver.execute_script("arguments[0].scrollIntoView();", btn)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", btn)
                    time.sleep(5)
                    current_page = next_num
                else:
                    print(f"Page {next_num} not found. Reached end.")
                    break
            except Exception as e:
                print("Could not paginate:", str(e))
                break
                
    finally:
        driver.quit()
        
    with open("frontend/src/data/megapc_rams.json", "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"Scraped {len(products)} products and saved to megapc_rams.json")

if __name__ == "__main__":
    scrape()
