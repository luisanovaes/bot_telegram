import json
import os

def carregar_todos_os_dados(arquivo_dados='aniversarios.json'):
    """Carrega dados do arquivo JSON"""
    if os.path.exists(arquivo_dados):
        with open(arquivo_dados, 'r') as f:
            return json.load(f)
    return {}

def salvar_no_arquivo(dados_completos, arquivo_dados='aniversarios.json'):
    """Salva dados no arquivo JSON"""
    with open(arquivo_dados, 'w') as f:
        json.dump(dados_completos, f, indent=4)
