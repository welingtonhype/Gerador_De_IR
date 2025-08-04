"""
Configurações do Sistema Gerador de IR
Centraliza todas as configurações do sistema
"""

import os
from pathlib import Path

# Configurações do Servidor
SERVER_CONFIG = {
    'HOST': os.environ.get('HOST', '0.0.0.0'),
    'PORT': int(os.environ.get('PORT', 10000)),
    'DEBUG': os.environ.get('DEBUG', 'False').lower() == 'true',
    'THREADED': True
}

# Configurações da Aplicação
APP_CONFIG = {
    'NAME': 'Gerador de IR - Hype Empreendimentos',
    'VERSION': '1.0.0',
    'DESCRIPTION': 'Sistema para geração de declarações de IR',
    'COMPANY': 'Hype Empreendimentos e Incorporações SA',
    'SUPPORT_EMAIL': 'suporte@hype.com.br',
    'SUPPORT_PHONE': '(11) 9999-9999'
}

# Configurações de Arquivos
FILES_CONFIG = {
    'EXCEL_FILE': 'IR 2024 - NÃO ALTERAR.xlsx',
    'SCRIPT_FILE': 'Scripts/gerador_ir_refatorado.py',
    'LOGO_HYPE': 'Imagens/Imagem2.png',
    'LOGO_BRASAO': 'Imagens/Imagem1.png',
    'LOG_FILE': 'server.log',
    'IR_LOG_FILE': 'gerador_ir.log'
}

# Configurações de Validação
VALIDATION_CONFIG = {
    'CPF_MIN_LENGTH': 11,
    'CPF_MAX_LENGTH': 14,
    'CPF_REGEX': r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
    'CPF_NUMBERS_REGEX': r'^\d{11}$'
}

# Configurações de PDF
PDF_CONFIG = {
    'PAGE_SIZE': 'A4',
    'MARGINS': {
        'LEFT': 0.3,
        'RIGHT': 0.8,
        'TOP': 0.8,
        'BOTTOM': 0.8
    },
    'FONTS': {
        'TITLE': 'Helvetica-Bold',
        'NORMAL': 'Helvetica',
        'SMALL': 'Helvetica'
    },
    'FONT_SIZES': {
        'TITLE': 10,
        'NORMAL': 10,
        'SMALL': 8
    },
    'COLORS': {
        'PRIMARY': '#018672',
        'SUCCESS': '#28a745',
        'ERROR': '#dc3545',
        'WARNING': '#ffc107',
        'INFO': '#17a2b8',
        'BLACK': '#000000',
        'GRAY': '#D9D9D9'
    }
}

# Configurações de API
API_CONFIG = {
    'ENDPOINTS': {
        'HEALTH': '/api/health',
        'SEARCH_CLIENT': '/api/buscar-cliente',
        'GENERATE_PDF': '/api/gerar-pdf',
        'DOWNLOAD_PDF': '/api/download-pdf/<filename>'
    },
    'TIMEOUTS': {
        'SEARCH': 10,
        'GENERATE_PDF': 30,
        'DOWNLOAD': 60
    },
    'CORS_ORIGINS': [
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'https://*.render.com',
        'https://*.onrender.com'
    ]
}

# Configurações de Logging
LOGGING_CONFIG = {
    'LEVEL': 'INFO',
    'FORMAT': '%(asctime)s - %(levelname)s - %(message)s',
    'DATE_FORMAT': '%Y-%m-%d %H:%M:%S',
    'MAX_BYTES': 10 * 1024 * 1024,  # 10MB
    'BACKUP_COUNT': 5
}

# Configurações de Cache
CACHE_CONFIG = {
    'ENABLED': True,
    'TTL': 300,  # 5 minutos
    'MAX_SIZE': 100
}

# Configurações de Segurança
SECURITY_CONFIG = {
    'RATE_LIMIT': {
        'DEFAULT': "200 per day, 50 per hour",
        'SEARCH': "10 per minute",
        'GENERATE_PDF': "5 per minute",
        'DOWNLOAD': "20 per minute"
    },
    'HEADERS': {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
    'WORKERS': int(os.environ.get('WORKERS', 2)),
    'TIMEOUT': int(os.environ.get('TIMEOUT', 120)),
    'MAX_REQUESTS': int(os.environ.get('MAX_REQUESTS', 1000)),
    'MAX_REQUESTS_JITTER': int(os.environ.get('MAX_REQUESTS_JITTER', 100))
}

# Configurações de Teste
TEST_CONFIG = {
    'TEST_CPF': '91446260968',  # CPF de teste conhecido
    'TEST_NOME': 'Fabio Roberto'  # Nome de teste conhecido
}

# Configuração principal
def get_config():
    """Retorna configuração principal do sistema"""
    return {
        'SERVER': SERVER_CONFIG,
        'APP': APP_CONFIG,
        'FILES': FILES_CONFIG,
        'VALIDATION': VALIDATION_CONFIG,
        'PDF': PDF_CONFIG,
        'API': API_CONFIG,
        'LOGGING': LOGGING_CONFIG,
        'CACHE': CACHE_CONFIG,
        'SECURITY': SECURITY_CONFIG,
        'PERFORMANCE': PERFORMANCE_CONFIG,
        'TEST': TEST_CONFIG
    }

def validate_config():
    """Valida se todas as configurações estão corretas"""
    config = get_config()
    
    # Validar arquivos essenciais
    required_files = [
        config['FILES']['EXCEL_FILE'],
        config['FILES']['SCRIPT_FILE'],
        config['FILES']['LOGO_HYPE'],
        config['FILES']['LOGO_BRASAO']
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        raise FileNotFoundError(f"Arquivos essenciais não encontrados: {missing_files}")
    
    # Validar configurações do servidor
    if config['SERVER']['PORT'] < 1 or config['SERVER']['PORT'] > 65535:
        raise ValueError("Porta inválida")
    
    return True 