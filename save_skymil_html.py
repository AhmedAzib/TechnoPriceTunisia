import requests

url = "https://skymil-informatique.com/25-processeur-intel"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    with open("skymil_debug.html", "w", encoding="utf-8") as f:
        f.write(response.text)
        
    print("Successfully saved skymil_debug.html")

except Exception as e:
    print(f"Error: {e}")
