import json
import os

# Isso garante que ele ache o JSON na raiz do projeto, independente de onde o bot rode
CAMINHO_JSON = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'aniversarios.json')

def carregar_todos_os_dados():
    if os.path.exists(CAMINHO_JSON):
        with open(CAMINHO_JSON, 'r') as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def salvar_no_arquivo(dados):
    with open(CAMINHO_JSON, 'w') as f:
        json.dump(dados, f, indent=4)