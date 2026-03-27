import requests
import re
import json

def check_api():
    base_url = "https://megapc.tn"
    cat_url = "https://megapc.tn/shop/category/ordinateur-portable"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': base_url
    }
    
    print("Fetching HTML to find Build ID...")
    try:
        r = requests.get(cat_url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"Main page failed: {r.status_code}")
            return
            
        # Find Build ID
        # "buildId":"build-1757602359699"
        match = re.search(r'"buildId":"([^"]+)"', r.text)
        if not match:
            print("Could not find Build ID.")
            return
            
        build_id = match.group(1)
        print(f"Found Build ID: {build_id}")
        
        # Construct Data URL
        # URL structure: https://megapc.tn/_next/data/{build_id}/shop/category/ordinateur-portable.json
        # The page is likely mapped to /shop/category/[slug] ?? 
        # Actually dump says: "page":"/shop/[category]/[subcategory]"
        # But the url is /shop/category/ordinateur-portable
        # Wait, 'category' is the [category] and 'ordinateur-portable' is [subcategory]?
        # Or is it /shop/category/ordinateur-portable?
        
        # Let's try matching the current URL path: /shop/category/ordinateur-portable
        # next_data_url = f"{base_url}/_next/data/{build_id}/shop/category/ordinateur-portable.json"
        
        # Checking logic: if existing URL is /foo/bar, data is /_next/data/build/foo/bar.json
        data_url = f"{base_url}/_next/data/{build_id}/shop/category/ordinateur-portable.json"
        
        print(f"Fetching Data URL: {data_url}")
        r_data = requests.get(data_url, headers=headers, timeout=15)
        print(f"Data Status: {r_data.status_code}")
        
        if r_data.status_code == 200:
            data = r_data.json()
            print("Success! Keys:", data.keys())
            if 'pageProps' in data:
                print("pageProps keys:", data['pageProps'].keys())
                # Dig for products
                # Usually in pageProps -> fallback -> ... or products
    #             with open("megapc_data.json", "w") as f:
    #                 json.dump(data, f)
        else:
            print("Failed to get JSON.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()
