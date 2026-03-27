import requests
from bs4 import BeautifulSoup
import time
from .base_scraper import BaseScraper
from .utils import clean_price, clean_text

class TunisianetScraper(BaseScraper):
    def __init__(self):
        super().__init__("Tunisianet", "frontend/src/data/tunisianet_new.json")
        self.urls = [
            "https://www.tunisianet.com.tn/301-pc-portable-tunisie",
            "https://www.tunisianet.com.tn/681-pc-portable-gamer",
            "https://www.tunisianet.com.tn/703-pc-portable-pro",
            "https://www.tunisianet.com.tn/596-smartphone-tunisie"
        ]

    def scrape(self):
        for base_url in self.urls:
            page = 1
            while True:
                url = f"{base_url}?page={page}&order=product.price.asc"
                self.logger.info(f"Scraping {url}")
                
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code != 200:
                        self.logger.error(f"Failed to fetch {url}: {response.status_code}")
                        break
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    products = soup.select('.product-miniature')
                    
                    if not products:
                        self.logger.info("No more products found.")
                        break
                    
                    for prod in products:
                        try:
                            title_elem = prod.select_one('.product-title a')
                            price_elem = prod.select_one('.price')
                            img_elem = prod.select_one('.product-thumbnail img')
                            
                            if title_elem and price_elem:
                                title = clean_text(title_elem.text)
                                link = title_elem['href']
                                price = clean_price(price_elem.text)
                                image = img_elem['src'] if img_elem else ""
                                
                                # Determine category based on URL or title
                                category = "Laptops"
                                if "smartphone" in base_url:
                                    category = "Smartphones"
                                elif "gamer" in base_url:
                                    category = "Laptops (Gamer)"
                                elif "pro" in base_url:
                                    category = "Laptops (Pro)"
                                
                                self.add_product({
                                    "title": title,
                                    "price": price,
                                    "link": link,
                                    "image": image,
                                    "source": "Tunisianet",
                                    "category": category
                                })
                        except Exception as e:
                            self.logger.error(f"Error parsing product: {e}")
                            
                    # Check for next page button availability or just increment
                    # Heuristic: If we found products, try next page.
                    # Or check for 'next' button in pagination
                    next_btn = soup.select_one('a.next')
                    if not next_btn:
                        self.logger.info("Last page reached.")
                        break
                        
                    page += 1
                    time.sleep(1) # Be polite
                    
                except Exception as e:
                    self.logger.error(f"Error scraping page {page}: {e}")
                    break
        
        self.save_data()

if __name__ == "__main__":
    scraper = TunisianetScraper()
    scraper.scrape()
