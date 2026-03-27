
from curl_cffi import requests
import xml.etree.ElementTree as ET

def get_product_urls():
    sitemap_index_url = "https://spacenet.tn/sitemap/sitemap.xml"
    urls = []
    
    try:
        print(f"Fetching sitemap index: {sitemap_index_url}")
        resp = requests.get(sitemap_index_url, impersonate="chrome110", timeout=20)
        
        # Check if it's an index or a direct urlset
        root = ET.fromstring(resp.content)
        
        # Namespaces are common in sitemaps
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # If accessing index, find product sitemaps
        sitemaps = root.findall('s:sitemap', ns)
        if not sitemaps:
            # Maybe it's a urlset directly? (Less likely for main sitemap.xml)
            print("Direct urlset found?")
            sitemaps = [] # Handle logic if needed, but usually it's an index
        
        # Filter for product sitemaps (usually named 'products', 'produits', or numerically indexed)
        # PrestaShop often splits them. Let's just traverse all or look for specific ones
        target_sitemaps = [s.find('s:loc', ns).text for s in sitemaps if 'product' in s.find('s:loc', ns).text or 'produits' in s.find('s:loc', ns).text]
        
        if not target_sitemaps: 
             # Fallback: traverse all just in case naming is weird
             target_sitemaps = [s.find('s:loc', ns).text for s in sitemaps]

        print(f"Found {len(target_sitemaps)} candidate sitemaps.")
        
        product_urls = []
        for sm_url in target_sitemaps:
            print(f"Fetching sub-sitemap: {sm_url}")
            try:
                sm_resp = requests.get(sm_url, impersonate="chrome110", timeout=20)
                sm_root = ET.fromstring(sm_resp.content)
                locs = sm_root.findall('s:url/s:loc', ns)
                for loc in locs:
                    product_urls.append(loc.text)
            except Exception as e:
                print(f"Error fetching {sm_url}: {e}")
        
        print(f"Total separate URLs found: {len(product_urls)}")
        
        # Filter Logic
        # "just no desktop and nothing else"
        # We start by keeping things that look like laptops
        # Keys: 'pc-portable', 'macbook', 'gamer', 'laptop'
        # Exclude: 'bureau', 'desktop', 'ecran', 'accessoire', 'imprimante', 'stockage', 'tablette' unless it's a PC
        
        good_keywords = ['pc-portable', 'macbook', 'gamer', 'ordinateur-portable']
        bad_keywords = ['bureau', 'desktop', 'ecran', 'accessoire', 'tablette', 'smartphone', 'imprimante', 'consommables', 'all-in-one', 'tout-en-un']
        
        filtered = []
        for u in product_urls:
            u_lower = u.lower()
            if any(k in u_lower for k in good_keywords):
                if not any(b in u_lower for b in bad_keywords):
                    filtered.append(u)
                    
        print(f"Filtered Candidate URLs: {len(filtered)}")
        
        # Save results
        with open("spacenet_laptop_leads.txt", "w", encoding="utf-8") as f:
            for u in filtered:
                f.write(u + "\n")
                
    except Exception as e:
        print(f"Critical Sitemapping Error: {e}")

if __name__ == "__main__":
    get_product_urls()
