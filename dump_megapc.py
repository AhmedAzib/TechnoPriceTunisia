import requests

def dump_html():
    url = "https://megapc.tn/shop/category/ordinateur-portable"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        with open("megapc_dump.html", "w", encoding="utf-8") as f:
            f.write(r.text)
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_html()
