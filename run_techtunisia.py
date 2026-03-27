
from frontend.scrapers.techtunisia import TechTunisiaScraper
import logging

# Configure logging to show info
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    scraper = TechTunisiaScraper()
    scraper.scrape()
