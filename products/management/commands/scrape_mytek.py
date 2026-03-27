import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from django.core.management.base import BaseCommand
from products.models import Product, Brand, Sector, PriceHistory

class Command(BaseCommand):
    help = 'ULTIMATE SCRAPER - 500 Items with Details (Stable)'

    def handle(self, *args, **kwargs):
        print("🤖 Launching ULTIMATE 500 ITEM SCRAPER (Stable Mode)...")
        
        # 1. INIT DRIVER WITH STABILITY OPTIONS
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        
        # use_subprocess=True helps prevent the "Target window already closed" error
        driver = uc.Chrome(options=options, use_subprocess=True)
        
        print("   🌐 Navigating to MyTek...")
        try:
            driver.get("https://www.mytek.tn/")
        except Exception as e:
            print(f"   ⚠️ Initial Navigation Error: {e}")
            print("   🔄 Retrying navigation...")
            time.sleep(2)
            driver.get("https://www.mytek.tn/")
            
        time.sleep(5)
        
        # 2. MANUAL NAVIGATION PROMPT
        print("\n" + "🚨"*20)
        print("👉 ACTION REQUIRED: Navigate to 'PC Portable' 🚨")
        print("1. Click 'Informatique' -> 'PC Portable'.")
        print("2. Close any Popups.")
        print("3. SCROLL DOWN to the bottom of Page 1.")
        print("🚨"*20 + "\n")
        input("⌨️  Press ENTER here when you see the laptops to start collecting 500 items...")
        
        total_saved = 0
        target_count = 500
        page_number = 1
        
        while total_saved < target_count:
            print(f"\n   📄 Scraping Page {page_number}... (Total: {total_saved}/{target_count})")
            
            # 3. JS INJECTION (Robust extraction)
            items = driver.execute_script("""
                var results = [];
                var boxes = document.querySelectorAll('li.product-item, div.product-item, .item.product');
                boxes.forEach(box => {
                    try {
                        var nameEl = box.querySelector('a.product-item-link');
                        var priceEl = box.querySelector('[data-price-amount]'); 
                        var priceText = "0";
                        if (priceEl) {
                            priceText = priceEl.getAttribute('data-price-amount');
                        } else {
                            var visualPrice = box.querySelector('.price');
                            if (visualPrice) priceText = visualPrice.innerText;
                        }
                        if (nameEl) {
                            results.push({
                                name: nameEl.innerText.trim(),
                                link: nameEl.href,
                                price_raw: priceText
                            });
                        }
                    } catch(e) {}
                });
                return results;
            """)
            
            if not items:
                print("     ⚠️ No items found on this page via JS.")
            else:
                print(f"     🎯 Found {len(items)} items. Analyzing Specs...")
                
                page_saved_count = 0
                for item in items:
                    if total_saved >= target_count: break
                    
                    try:
                        title = item['name']
                        link = item['link']
                        raw_price = str(item['price_raw'])
                        
                        # --- PRICE CLEANING ---
                        clean_price_str = re.sub(r'[^\d,.]', '', raw_price).replace(',', '.')
                        try:
                            price = float(clean_price_str)
                        except:
                            price = 0.0
                            
                        # --- SPEC EXTRACTION (REGEX MAGIC) ---
                        name_lower = title.lower()
                        
                        # CPU
                        cpu = "N/A"
                        if 'apple' in name_lower and 'm1' in name_lower: cpu = "Apple M1"
                        elif 'apple' in name_lower and 'm2' in name_lower: cpu = "Apple M2"
                        elif 'apple' in name_lower and 'm3' in name_lower: cpu = "Apple M3"
                        elif 'i9' in name_lower: cpu = "Intel Core i9"
                        elif 'i7' in name_lower: cpu = "Intel Core i7"
                        elif 'i5' in name_lower: cpu = "Intel Core i5"
                        elif 'i3' in name_lower: cpu = "Intel Core i3"
                        elif 'ryzen 9' in name_lower: cpu = "AMD Ryzen 9"
                        elif 'ryzen 7' in name_lower: cpu = "AMD Ryzen 7"
                        elif 'ryzen 5' in name_lower: cpu = "AMD Ryzen 5"
                        elif 'ryzen 3' in name_lower: cpu = "AMD Ryzen 3"
                        elif 'celeron' in name_lower: cpu = "Intel Celeron"
                        else: cpu = "Other Proccessor"

                        # RAM
                        ram = "N/A"
                        ram_match = re.search(r'(\d+)\s*(?:go|gb)', name_lower)
                        if ram_match: ram = f"{ram_match.group(1)}GB"

                        # Storage
                        storage = "N/A"
                        tb_match = re.search(r'(\d+)\s*(?:to|tb)', name_lower)
                        gb_match = re.search(r'(\d+)\s*(?:go|gb)\s*(?:ssd|hdd)', name_lower)
                        if tb_match: storage = f"{tb_match.group(1)}TB"
                        elif gb_match: storage = f"{gb_match.group(1)}GB"
                        
                        # Screen
                        screen = "N/A"
                        screen_match = re.search(r'(\d+(?:[\.,]\d+)?)\s*(?:pouces|")', name_lower)
                        if screen_match: screen = f"{screen_match.group(1).replace(',', '.')}\""
                        elif "15.6" in name_lower: screen = '15.6"'
                        elif "17.3" in name_lower: screen = '17.3"'
                        elif "14" in name_lower: screen = '14.0"'
                        
                        # GPU Brand
                        gpu_brand = "Other"
                        if "rtx" in name_lower or "gtx" in name_lower or "nvidia" in name_lower: gpu_brand = "NVIDIA"
                        elif "radeon" in name_lower or "amd" in name_lower: gpu_brand = "AMD"
                        elif "iris" in name_lower or "intel" in name_lower: gpu_brand = "Intel"
                        
                        # --- SAVE TO DB ---
                        sec, _ = Sector.objects.get_or_create(name="Office")
                        brand_name = title.split()[0] if title else "Unknown"
                        brand, _ = Brand.objects.get_or_create(name=brand_name)
                        
                        # Create or Update with FULL SPECS
                        prod, created = Product.objects.get_or_create(
                            link=link,
                            defaults={
                                'name': title, 
                                'sector': sec, 
                                'brand': brand, 
                                'current_price': price,
                                'cpu': cpu,
                                'ram': ram,
                                'storage': storage,
                                'screen_size': screen,
                                'gpu_brand': gpu_brand
                            }
                        )
                        
                        # Update specs even if exists
                        prod.cpu = cpu
                        prod.ram = ram
                        prod.storage = storage
                        prod.screen_size = screen
                        prod.gpu_brand = gpu_brand
                        if prod.current_price != price:
                            prod.current_price = price
                            PriceHistory.objects.create(product=prod, price=price)
                        prod.save()
                        
                        if created:
                             PriceHistory.objects.create(product=prod, price=price)
                             
                        print(f"     ✅ Saved: {title[:25]}... | {cpu} | {ram} | {price} DT")
                        total_saved += 1
                        page_saved_count += 1
                        
                    except Exception as e:
                        continue
            
            # --- PAGINATION ---
            if total_saved >= target_count:
                print(f"\n🎉 GOAL REACHED! Saved {total_saved} items.")
                break
                
            next_page_num = page_number + 1
            print(f"     👀 Moving to Page {next_page_num}...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            try:
                # Robust JS click for pagination
                clicked = driver.execute_script(f"""
                    var links = document.querySelectorAll('a');
                    for (var i=0; i<links.length; i++) {{
                        if (links[i].innerText.trim() === "{next_page_num}") {{
                            links[i].click();
                            return true;
                        }}
                    }}
                    return false;
                """)
                
                if not clicked:
                    # Fallback to Selenium Link Text
                    next_link = driver.find_element(By.LINK_TEXT, str(next_page_num))
                    driver.execute_script("arguments[0].click();", next_link)
                
                print(f"     ➡️  Page {next_page_num} loading...")
                time.sleep(6)
                page_number += 1
            except:
                print("     🛑 No more pages found or Pagination blocked. Done.")
                break
        
        print(f"\n🏁 Scraper Finished. Total Saved: {total_saved}")
        driver.quit()