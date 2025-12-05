# import sys, os
#
# def setup_path():
#     project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
#     if project_root not in sys.path:
#         sys.path.append(project_root)

import sys,os
from pathlib import Path

def setup_path():
    # Pega o caminho absoluto da pasta onde este arquivo (setup.py) está: .../Principal
    current_dir = Path(__file__).resolve().parent

    # Pega o pai desse diretório (a raiz do projeto): .../Barulho_belem
    project_root = current_dir.parent

    # Adiciona ao sys.path se ainda não estiver lá
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))