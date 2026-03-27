from frontend.scrapers.tdiscount import TdiscountScraper
import logging

# Configure logging to show info
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    scraper = TdiscountScraper()
    scraper.scrape()
