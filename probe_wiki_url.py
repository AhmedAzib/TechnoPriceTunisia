import requests

urls = [
    "https://www.wiki.tn/composants-informatique/processeur-70.html",
    "https://www.wiki.tn/c/composants-informatique/processeur",
    "https://www.wiki.tn/composants-informatique/processeurs-137.html",
    "https://www.wiki.tn/composants/processeurs-70.html"
]

for url in urls:
    try:
        r = requests.head(url, timeout=5)
        print(f"{url}: {r.status_code}")
    except Exception as e:
        print(f"{url}: Error {e}")
