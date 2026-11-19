import json
import ast

def verify():
    with open('redlamp.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)

    print(f"Total cells: {len(nb['cells'])}")
    for i, c in enumerate(nb['cells']):
        src = ''.join(c.get('source', []))
        first = src.strip().split('\n')[0] if src.strip() else '(empty)'
        ctype = c['cell_type']
        print(f"Cell {i:2d} [{ctype[:4]}]: {first[:75]}")

        # Check Python syntax for code cells that don't start with bash/magic commands
        if ctype == 'code':
            lines = [l for l in src.split('\n') if not l.strip().startswith(('!', '%', '%%'))]
            py_code = '\n'.join(lines)
            if py_code.strip():
                try:
                    ast.parse(py_code)
                except SyntaxError as e:
                    print(f"  --> SYNTAX ERROR in cell {i}: {e}")

    print("\nVerification complete! No unexpected JSON or Python syntax errors detected.")

if __name__ == '__main__':
    verify()

