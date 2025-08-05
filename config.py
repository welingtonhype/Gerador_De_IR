"""
Configurações do Sistema de Geração de Declaração de IR
"""

import os
from pathlib import Path

# Configurações de arquivos
FILES_CONFIG = {
    'EXCEL_FILE': 'IR 2024 - NÃO ALTERAR.xlsx',
    'LOGS_DIR': 'logs',
    'OUTPUT_DIR': 'output'
}

# Configurações de teste
TEST_CONFIG = {
    'TEST_CPF': '91446260968',  # CPF de teste
    'TEST_NOME': 'Fabio Roberto'
}

# Configurações do sistema
SYSTEM_CONFIG = {
    'DEBUG': True,
    'LOG_LEVEL': 'INFO',
    'CACHE_ENABLED': True,
    'CACHE_TIMEOUT': 300  # 5 minutos
}

# Configurações de validação
VALIDATION_CONFIG = {
    'CPF_VALIDATION': True,
    'SALDO_CONSISTENCY_CHECK': True,
    'ALLOW_PDF_WITH_DIFFERENCES': True  # Permite gerar PDF mesmo com diferenças
}

def get_config():
    """Retorna configuração completa do sistema"""
    return {
        'FILES': FILES_CONFIG,
        'TEST': TEST_CONFIG,
        'SYSTEM': SYSTEM_CONFIG,
        'VALIDATION': VALIDATION_CONFIG
    }

def get_excel_file_path():
    """Retorna caminho completo do arquivo Excel"""
    return os.path.join(os.getcwd(), FILES_CONFIG['EXCEL_FILE'])

def ensure_directories():
    """Garante que os diretórios necessários existam"""
    for dir_name in [FILES_CONFIG['LOGS_DIR'], FILES_CONFIG['OUTPUT_DIR']]:
        Path(dir_name).mkdir(exist_ok=True)

# Inicializar diretórios
ensure_directories() 