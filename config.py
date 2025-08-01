"""
Configurações do Sistema Gerador de IR
Centraliza todas as configurações do sistema
"""

import os
from pathlib import Path

# Configurações do Servidor
SERVER_CONFIG = {
    'HOST': os.environ.get('HOST', '0.0.0.0'),
    'PORT': int(os.environ.get('PORT', 5000)),
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
        'http://127.0.0.1:3000'
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

# Configurações de Segurança
SECURITY_CONFIG = {
    'MAX_FILE_SIZE': 50 * 1024 * 1024,  # 50MB
    'ALLOWED_EXTENSIONS': ['.xlsx', '.xls'],
    'RATE_LIMIT': {
        'REQUESTS_PER_MINUTE': 60,
        'REQUESTS_PER_HOUR': 1000
    }
}

# Configurações de Interface
UI_CONFIG = {
    'THEME': {
        'PRIMARY_COLOR': '#018672',
        'SECONDARY_COLOR': '#00a896',
        'SUCCESS_COLOR': '#28a745',
        'ERROR_COLOR': '#dc3545',
        'WARNING_COLOR': '#ffc107',
        'INFO_COLOR': '#17a2b8',
        'BACKGROUND_GRADIENT': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    },
    'ANIMATIONS': {
        'ENABLED': True,
        'DURATION': 300,
        'EASING': 'ease'
    },
    'RESPONSIVE': {
        'MOBILE_BREAKPOINT': 768,
        'TABLET_BREAKPOINT': 1024
    }
}

# Configurações de Mensagens
MESSAGES = {
    'WELCOME': 'Bem-vindo ao Gerador de IR',
    'WELCOME_SUBTITLE': 'Digite o CPF do cliente para começar',
    'CLIENT_FOUND': 'Cliente Encontrado',
    'CLIENT_FOUND_SUBTITLE': 'Dados carregados com sucesso',
    'CLIENT_NOT_FOUND': 'Cliente não encontrado',
    'CLIENT_NOT_FOUND_SUBTITLE': 'CPF não encontrado na base de dados',
    'PDF_GENERATED': 'PDF Gerado',
    'PDF_GENERATED_SUBTITLE': 'Declaração de IR gerada com sucesso',
    'ERROR_VALIDATION': 'Erro de Validação',
    'ERROR_SYSTEM': 'Erro de Sistema',
    'ERROR_SYSTEM_SUBTITLE': 'Erro ao processar a solicitação',
    'ERROR_PDF': 'Erro',
    'ERROR_PDF_SUBTITLE': 'Erro ao gerar o PDF'
}

# Configurações de Teste
TEST_CONFIG = {
    'TEST_CPF': '30204690900',
    'TIMEOUT': 30,
    'RETRY_ATTEMPTS': 3,
    'RETRY_DELAY': 1
}

def get_config():
    """Retorna todas as configurações"""
    return {
        'SERVER': SERVER_CONFIG,
        'APP': APP_CONFIG,
        'FILES': FILES_CONFIG,
        'VALIDATION': VALIDATION_CONFIG,
        'PDF': PDF_CONFIG,
        'API': API_CONFIG,
        'LOGGING': LOGGING_CONFIG,
        'SECURITY': SECURITY_CONFIG,
        'UI': UI_CONFIG,
        'MESSAGES': MESSAGES,
        'TEST': TEST_CONFIG
    }

def validate_config():
    """Valida se todas as configurações estão corretas"""
    errors = []
    
    # Verificar arquivos obrigatórios (apenas os essenciais)
    essential_files = {
        'EXCEL_FILE': 'Arquivo Excel da base de dados',
        'SCRIPT_FILE': 'Script principal do gerador'
    }
    
    for file_key, description in essential_files.items():
        file_path = FILES_CONFIG[file_key]
        if not os.path.exists(file_path):
            errors.append(f"{description} não encontrado: {file_path}")
    
    # Verificar configurações do servidor
    if SERVER_CONFIG['PORT'] < 1 or SERVER_CONFIG['PORT'] > 65535:
        errors.append("Porta do servidor inválida")
    
    # Verificar configurações de API
    for endpoint in API_CONFIG['ENDPOINTS'].values():
        if not endpoint.startswith('/'):
            errors.append(f"Endpoint inválido: {endpoint}")
    
    return errors

if __name__ == "__main__":
    # Testar configurações
    print("🔧 Validando configurações...")
    errors = validate_config()
    
    if errors:
        print("❌ Erros encontrados:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ Todas as configurações estão corretas")
    
    # Mostrar configurações
    config = get_config()
    print(f"\n📋 Configurações do Sistema:")
    print(f"   Nome: {config['APP']['NAME']}")
    print(f"   Versão: {config['APP']['VERSION']}")
    print(f"   Servidor: {config['SERVER']['HOST']}:{config['SERVER']['PORT']}")
    print(f"   Debug: {config['SERVER']['DEBUG']}") 