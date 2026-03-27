import json
import os
from .tunisianet import TunisianetScraper
from .mytek import MytekScraper
from .skymil import SkymilScraper
from .megapc import MegaPCScraper
from .techspace import TechSpaceScraper
from .utils import clean_text

def merge_data():
    all_products = []
    seen_titles = set()
    
    files = [
        "frontend/src/data/tunisianet_new.json",
        "frontend/src/data/mytek_new.json",
        "frontend/src/data/skymil_new.json",
        "frontend/src/data/megapc_new.json",
        "frontend/src/data/techspace_new.json"
    ]
    
    for fpath in files:
        if os.path.exists(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    print(f"Loaded {len(data)} products from {fpath}")
                    for p in data:
                        # Deduplication logic
                        # We use title as key, but clean it first
                        key = clean_text(p['title']).lower()
                        
                        # Add source to key to allow same product from different sources
                        # But user said "duplicated computers between the sections" (e.g. gamer and normal)
                        # So we should deduplicate within the SAME source if the title is identical.
                        # But do we want to dedup across sources? Usually yes for a comparator.
                        # However, for now, let's keep them distinct by source, but dedup within source.
                        
                        unique_id = f"{p['source']}_{key}"
                        
                        if unique_id not in seen_titles:
                            seen_titles.add(unique_id)
                            all_products.append(p)
                except json.JSONDecodeError:
                    print(f"Error reading {fpath}")

    # Save merged
    output = "frontend/src/data/products.json" # Overwriting main file? Or new one?
    # User said "clean all that from zero". So maybe we overwrite the main one.
    # But let's be safe and write to all_products_new.json first.
    
    with open("frontend/src/data/all_products_new.json", 'w', encoding='utf-8') as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    
    print(f"Total unique products: {len(all_products)}")

def run_all():
    scrapers = [
        TunisianetScraper(),
        # MytekScraper(), # Takes long, maybe run separately or uncomment
        # SkymilScraper(),
        # MegaPCScraper(),
        # TechSpaceScraper()
    ]
    
    # automated execution? 
    # For now, let's just definition. 
    pass

if __name__ == "__main__":
    # If run directly, maybe run merge?
    merge_data()
