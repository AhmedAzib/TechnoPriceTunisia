
from curl_cffi import requests

def check_spacenet():
    urls = [
        "https://spacenet.tn/robots.txt",
        "https://spacenet.tn/18-ordinateur-portable"
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
                print(f"Content Preview (first 200 chars): {response.text[:200]}")
                # Save just to be sure we can inspect if needed
                filename = "spacenet_debug_" + url.split("/")[-1].replace(".", "_") + ".html"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(response.text)
            else:
                print("Failed to access.")
        except Exception as e:
            print(f"Error checking {url}: {e}")

if __name__ == "__main__":
    check_spacenet()
