
from curl_cffi import requests
import xml.etree.ElementTree as ET
import gzip
import io

def fetch_sitemap_index():
    url = "https://www.mytek.tn/media/sitemap/sitemap.xml"
    print(f"Fetching Sitemap Index: {url}")
    try:
        response = requests.get(url, impersonate="chrome110", timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Failed to fetch sitemap. Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_sitemap(content):
    try:
        root = ET.fromstring(content)
        # Check if it's a sitemap index or urlset
        if 'sitemapindex' in root.tag:
            print("Detected Sitemap Index. Fetching sub-sitemaps...")
            sub_maps = []
            for sitemap in root:
                loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
                sub_maps.append(loc)
            return ("index", sub_maps)
        elif 'urlset' in root.tag:
             print("Detected URL Set.")
             urls = []
             for url in root:
                 loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
                 urls.append(loc)
             return ("urlset", urls)
        else:
            print(f"Unknown root tag: {root.tag}")
            return ("unknown", [])
    except Exception as e:
        print(f"XML Parse Error: {e}")
        return ("error", [])

def main():
    content = fetch_sitemap_index()
    if content:
        result_type, data = parse_sitemap(content)
        
        if result_type == "index":
            print(f"Found {len(data)} sub-sitemaps.")
            for sm in data:
                print(f"  - {sm}")
                # We will likely need to fetch these later, but let's see listing first
        elif result_type == "urlset":
            print(f"Found {len(data)} URLs.")
            laptop_urls = [u for u in data if "ordinateurs-portables" in u]
            print(f"Found {len(laptop_urls)} Laptop URLs.")
            for u in laptop_urls[:10]:
                print(u)

if __name__ == "__main__":
    main()
