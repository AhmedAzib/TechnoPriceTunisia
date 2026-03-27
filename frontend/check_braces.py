
import re

def check_braces(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stack = []
    in_block_comment = False
    
    for i, line in enumerate(lines):
        line_num = i + 1
        line_content = line.strip()
        
        # Strip block comments
        temp_line = ""
        j = 0
        while j < len(line):
            if in_block_comment:
                if line[j:j+2] == '*/':
                    in_block_comment = False
                    j += 2
                else:
                    j += 1
            else:
                if line[j:j+2] == '/*':
                    in_block_comment = True
                    j += 2
                elif line[j:j+2] == '//':
                    break 
                else:
                    temp_line += line[j]
                    j += 1
        
        for char in temp_line:
            if char in '{[(':
                stack.append((char, line_num))
            elif char in '}])':
                if not stack:
                    print(f"Error: Unexpected closing '{char}' at line {line_num}")
                    return
                last_char, last_line = stack.pop()
                if line_num > 2075:
                     print(f"Debug: '{char}' at {line_num} closed '{last_char}' from {last_line}")
                
                expected = {'}':'{', ']':'[', ')':'('}[char]
                if last_char != expected:
                    print(f"Error: Mismatched closing '{char}' at line {line_num}. Expected closing for '{last_char}' from line {last_line}")
                    return

    if stack:
        char, line = stack.pop()
        print(f"Error: Unclosed '{char}' from line {line}")

check_braces('src/ProductsPage.jsx')
