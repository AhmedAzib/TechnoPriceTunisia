
import os

path = r"c:\Users\USER\Documents\programmation\frontend\src\ProductsPage.jsx"

try:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_idx = -1
    end_idx = -1

    # Find start: "    if (!brand) return "UNKNOWN";"
    for i, line in enumerate(lines):
        if 'if (!brand) return "UNKNOWN";' in line:
            start_idx = i
            break

    # Find end: "];" followed shortly by "// --- COMPONENTS ---"
    if start_idx != -1:
        for i in range(start_idx, len(lines)):
            if lines[i].strip() == '];':
                # Check lookahead for COMPONETNS
                found_components = False
                for j in range(1, 20): # Look 20 lines ahead
                    if i + j < len(lines):
                        if '// --- COMPONENTS ---' in lines[i+j]:
                            found_components = True
                            break
                
                if found_components:
                    end_idx = i
                    break

    if start_idx != -1 and end_idx != -1:
        print(f"Found block: Line {start_idx+1} to {end_idx+1}")
        # Delete the block
        # We perform the deletion by keeping lines before start and after end
        new_lines = lines[:start_idx] + lines[end_idx+1:]
        
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("Successfully deleted zombie code.")
    else:
        print(f"Could not find markers. Start: {start_idx}, End: {end_idx}")

except Exception as e:
    print(f"Error: {e}")
