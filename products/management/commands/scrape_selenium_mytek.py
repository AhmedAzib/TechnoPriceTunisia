import time
import re
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from products.models import Product, Price, Brand, Shop

class Command(BaseCommand):
    help = 'Scrape MyTek using Meta Tags (Facebook Data) + Screenshot Debug'

    def handle(self, *args, **kwargs):
        self.stdout.write("🤖 Launching Meta-Tag Robot...")

        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        # chrome_options.add_argument("--headless") # Keep commented out to see the browser
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        try:
            # 1. CATALOG
            shop, _ = Shop.objects.get_or_create(name="MyTek", defaults={'url': "https://mytek.tn"})
            
            page_num = 1
            total_scraped_count = 0

            while True:
                # 1. PAGE NAVIGATION (URL-Based)
                url = f"https://www.mytek.tn/informatique/ordinateurs-portables/pc-portable.html?p={page_num}"
                self.stdout.write(f"--- 📄 Scrapping Page {page_num} ---")
                self.stdout.write(f"    🔗 Visiting: {url}")
                
                driver.get(url)
                time.sleep(5) # Wait for page load

                # Get Links
                link_elements = driver.find_elements(By.CSS_SELECTOR, "a.product-item-link")
                product_urls = list(set([link.get_attribute('href') for link in link_elements if link.get_attribute('href')]))
                
                # STOP CONDITION: No products found on page
                if not product_urls:
                    self.stdout.write(f"🛑 No products found on Page {page_num}. Reached end of catalog.")
                    break
                
                self.stdout.write(f"🎯 Found {len(product_urls)} laptops. Visiting...")
                
                # 2. VISIT PAGES
                for link in product_urls: 
                    try:
                        self.stdout.write(f"Visiting: {link}")
                        driver.get(link)
                        # time.sleep(1) 

                        # --- A. NAME ---
                        try:
                            name = driver.find_element(By.TAG_NAME, "h1").text.strip()
                        except:
                            self.stdout.write("   ❌ No Name found. Skipping.")
                            continue

                        # --- B. PRICE ---
                        price_value = 0.0
                        try:
                            meta_price = driver.find_element(By.XPATH, "//meta[@property='product:price:amount']")
                            price_value = float(meta_price.get_attribute("content"))
                            self.stdout.write(f"   🔹 Found via Meta Tag: {price_value}")
                        except:
                            try:
                                body_text = driver.find_element(By.TAG_NAME, "body").text
                                matches = re.findall(r'(\d[\d\s\.,]*)\s*(?:TND|DT)', body_text)
                                candidates = []
                                for m in matches:
                                    clean = m.replace(" ", "").replace(",", ".")
                                    if clean.count('.') > 1: clean = clean.replace(".", "")
                                    try:
                                        val = float(clean)
                                        if 600 < val < 10000: candidates.append(val)
                                    except: continue
                                if candidates: 
                                    price_value = min(candidates)
                                    self.stdout.write(f"   🔹 Found via Text Search: {price_value}")
                            except: pass

                        # --- C. IMAGE ---
                        image_url = ""
                        try:
                            meta_img = driver.find_element(By.XPATH, "//meta[@property='og:image']")
                            image_url = meta_img.get_attribute("content")
                        except: pass

                        # --- E. SAVE ---
                        if price_value > 0:
                            # --- MASTERCLASS EXTRACTION LOGIC (TABLE FIRST) ---
                            name_lower = name.lower()
                            
                            # Initialize Defaults
                            cpu = "N/A"
                            ram = "N/A"
                            storage = "N/A"
                            gpu = "N/A"
                            screen_size = "N/A"
                            gpu_brand = "Other"

                            # 0. ATTEMPT TO CLICK "FICHE TECHNIQUE" TAB (Force Load)
                            try:
                                tab = driver.find_element(By.CSS_SELECTOR, "#tab-label-additional-title")
                                driver.execute_script("arguments[0].click();", tab)
                                time.sleep(0.5) # Short wait for DOM update
                            except: pass

                            # 1. TRY PARSING "FICHE TECHNIQUE" TABLE
                            try:
                                # Try multiple table selectors
                                table_selectors = [
                                    "table#product-attribute-specs-table tr",
                                    "table.additional-attributes tr",
                                    ".data.table.additional-attributes tr",
                                    "#product-attribute-specs-table tr"
                                ]
                                specs_table = []
                                for sel in table_selectors:
                                    specs_table = driver.find_elements(By.CSS_SELECTOR, sel)
                                    if specs_table:
                                        self.stdout.write(f"   📋 Found Specs Table via {sel}!")
                                        break
                                
                                if specs_table:
                                    for row in specs_table:
                                        try:
                                            cols = row.find_elements(By.TAG_NAME, "td")
                                            if not cols: 
                                                cols = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
                                            
                                            if len(cols) >= 2:
                                                key = cols[0].text.lower().strip()
                                                val = cols[1].text.strip()
                                                
                                                if "processeur" in key: cpu = val
                                                elif "mémoire" in key: ram = val
                                                elif "disque" in key or "stockage" in key: storage = val
                                                elif "graphique" in key: gpu = val
                                                elif "ecran" in key: screen_size = val
                                        except: continue
                            except Exception as e:
                                self.stdout.write(f"   ⚠️ Table Parse Failed: {e}")

                            # 2. FALLBACK & INFERENCE: USE REGEX IF TABLE FAILED (OR DATA MISSING)
                            
                            # 2. FALLBACK & INFERENCE: USE REGEX IF TABLE FAILED (OR DATA MISSING)
                            
                            # --- CPU EXTRACTION ---
                            if cpu == "N/A":
                                # Apple
                                if 'apple' in name_lower or 'macbook' in name_lower:
                                    m_match = re.search(r'\b(m[1-3](?:\s*(?:pro|max|ultra))?)\b', name_lower)
                                    if m_match: cpu = f"Apple {m_match.group(1).capitalize()}"
                                
                                # Intel Core Ultra / Series 1 (Core 3/5/7)
                                elif ('core' in name_lower or 'ultra' in name_lower) and any(x in name_lower for x in [' 3 ', ' 5 ', ' 7 ', 'ultra']):
                                    ultra_match = re.search(r'ultra\s*(\d+)', name_lower)
                                    series_match = re.search(r'core\s*(\d+)\s*(\w+)', name_lower) 
                                    if ultra_match: cpu = f"Intel Core Ultra {ultra_match.group(1)}"
                                    elif series_match: cpu = f"Intel Core {series_match.group(1)} {series_match.group(2).upper()}"
                                
                                # Intel N-Series / Celeron / Pentium
                                elif re.search(r'\b(n[1-9]\d{1,3})\b', name_lower): # Matches N95, N100, N200, N4020
                                    n_match = re.search(r'\b(n[1-9]\d{1,3})\b', name_lower)
                                    cpu = f"Intel {n_match.group(1).upper()}"
                                
                                # Classic Intel Core iX (handle "i3 13ém" / "Core 9")
                                elif 'intel' in name_lower or 'i3' in name_lower or 'i5' in name_lower or 'i7' in name_lower or 'i9' in name_lower or 'core 9' in name_lower:
                                    if 'i9' in name_lower or 'core 9' in name_lower: cpu = 'Intel Core i9'
                                    elif 'i7' in name_lower: cpu = 'Intel Core i7'
                                    elif 'i5' in name_lower: cpu = 'Intel Core i5'
                                    elif 'i3' in name_lower: cpu = 'Intel Core i3'
                                    elif 'celeron' in name_lower: cpu = "Intel Celeron"
                                    elif 'pentium' in name_lower: cpu = "Intel Pentium"
                                
                                # AMD
                                elif 'amd' in name_lower or 'ryzen' in name_lower:
                                    if 'ryzen ai' in name_lower or 'ryzen al' in name_lower:
                                        ai_match = re.search(r'ryzen\s*(?:ai|al)\s*(?:max)?\s*(\d+)', name_lower)
                                        cpu = f"AMD Ryzen AI {ai_match.group(1)}" if ai_match else "AMD Ryzen AI"
                                    elif re.search(r'ryzen\s*9', name_lower): cpu = 'AMD Ryzen 9'
                                    elif re.search(r'ryzen\s*7', name_lower): cpu = 'AMD Ryzen 7'
                                    elif re.search(r'ryzen\s*5', name_lower): cpu = 'AMD Ryzen 5'
                                    elif re.search(r'ryzen\s*3', name_lower): cpu = 'AMD Ryzen 3'
                                    elif 'athlon' in name_lower: cpu = 'AMD Athlon'
                                
                                # Snapdragon
                                elif 'snapdragon' in name_lower:
                                    cpu = "Snapdragon X Elite" if "elite" in name_lower else "Snapdragon X Plus"

                            # --- RAM EXTRACTION ---
                            if ram == "N/A":
                                # Find all potential matches
                                ram_matches = re.findall(r'(\d+)\s*(?:go|gb|g)', name_lower)
                                for val_str in ram_matches:
                                    val = int(val_str)
                                    if 4 <= val <= 64: # Typical RAM range
                                         ram = f"{val}GB"
                                         break

                            # --- STORAGE EXTRACTION ---
                            if storage == "N/A":
                                # 1TB (loose regex: 1to, 1tb, 1t, 2to...)
                                tb_match = re.search(r'(\d+)\s*(?:(?:t[ob]?)|t)\b', name_lower)
                                if tb_match: 
                                    storage = f"{tb_match.group(1)}TB"
                                else:
                                    # Find candidates > 64GB
                                    candidates = re.findall(r'(\d+)\s*(?:go|gb|g)\b', name_lower)
                                    for val_str in candidates:
                                        val = int(val_str)
                                        if val >= 128:
                                             dtype = "SSD"
                                             if "hdd" in name_lower or "disque dur" in name_lower: dtype = "HDD"
                                             storage = f"{val}GB {dtype}"
                                             break

                            # --- SCREEN SIZE EXTRACTION ---
                            if screen_size == "N/A":
                                # Explicit "15.6 pouces"
                                screen_match = re.search(r'(\d+(?:[\.,]\d+)?)[\s"\']*(?:pouces|inch|”|\s|$)', name_lower)
                                found_screen = False
                                if screen_match:
                                    try:
                                        s_val = float(screen_match.group(1).replace(',', '.'))
                                        if 10.0 <= s_val <= 19.0: 
                                            screen_size = f"{s_val}\""
                                            found_screen = True
                                    except: pass
                                
                                # Inference from Model Number (e.g. HP 15-fd... -> 15.6")
                                if not found_screen:
                                    if re.search(r'\b17-', name_lower) or re.search(r'\b17\s', name_lower): screen_size = '17.3"'
                                    elif re.search(r'\b16-', name_lower) or re.search(r'\b16\s', name_lower): screen_size = '16.0"'
                                    elif re.search(r'\b15-', name_lower) or re.search(r'\b15\s', name_lower): screen_size = '15.6"'
                                    elif re.search(r'\b14-', name_lower) or re.search(r'\b14\s', name_lower): screen_size = '14.0"'
                                    elif re.search(r'\b13-', name_lower) or re.search(r'\b13\s', name_lower): screen_size = '13.3"'
                            
                            # --- GPU EXTRACTION & INFERENCE ---
                            # Priority 1: Explicit mention in Title
                            if "rtx" in name_lower: 
                                rtx_match = re.search(r'rtx\s*(\d{3,4})', name_lower)
                                gpu = f"NVIDIA RTX {rtx_match.group(1)}" if rtx_match else "NVIDIA RTX Series"
                            elif "gtx" in name_lower: 
                                gtx_match = re.search(r'gtx\s*(\d{3,4}(?:\s*ti)?)', name_lower)
                                gpu = f"NVIDIA GTX {gtx_match.group(1).upper()}" if gtx_match else "NVIDIA GTX Series"
                            elif "mx" in name_lower and "nvidia" in name_lower: gpu = "NVIDIA MX Series"
                            elif "radeon" in name_lower or "rx" in name_lower: 
                                rx_match = re.search(r'(?:rx|radeon)\s*(\d{3,4}[ms]?)', name_lower)
                                gpu = f"AMD Radeon RX {rx_match.group(1).upper()}" if rx_match else "AMD Radeon"
                            elif "arc" in name_lower: 
                                arc_match = re.search(r'arc\s*(a\d{3})', name_lower)
                                gpu = f"Intel Arc {arc_match.group(1).upper()}" if arc_match else "Intel Arc"
                            
                            # Priority 2: Inferred from CPU (Crucial for "Office" laptops with integrated graphics)
                            if gpu == "N/A":
                                if "intel" in cpu.lower():
                                    if any(x in cpu.lower() for x in ["ultra", "i7", "i5", "i9"]): gpu = "Intel Iris Xe"
                                    else: gpu = "Intel UHD Graphics" # Celeron, N-Series, i3
                                elif "amd" in cpu.lower():
                                    gpu = "AMD Radeon Graphics"
                                elif "snapdragon" in cpu.lower():
                                    gpu = "Qualcomm Adreno"
                                elif "apple" in cpu.lower():
                                    gpu = "Apple GPU"

                            # 3. DERIVE GPU BRAND (For Filter)
                            gpu_lower = gpu.lower() if gpu else ""
                            if "nvidia" in gpu_lower or "rtx" in gpu_lower or "gtx" in gpu_lower or "geforce" in gpu_lower:
                                gpu_brand = "NVIDIA"
                            elif "amd" in gpu_lower or "radeon" in gpu_lower or "ryzen" in gpu_lower:
                                gpu_brand = "AMD" 
                            elif "intel" in gpu_lower or "iris" in gpu_lower or "uhd" in gpu_lower or "arc" in gpu_lower:
                                gpu_brand = "Intel"
                            elif "apple" in gpu_lower or "m1" in gpu_lower or "m2" in gpu_lower or "m3" in gpu_lower:
                                gpu_brand = "Apple"
                            elif "qualcomm" in gpu_lower or "adreno" in gpu_lower:
                                gpu_brand = "Qualcomm"
                            else:
                                gpu_brand = "Other"

                            # 4. BRAND & SECTOR
                            KNOWN_BRANDS = ['hp', 'dell', 'lenovo', 'asus', 'acer', 'msi', 'apple', 'huawei', 'infinix', 'samsung', 'microsoft', 'gigabyte', 'razer']
                            brand_name = "Other"
                            for b in KNOWN_BRANDS:
                                if b in name_lower.split(): 
                                    brand_name = b.capitalize()
                                    break
                            if brand_name == "Hp": brand_name = "HP" 
                            if brand_name == "Msi": brand_name = "MSI"
                            
                            brand, _ = Brand.objects.get_or_create(name=brand_name)

                            sector = "Office"
                            # Enhanced Sector Logic
                            if "nvidia" in gpu_brand.lower(): sector = "Gaming"
                            if any(k in name_lower for k in ['gamer', 'gaming', 'legion', 'rog', 'tuf', 'alienware', 'omen', 'victus', 'nitro', 'loq']):
                                sector = "Gaming"
                            elif any(k in name_lower for k in ['macbook', 'xps', 'zenbook', 'creator', 'workstation', 'probook', 'thinkpad']):
                                sector = "Creative/Pro"

                            # --- SAVE ---
                            product, created = Product.objects.get_or_create(
                                name=name,
                                defaults={
                                    'brand': brand, 
                                    'sector': sector, 
                                    'image_url': image_url, 
                                    'cpu': cpu, 'ram': ram, 'storage': storage, 'screen_size': screen_size, 'gpu': gpu, 'gpu_brand': gpu_brand
                                }
                            )
                            # Clean update
                            product.brand = brand
                            product.sector = sector
                            product.image_url = image_url
                            product.cpu = cpu
                            product.ram = ram
                            product.storage = storage
                            product.screen_size = screen_size
                            product.gpu = gpu
                            product.gpu_brand = gpu_brand
                            product.save()

                            Price.objects.update_or_create(
                                product=product,
                                shop=shop,
                                defaults={'price': price_value, 'url': link}
                            )
                            total_scraped_count += 1
                            self.stdout.write(f"   ✅ {brand_name} | {cpu} | {gpu} | {ram}")

                    except Exception as e:
                        self.stdout.write(f"   ❌ Error processing {link}: {e}")

                # Next Page
                page_num += 1

            self.stdout.write(self.style.SUCCESS(f"✅ Finished. Scraped {total_scraped_count} items across {page_num} pages."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Critical Error: {e}"))
        
        finally:
            driver.quit()