
from curl_cffi import requests
import json

def test_api():
    url = "https://www.mytek.tn/myteksearch/autocomplete/index/?q=pc%20gamer"
    try:
        response = requests.get(url, impersonate="chrome110", timeout=20)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
             # Try to parse JSON to ensure validity
             try:
                 data = response.json()
                 with open("mytek_api_test_safe.json", "w", encoding="utf-8") as f:
                     json.dump(data, f, indent=2)
                 print("Saved VALID JSON.")
             except:
                 print("Not JSON content.")
                 with open("mytek_api_test_safe.txt", "w", encoding="utf-8") as f:
                     f.write(response.text)
                 print("Saved Text.")
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_api()
