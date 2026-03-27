import traceback
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from django.core.management.base import BaseCommand
from products.models import Product, Brand, Sector, PriceHistory

class Command(BaseCommand):
    help = 'Debug Database Saving Issues'

    def handle(self, *args, **kwargs):
        print("\n[DEBUG] STARTING DIAGNOSTIC TEST...")
        
        # TEST 1: Database Write Check
        print("\n[1] Testing Database Connection...")
        try:
            sec, _ = Sector.objects.get_or_create(name="TEST_SECTOR")
            br, _ = Brand.objects.get_or_create(name="TEST_BRAND")
            prod = Product.objects.create(
                name="TEST_LAPTOP_123", 
                link="http://test.com/123", 
                sector=sec, 
                brand=br, 
                current_price=999.00
            )
            print("   SUCCESS: Database is Writable! (Created Test Laptop)")
            # Cleanup
            prod.delete()
        except Exception as e:
            print(f"   FATAL DB ERROR: {e}")
            print("   STOPPING. Fix your models/database first.")
            return
            
        # TEST 2: Scraper Save Check
        print("\n[2] Testing Real Scrape Save...")
        driver = uc.Chrome()
        try:
            driver.get("https://www.mytek.tn/informatique/ordinateurs-portables/pc-portable.html")
            print("   Navigated to MyTek. Finding one laptop...")
            
            # Find first item only
            name_el = driver.find_element(By.XPATH, "//a[contains(@class, 'product-item-link')]")
            
            print(f"   Found Laptop: '{name_el.text}'")
            
            # Extract details
            title = name_el.text.strip()
            link = name_el.get_attribute("href")
            
            box = name_el.find_element(By.XPATH, "./ancestor::li[contains(@class, 'product-item')]")
            price_el = box.find_element(By.CSS_SELECTOR, "[data-price-amount]")
            price_raw = price_el.get_attribute("data-price-amount")
            price = float(price_raw)
            
            print(f"   Extracted Data -> Price: {price}, Link Length: {len(link)}")
            
            # ATTEMPT SAVE (With NO safety net)
            print("   Attempting to Save to DB...")
            
            sec, _ = Sector.objects.get_or_create(name="Office")
            brand_name = title.split()[0]
            br, _ = Brand.objects.get_or_create(name=brand_name)
            
            p, created = Product.objects.get_or_create(
                link=link,
                defaults={'name': title, 'sector': sec, 'brand': br, 'current_price': price}
            )
            PriceHistory.objects.create(product=p, price=price)
            
            print(f"   SUCCESS! Real Product Saved: {p.name}")
            print("   THE DATABASE IS WORKING. The issue was likely a one-off glitch or solved.")
            
        except Exception as e:
            print("\n!!! CAUGHT THE BUG !!!")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {e}")
            print("Traceback:")
            traceback.print_exc()
        finally:
            driver.quit()
