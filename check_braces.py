
def check_braces(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    stack = []
    
    for i, line in enumerate(lines):
        for char in line:
            if char in "{[(":
                stack.append((char, i + 1))
            elif char in "}])":
                if not stack:
                    print(f"Error: Unexpected '{char}' at line {i+1}")
                    return
                
                last, line_idx = stack.pop()
                expected = '}' if last == '{' else ']' if last == '[' else ')'
                if char != expected:
                    print(f"Error: Mismatched '{char}' at line {i+1}. Expected '{expected}' (opened at line {line_idx})")
                    return
                    
    if stack:
        char, line_idx = stack[-1]
        print(f"Error: Unclosed '{char}' at line {line_idx}")
    else:
        print("Braces are balanced.")

check_braces("frontend/src/ProductsPage.jsx")
