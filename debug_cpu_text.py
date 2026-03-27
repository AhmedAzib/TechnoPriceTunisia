
import requests
from bs4 import BeautifulSoup
import re

url = "https://www.mytek.tn/processeur-intel-celeron-g5900-lga-1200.html"
headers = {"User-Agent": "Mozilla/5.0"}

def clean_price(price_text):
    return price_text

def extract_cpu_details(title, description):
    spec_data = {
        "category": "cpu",
        "cpu": title, 
        "brand": "Unknown",
        "clock_speed": "Unknown",
        "cores": "Unknown"
    }

    clean_text = description
    print(f"\n--- Clean Text Preview ---\n{clean_text[:500]}...\n")

    # Brand
    t_upper = title.upper()
    if "INTEL" in t_upper: spec_data["brand"] = "Intel"
    elif "AMD" in t_upper: spec_data["brand"] = "AMD"

    # Threads
    th_patterns = [
        r'NOMBRE\s+(?:DE)?\s*THREADS?\s*:\s*(\d+)',
        r'THREADS?\s*:\s*(\d+)'
    ]
    for p in th_patterns:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
             print(f"MATCH THREADS: {m.group(0)} -> {m.group(1)}")
        else:
             print(f"NO MATCH THREADS: {p}")

    # Cache
    cache_patterns = [
        r'MÉMOIRE\s+CACHE\s*:\s*([^<\n\r]+)',
        r'CACHE\s*:\s*([^<\n\r]+)'
    ]
    for p in cache_patterns:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
             print(f"MATCH CACHE: {m.group(0)} -> {m.group(1)}")
        else:
             print(f"NO MATCH CACHE: {p}")
             
    # Mem Type
    mem_patterns = [
        r'TYPES? DE MÉMOIRES?\s*:\s*([^<\n\r]+)',
        r'(?<!CACHE )(?<!VITESSE )MÉMOIRE\s*:\s*([^<\n\r]+)'
    ]
    for p in mem_patterns:
        m = re.search(p, clean_text, re.IGNORECASE)
        if m:
            print(f"MATCH MEM: {m.group(0)} -> {m.group(1)}")


print("Fetching...")
r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.content, 'html.parser')

text_content = ""
short_desc = soup.select_one('.product-info-main')
if short_desc: text_content += " " + short_desc.get_text(" ", strip=True)
attrs = soup.select_one('#additional') 
if attrs: text_content += " " + attrs.get_text(" ", strip=True)
desc_tab = soup.select_one('#description')
if desc_tab: text_content += " " + desc_tab.get_text(" ", strip=True)

extract_cpu_details("Processeur Intel Celeron G5900", text_content)
