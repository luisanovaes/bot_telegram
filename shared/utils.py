import re
from datetime import datetime

def validar_data(data_str):
    """Valida se a data está no formato DD/MM"""
    padrao_data = r"(\d{1,2}/\d{1,2})"
    return re.search(padrao_data, data_str)

def extrair_nome_e_data(frase_completa):
    """Extrai nome e data de uma frase"""
    padrao_data = r"(\d{1,2}/\d{1,2})"
    resultado = re.search(padrao_data, frase_completa)
    
    if not resultado:
        return None, None
    
    data = resultado.group(1)
    nome = frase_completa.replace(data, "").strip()
    
    return nome, data

def proximoaniversario(dia, mes):
    """Calcula quantos dias faltam para o próximo aniversário"""
    hoje = datetime.now()
    proxima_data = datetime(hoje.year, int(mes), int(dia))
    
    if proxima_data < hoje:
        proxima_data = datetime(hoje.year + 1, int(mes), int(dia))
    
    diferenca = proxima_data - hoje
    return diferenca.days
