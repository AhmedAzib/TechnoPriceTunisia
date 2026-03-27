from frontend.scrapers.wiki import WikiScraper
import logging

if __name__ == "__main__":
    scraper = WikiScraper()
    scraper.scrape()
