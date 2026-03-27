import requests
from bs4 import BeautifulSoup
import time
from .base_scraper import BaseScraper
from .utils import clean_price, clean_text

class TechSpaceScraper(BaseScraper):
    def __init__(self):
        super().__init__("TechSpace", "frontend/src/data/techspace_new.json")
        self.urls = [
            "https://techspace.tn/pc-portable/"
        ]

    def scrape(self):
        for base_url in self.urls:
            page = 1
            while True:
                if page == 1:
                    url = base_url
                else:
                    url = f"{base_url}page/{page}/"
                
                self.logger.info(f"Scraping {url}")
                
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code != 200: # TechSpace often returns 404 for page out of range
                        self.logger.info(f"Page {page} returned {response.status_code}, assuming end.")
                        break
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    products = soup.select('.product-type-simple') # Common woo commerce class
                    
                    if not products:
                         # Try another common selector
                        products = soup.select('.product')

                    if not products:
                        self.logger.info("No products found.")
                        break
                    
                    for prod in products:
                        try:
                            title_elem = prod.select_one('.woocommerce-loop-product__title')
                            price_elem = prod.select_one('.price .amount')
                            img_elem = prod.select_one('img')
                            link_elem = prod.select_one('a.woocommerce-LoopProduct-link')
                            
                            if title_elem and price_elem:
                                title = clean_text(title_elem.text)
                                link = link_elem['href'] if link_elem else ""
                                price = clean_price(price_elem.text)
                                image = img_elem['src'] if img_elem else ""
                                
                                self.add_product({
                                    "title": title,
                                    "price": price,
                                    "link": link,
                                    "image": image,
                                    "source": "TechSpace",
                                    "category": "Laptops"
                                })
                        except Exception as e:
                            self.logger.error(f"Error parsing product: {e}")

                    # Check for next page
                    next_btn = soup.select_one('a.next')
                    if not next_btn:
                        self.logger.info("Last page reached.")
                        break
                        
                    page += 1
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"Error scraping page {page}: {e}")
                    break
        
        self.save_data()

if __name__ == "__main__":
    scraper = TechSpaceScraper()
    scraper.scrape()
