
from curl_cffi import requests

def check_tdiscount():
    urls = [
        "https://tdiscount.tn/robots.txt",
        "https://tdiscount.tn/sitemap.xml",
        "https://tdiscount.tn/1_index_sitemap.xml" 
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for url in urls:
        try:
            print(f"Checking {url}...")
            response = requests.get(url, headers=headers, impersonate="chrome110", timeout=15)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Content Preview: {response.text[:200]}")
                with open("tdiscount_debug_" + url.split("/")[-1].replace(".", "_") + ".html", "w", encoding="utf-8") as f:
                    f.write(response.text)
        except Exception as e:
            print(f"Error checking {url}: {e}")

if __name__ == "__main__":
    check_tdiscount()
