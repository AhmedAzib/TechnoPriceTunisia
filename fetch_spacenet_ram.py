import requests

url = "https://spacenet.tn/25-barrette-memoire"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)
with open("c:/Users/USER/Documents/programmation/spacenet_ram_page1.html", "w", encoding="utf-8") as f:
    f.write(response.text)
print("Saved HTML")
