import json
import os
import re

def refine_filter():
    path = "frontend/src/data/tunisianet_new.json"
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        initial_count = len(data)
        cleaned_data = []
        
        desktop_keywords = [
            "pc de bureau", "unité centrale", "unite centrale", 
            "all in one", "desktop", "thinkcentre", "optiplex", 
            "prodesk", "elitedesk", "ideacentre", "veriton", 
            "sff ", "tour ", "tower"
        ]
        
        removed_items = []
        
        for p in data:
            t = (p.get('title') or "").lower()
            
            # KEY: We need to emulate the "Unknown" CPU logic.
            # If the title mentions Core, Ryzen, Intel, AMD, Celeron, Pentium, it's NOT Unknown.
            
            cpu_keywords = [
                "intel", "amd", "ryzen", "core", "i3", "i5", "i7", "i9", "ultra",
                "celeron", "pentium", "athlon", "snapdragon", "apple", "m1", "m2", "m3"
            ]
            
            has_cpu_info = any(k in t for k in cpu_keywords)
            
            is_desktop = any(k in t for k in desktop_keywords)
            
            # Deletion Condition:
            # 1. It IS a desktop (contains keyword)
            # 2. It does NOT have obvious CPU info (which usually leads to "Unknown" category)
            # 3. NOT explicitly "Portable"
            
            should_remove = False
            
            if is_desktop and not ("portable" in t or "laptop" in t):
                if not has_cpu_info:
                    should_remove = True
                    
            if should_remove:
                removed_items.append(t)
            else:
                cleaned_data.append(p)
                
        final_count = len(cleaned_data)
        removed_count = initial_count - final_count
        
        print(f"Refined Filter Analysis:")
        print(f"Initial: {initial_count}")
        print(f"Removed: {removed_count}")
        print(f"Final: {final_count}")
        
        if removed_count > 0:
            print("\nExamples of Removed Items:")
            for x in removed_items[:10]:
                print(f" - {x}")

            # Apply changes? User said "return them... retun those 500".
            # I have returned them (restored).
            # Now "delete any disck top... in uncknown".
            # I will apply this refined filter.
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    refine_filter()
