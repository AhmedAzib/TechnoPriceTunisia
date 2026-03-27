
from django.core.management.base import BaseCommand
from products.models import Product
import re

class Command(BaseCommand):
    help = 'Normalize product data by inferring specs from the name field (Offline)'

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        count = 0
        
        self.stdout.write("--- Starting Normalization ---")

        for p in products:
            name_lower = p.name.lower()
            original_data = f"{p.cpu}|{p.ram}|{p.storage}|{p.gpu}"
            
            # --- CPU INFERENCE ---
            if p.cpu in ["N/A", None, ""]:
                # Apple
                if 'apple' in name_lower or 'macbook' in name_lower:
                    m_match = re.search(r'\b(m[1-3](?:\s*(?:pro|max|ultra))?)\b', name_lower)
                    if m_match: p.cpu = f"Apple {m_match.group(1).capitalize()}"
                
                # Intel Core Ultra / Series 1 (Core 3/5/7)
                elif ('core' in name_lower or 'ultra' in name_lower) and any(x in name_lower for x in [' 3 ', ' 5 ', ' 7 ', 'ultra']):
                    ultra_match = re.search(r'ultra\s*(\d+)', name_lower)
                    series_match = re.search(r'core\s*(\d+)\s*(\w+)', name_lower) 
                    if ultra_match: p.cpu = f"Intel Core Ultra {ultra_match.group(1)}"
                    elif series_match: p.cpu = f"Intel Core {series_match.group(1)} {series_match.group(2).upper()}"
                
                # Intel N-Series / Celeron / Pentium
                elif re.search(r'\b(n[1-9]\d{1,3})\b', name_lower): # Matches N95, N100, N200, N4020
                    n_match = re.search(r'\b(n[1-9]\d{1,3})\b', name_lower)
                    p.cpu = f"Intel {n_match.group(1).upper()}"
                
                # Classic Intel Core iX (handle "i3 13ém" / "Core 9")
                elif 'intel' in name_lower or 'i3' in name_lower or 'i5' in name_lower or 'i7' in name_lower or 'i9' in name_lower or 'core 9' in name_lower:
                    if 'i9' in name_lower or 'core 9' in name_lower: p.cpu = 'Intel Core i9'
                    elif 'i7' in name_lower: p.cpu = 'Intel Core i7'
                    elif 'i5' in name_lower: p.cpu = 'Intel Core i5'
                    elif 'i3' in name_lower: p.cpu = 'Intel Core i3'
                    elif 'celeron' in name_lower: p.cpu = "Intel Celeron"
                    elif 'pentium' in name_lower: p.cpu = "Intel Pentium"
                
                # AMD
                elif 'amd' in name_lower or 'ryzen' in name_lower:
                    if 'ryzen ai' in name_lower or 'ryzen al' in name_lower:
                        ai_match = re.search(r'ryzen\s*(?:ai|al)\s*(?:max)?\s*(\d+)', name_lower)
                        p.cpu = f"AMD Ryzen AI {ai_match.group(1)}" if ai_match else "AMD Ryzen AI"
                    elif re.search(r'ryzen\s*9', name_lower): p.cpu = 'AMD Ryzen 9'
                    elif re.search(r'ryzen\s*7', name_lower): p.cpu = 'AMD Ryzen 7'
                    elif re.search(r'ryzen\s*5', name_lower): p.cpu = 'AMD Ryzen 5'
                    elif re.search(r'ryzen\s*3', name_lower): p.cpu = 'AMD Ryzen 3'
                    elif 'athlon' in name_lower: p.cpu = 'AMD Athlon'
                
                # Snapdragon
                elif 'snapdragon' in name_lower:
                    p.cpu = "Snapdragon X Elite" if "elite" in name_lower else "Snapdragon X Plus"

            # --- RAM INFERENCE ---
            if p.ram in ["N/A", None, ""]:
                # Find all potential matches
                ram_matches = re.findall(r'(\d+)\s*(?:go|gb|g)', name_lower)
                for val_str in ram_matches:
                    val = int(val_str)
                    if 4 <= val <= 64: # Typical RAM range
                         p.ram = f"{val}GB"
                         break

            # --- STORAGE INFERENCE ---
            if p.storage in ["N/A", None, ""]:
                # 1TB (loose regex: 1to, 1tb, 1t, 2to...)
                tb_match = re.search(r'(\d+)\s*(?:(?:t[ob]?)|t)\b', name_lower)
                if tb_match: 
                    p.storage = f"{tb_match.group(1)}TB"
                else:
                    # Find candidates > 64GB
                    candidates = re.findall(r'(\d+)\s*(?:go|gb|g)\b', name_lower)
                    found_storage = False
                    for val_str in candidates:
                        val = int(val_str)
                        if val >= 128:
                             dtype = "SSD"
                             # Check if 'ssd' follows this specific match? Hard with findall.
                             # Simple check: if 'hdd' is anywhere, assume HDD, else SSD.
                             if "hdd" in name_lower or "disque dur" in name_lower: dtype = "HDD"
                             p.storage = f"{val}GB {dtype}"
                             found_storage = True
                             break

            # --- SCREEN INFERENCE ---
            if p.screen_size in ["N/A", None, ""]:
                 # Explicit "15.6 pouces"
                 screen_match = re.search(r'(\d+(?:[\.,]\d+)?)[\s"\']*(?:pouces|inch|”|\s|$)', name_lower)
                 found_screen = False
                 if screen_match:
                     try:
                         val = float(screen_match.group(1).replace(',', '.'))
                         if 10.0 <= val <= 19.0: 
                             p.screen_size = f"{val}\""
                             found_screen = True
                     except: pass
                 
                 # Inference from Model Number (e.g. HP 15-fd... -> 15.6")
                 if not found_screen:
                     if re.search(r'\b17-', name_lower) or re.search(r'\b17\s', name_lower): p.screen_size = '17.3"'
                     elif re.search(r'\b16-', name_lower) or re.search(r'\b16\s', name_lower): p.screen_size = '16.0"'
                     elif re.search(r'\b15-', name_lower) or re.search(r'\b15\s', name_lower): p.screen_size = '15.6"'
                     elif re.search(r'\b14-', name_lower) or re.search(r'\b14\s', name_lower): p.screen_size = '14.0"'
                     elif re.search(r'\b13-', name_lower) or re.search(r'\b13\s', name_lower): p.screen_size = '13.3"'

            # --- GPU INFERENCE ---
            if p.gpu in ["N/A", None, ""]:
                # Explicit
                if "rtx" in name_lower: 
                    rtx_match = re.search(r'rtx\s*(\d{3,4})', name_lower)
                    p.gpu = f"NVIDIA RTX {rtx_match.group(1)}" if rtx_match else "NVIDIA RTX Series"
                elif "gtx" in name_lower: 
                    gtx_match = re.search(r'gtx\s*(\d{3,4}(?:\s*ti)?)', name_lower)
                    p.gpu = f"NVIDIA GTX {gtx_match.group(1).upper()}" if gtx_match else "NVIDIA GTX Series"
                elif "mx" in name_lower and "nvidia" in name_lower: p.gpu = "NVIDIA MX Series"
                elif "radeon" in name_lower or "rx" in name_lower: 
                    rx_match = re.search(r'(?:rx|radeon)\s*(\d{3,4}[ms]?)', name_lower)
                    p.gpu = f"AMD Radeon RX {rx_match.group(1).upper()}" if rx_match else "AMD Radeon"
                elif "arc" in name_lower: 
                    arc_match = re.search(r'arc\s*(a\d{3})', name_lower)
                    p.gpu = f"Intel Arc {arc_match.group(1).upper()}" if arc_match else "Intel Arc"
                
                # Implicit (Integrated)
                elif "intel" in str(p.cpu).lower(): # ... (rest same)
                    if any(x in str(p.cpu).lower() for x in ["ultra", "i7", "i5", "i9"]): p.gpu = "Intel Iris Xe"
                    else: p.gpu = "Intel UHD Graphics" # N-Series etc.
                elif "amd" in str(p.cpu).lower():
                    p.gpu = "AMD Radeon Graphics"
                elif "snapdragon" in str(p.cpu).lower():
                    p.gpu = "Qualcomm Adreno"
                elif "apple" in str(p.cpu).lower():
                     p.gpu = "Apple GPU"
            
            # --- SECTOR CORRECTION ---
            # If GPU is RTX/GTX, ensure Sector is Gaming
            if p.gpu and any(x in p.gpu.lower() for x in ['rtx', 'gtx']):
                p.sector = "Gaming"
            
            # --- GPU BRAND INFERENCE ---
            # Always re-calculate based on GPU field
            gpu_str = str(p.gpu).lower()
            if "nvidia" in gpu_str or "rtx" in gpu_str or "gtx" in gpu_str: p.gpu_brand = "NVIDIA"
            elif "amd" in gpu_str or "radeon" in gpu_str: p.gpu_brand = "AMD"
            elif "intel" in gpu_str or "iris" in gpu_str or "uhd" in gpu_str: p.gpu_brand = "Intel"
            elif "apple" in gpu_str: p.gpu_brand = "Apple"
            elif "qualcomm" in gpu_str or "adreno" in gpu_str: p.gpu_brand = "Qualcomm"
            else: p.gpu_brand = "Other"

            # Check for changes
            new_data = f"{p.cpu}|{p.ram}|{p.storage}|{p.gpu}"
            if new_data != original_data:
                p.save()
                count += 1
                if count % 50 == 0: self.stdout.write(f"Updated {count} products...")

        self.stdout.write(f"Done! Normalized {count} products.")
