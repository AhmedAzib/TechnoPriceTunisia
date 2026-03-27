import requests
from bs4 import BeautifulSoup
import time
from .base_scraper import BaseScraper
from .utils import clean_price, clean_text

class SkymilScraper(BaseScraper):
    def __init__(self):
        super().__init__("Skymil", "frontend/src/data/skymil_new.json")
        self.urls = [
            "https://skymil-informatique.com/169-pc-portable-gamer",
            "https://skymil-informatique.com/170-pc-portable-pro"
        ]

    def scrape(self):
        for base_url in self.urls:
            page = 1
            while True:
                url = f"{base_url}?page={page}"
                self.logger.info(f"Scraping {url}")
                
                try:
                    response = requests.get(url, headers=self.headers, timeout=10)
                    if response.status_code != 200:
                        self.logger.error(f"Failed to fetch {url}: {response.status_code}")
                        break
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    products = soup.select('.product-miniature')
                    
                    if not products:
                        self.logger.info("No products found.")
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

                                category = "Laptops"
                                if "gamer" in base_url or "gamer" in title.lower():
                                    category = "Laptops (Gamer)"
                                elif "pro" in base_url:
                                    category = "Laptops (Pro)"
                                
                                self.add_product({
                                    "title": title,
                                    "price": price,
                                    "link": link,
                                    "image": image,
                                    "source": "Skymil",
                                    "category": category
                                })
                        except Exception as e:
                            self.logger.error(f"Error parsing product: {e}")
                    
                    # Pagination check
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
    scraper = SkymilScraper()
    scraper.scrape()
