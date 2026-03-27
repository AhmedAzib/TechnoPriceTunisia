import requests

url = "https://skymil-informatique.com/30-memoire-ram-tunisie"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers)
with open('c:/Users/USER/Documents/programmation/skymil_ram_sample.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("Saved HTML to skymil_ram_sample.html")
