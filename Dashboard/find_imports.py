#!/usr/bin/env python3
import ast
import os
from pathlib import Path

def extract_imports(filepath):
    """Extrai todos os imports usando AST (Abstract Syntax Tree)"""
    imports = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
            for node in ast.walk(tree):
                # Captura imports padrão
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                # Captura 'from x import y'
                elif isinstance(node, ast.ImportFrom):
                    if node.module:  # Pode ser None em 'from . import x'
                        imports.add(node.module.split('.')[0])
        except (SyntaxError, UnicodeDecodeError):
            pass
    return imports

def find_dynamic_imports(filepath):
    """Captura imports dinâmicos via regex"""
    import re
    content = Path(filepath).read_text(encoding='utf-8')
    dynamic_imports = set()
    # Padrões comuns de imports dinâmicos
    patterns = [
        r'importlib\.import_module\(["\']([a-zA-Z0-9_]+)',
        r'__import__\(["\']([a-zA-Z0-9_]+)',
        r'exec\(.*["\']import ([a-zA-Z0-9_]+)'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, content)
        dynamic_imports.update(matches)
    return dynamic_imports

def scan_project(root_dir='.'):
    """Varredura completa do projeto"""
    all_imports = set()
    for py_file in Path(root_dir).rglob('*.py'):
        all_imports.update(extract_imports(py_file))
        all_imports.update(find_dynamic_imports(py_file))
    return sorted(all_imports)

if __name__ == '__main__':
    imports = scan_project()
    with open('used_imports.txt', 'w') as f:
        f.write('\n'.join(imports))
    print(f"✅ Identificados {len(imports)} imports únicos. Salvos em used_imports.txt")