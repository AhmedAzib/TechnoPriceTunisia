import requests

url = "https://www.mytek.tn/smartphone.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")
with open("mytek_debug.html", "w", encoding="utf-8") as f:
    f.write(response.text)
print("Saved debug HTML.")
