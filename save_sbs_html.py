import requests

URL = "https://www.sbsinformatique.com/cartes-graphiques-tunisie/carte-graphique-gigabyte-geforce-rtx-5050-windforce-oc-8g-tunisie"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def save_html():
    print(f"Fetching {URL}...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        with open("debug_sbs.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print("Saved to debug_sbs.html")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    save_html()
