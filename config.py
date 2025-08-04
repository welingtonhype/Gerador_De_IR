"""
Configurações do Sistema Gerador de IR
Centraliza todas as configurações do sistema
"""

import os

# Configurações do Servidor
SERVER_CONFIG = {
    'HOST': os.environ.get('HOST', '0.0.0.0'),
    'PORT': int(os.environ.get('PORT', 10000)),
    'DEBUG': os.environ.get('DEBUG', 'False').lower() == 'true',
    'THREADED': True
}

# Configurações Redis
REDIS_CONFIG = {
    'HOST': os.environ.get('REDIS_HOST', 'localhost'),
    'PORT': int(os.environ.get('REDIS_PORT', 6379)),
    'PASSWORD': os.environ.get('REDIS_PASSWORD', None),
    'DB': int(os.environ.get('REDIS_DB', 0)),
    'TTL': 3600,  # 1 hora
    'ENABLED': True
}

# Configurações Celery
CELERY_CONFIG = {
    'BROKER_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    'RESULT_BACKEND': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
    'TASK_SERIALIZER': 'json',
    'ACCEPT_CONTENT': ['json'],
    'RESULT_SERIALIZER': 'json',
    'TIMEZONE': 'America/Sao_Paulo',
    'ENABLE_UTC': True,
    'TASK_TRACK_STARTED': True,
    'TASK_TIME_LIMIT': 300,  # 5 minutos
    'WORKER_MAX_TASKS_PER_CHILD': 50
}

# Configurações da Aplicação
APP_CONFIG = {
    'NAME': 'Gerador de IR - Hype Empreendimentos',
    'VERSION': '2.0.0',
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
    'LOGO_BRASAO': 'Imagens/Imagem1.png'
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
        'DOWNLOAD_PDF': '/api/download-pdf/<filename>',
        'TASK_STATUS': '/api/task-status/<task_id>'
    },
    'TIMEOUTS': {
        'SEARCH': 10,
        'GENERATE_PDF': 30,
        'DOWNLOAD': 60,
        'ASYNC_TASK': 300
    },
    'CORS_ORIGINS': [
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:10000',
        'http://127.0.0.1:10000',
        'https://*.railway.app',
        'https://*.onrender.com',
        '*'
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
    'TTL': 3600,  # 1 hora
    'MAX_SIZE': 100,
    'REDIS_ENABLED': True
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
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data:;",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
    'WORKERS': int(os.environ.get('WORKERS', 2)),
    'TIMEOUT': int(os.environ.get('TIMEOUT', 300)),
    'MAX_REQUESTS': int(os.environ.get('MAX_REQUESTS', 100)),
    'MAX_REQUESTS_JITTER': int(os.environ.get('MAX_REQUESTS_JITTER', 10)),
    'EXCEL_CHUNK_SIZE': 100,  # Processar Excel em chunks
    'ASYNC_ENABLED': True
}

# Configuração principal
def get_config():
    """Retorna configuração principal do sistema"""
    return {
        'SERVER': SERVER_CONFIG,
        'REDIS': REDIS_CONFIG,
        'CELERY': CELERY_CONFIG,
        'APP': APP_CONFIG,
        'FILES': FILES_CONFIG,
        'VALIDATION': VALIDATION_CONFIG,
        'PDF': PDF_CONFIG,
        'API': API_CONFIG,
        'LOGGING': LOGGING_CONFIG,
        'CACHE': CACHE_CONFIG,
        'SECURITY': SECURITY_CONFIG,
        'PERFORMANCE': PERFORMANCE_CONFIG
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