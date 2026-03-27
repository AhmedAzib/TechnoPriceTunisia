import json
import logging
import time
import os
from abc import ABC, abstractmethod
import requests

class BaseScraper(ABC):
    def __init__(self, name, output_file):
        self.name = name
        self.output_file = output_file
        self.products = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.name)

    def save_data(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Saved {len(self.products)} products to {self.output_file}")

    @abstractmethod
    def scrape(self):
        pass

    def add_product(self, product):
        # Basic validation
        if product.get('title') and product.get('price'):
            self.products.append(product)
