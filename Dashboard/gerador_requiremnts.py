#!/usr/bin/env python3
"""
Uso:
    python gerador_de_requirements.py codigo.py
    # ou para um projeto inteiro
    python gerador_de_requirements.py .

Ele cria/atualiza requirements.txt na pasta informada.
"""

import ast
import argparse
import pathlib
from importlib import metadata

BUILTINS = {
    # módulos da biblioteca padrão (py‑docs)
    "abc","argparse","ast","asyncio","base64","collections","concurrent",
    "contextlib","csv","datetime","functools","glob","hashlib","itertools",
    "json","logging","math","os","pathlib","re","statistics","sys","threading",
    "time","typing","uuid","warnings","zipfile",
}

def py_files(root: pathlib.Path):
    if root.is_file() and root.suffix == ".py":
        yield root
    else:
        for p in root.rglob("*.py"):
            yield p

def imports_from_file(py_path: pathlib.Path):
    tree = ast.parse(py_path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module.split(".")[0]

def build_requirement(pkg):
    if pkg in BUILTINS:
        return None  # pula stdlib
    try:
        ver = metadata.version(pkg)
        return f"{pkg}=={ver}"
    except metadata.PackageNotFoundError:
        # pacote não instalado ainda → deixe sem versão
        return pkg

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("alvo", help="Arquivo ou pasta do projeto")
    parser.add_argument("-o", "--output", default="requirements.txt",
                        help="Nome do arquivo de saída (padrão: requirements.txt)")
    args = parser.parse_args()

    root = pathlib.Path(args.alvo).resolve()
    pacotes = set()
    for py in py_files(root):
        pacotes.update(imports_from_file(py))

    linhas = sorted(filter(None, (build_requirement(p) for p in pacotes)))

    out_path = root / args.output if root.is_dir() else root.parent / args.output
    out_path.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Gerado {out_path} com {len(linhas)} dependência(s).")

if __name__ == "__main__":
    main()
