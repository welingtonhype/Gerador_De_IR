from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import sys
import json
import re
import hashlib
import secrets
from datetime import datetime, timedelta
import logging
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from werkzeug.utils import secure_filename
import traceback

# Adicionar o diretório Scripts ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Scripts'))

# Importar configurações
from config import get_config, validate_config

# Importar o módulo do gerador de IR
from gerador_ir_refatorado import buscar_cliente_por_cpf, calcular_valores_financeiros_manual, gerar_pdf_declaracao

# Configurações
config = get_config()

# Cache simples em memória para otimizar buscas
dados_cache = {}  # Cache para dados completos (cliente + financeiros)

# Configuração de logging com rotação
from logging.handlers import RotatingFileHandler

# Configurar logging
def setup_logging():
    """Configura logging com rotação de arquivos"""
    log_format = config['LOGGING']['FORMAT']
    log_level = getattr(logging, config['LOGGING']['LEVEL'])
    
    # Criar diretório de logs se não existir
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'server.log'),
        maxBytes=config['LOGGING']['MAX_BYTES'],
        backupCount=config['LOGGING']['BACKUP_COUNT']
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Configurar logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# Inicializar Flask
app = Flask(__name__)

# Configurar CORS com origens específicas
CORS(app, origins=config['API']['CORS_ORIGINS'])

# Configurar rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configurar headers de segurança
@app.after_request
def add_security_headers(response):
    """Adiciona headers de segurança"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data:;"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Validação de CPF
def validate_cpf(cpf):
    """Valida CPF com algoritmo oficial"""
    if not cpf:
        return False, "CPF é obrigatório"
    
    # Remover caracteres não numéricos
    cpf_clean = re.sub(r'[^\d]', '', str(cpf))
    
    if len(cpf_clean) != 11:
        return False, "CPF deve ter 11 dígitos"
    
    # Verificar se todos os dígitos são iguais
    if len(set(cpf_clean)) == 1:
        return False, "CPF inválido"
    
    # Validar dígitos verificadores
    try:
        # Primeiro dígito verificador
        soma = sum(int(cpf_clean[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        digito1 = 0 if resto < 2 else 11 - resto
        
        # Segundo dígito verificador
        soma = sum(int(cpf_clean[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        digito2 = 0 if resto < 2 else 11 - resto
        
        # Verificar se os dígitos calculados são iguais aos do CPF
        if int(cpf_clean[9]) == digito1 and int(cpf_clean[10]) == digito2:
            return True, cpf_clean
        else:
            return False, "CPF inválido"
    except (ValueError, IndexError):
        return False, "CPF inválido"

# Sanitização de entrada
def sanitize_input(data):
    """Sanitiza dados de entrada"""
    if isinstance(data, str):
        # Remover caracteres perigosos
        data = re.sub(r'[<>"\']', '', data)
        # Limitar tamanho
        if len(data) > 1000:
            data = data[:1000]
    return data

# Validação de dados JSON
def validate_json_data(data):
    """Valida estrutura dos dados JSON"""
    if not isinstance(data, dict):
        return False, "Dados devem ser um objeto JSON"
    
    if 'cpf' not in data:
        return False, "Campo 'cpf' é obrigatório"
    
    return True, "OK"

# Middleware para logging de requisições
@app.before_request
def log_request():
    """Log de requisições para auditoria"""
    if request.endpoint:
        logger.info(f"Requisição: {request.method} {request.endpoint} - IP: {request.remote_addr}")

# Middleware para validação de conteúdo
@app.before_request
def validate_content_type():
    """Valida Content-Type para endpoints POST"""
    if request.method == 'POST' and request.endpoint in ['buscar_cliente', 'gerar_pdf']:
        if not request.is_json:
            abort(400, description="Content-Type deve ser application/json")

@app.route('/')
def index():
    """Servir a página principal"""
    try:
        return send_file('index.html')
    except FileNotFoundError:
        logger.error("Arquivo index.html não encontrado")
        abort(404, description="Página não encontrada")

@app.route('/styles.css')
def styles():
    """Servir o arquivo CSS"""
    try:
        return send_file('styles.css')
    except FileNotFoundError:
        logger.error("Arquivo styles.css não encontrado")
        abort(404, description="Arquivo CSS não encontrado")

@app.route('/script.js')
def script():
    """Servir o arquivo JavaScript"""
    try:
        return send_file('script.js')
    except FileNotFoundError:
        logger.error("Arquivo script.js não encontrado")
        abort(404, description="Arquivo JavaScript não encontrado")

@app.route('/Imagens/<filename>')
def serve_images(filename):
    """Servir arquivos de imagem"""
    try:
        return send_file(f'Imagens/{filename}')
    except FileNotFoundError:
        logger.error(f"Arquivo de imagem {filename} não encontrado")
        abort(404, description="Imagem não encontrada")

@app.route('/api/buscar-cliente', methods=['POST'])
@limiter.limit("10 per minute")
def buscar_cliente():
    """API para buscar cliente por CPF"""
    try:
        # Validar dados de entrada
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        
        # Validar estrutura JSON
        is_valid, message = validate_json_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
                # Sanitizar e validar CPF
        cpf_raw = sanitize_input(data.get('cpf', ''))
        is_valid_cpf, cpf_clean = validate_cpf(cpf_raw)
        
        if not is_valid_cpf:
            return jsonify({
                'success': False,
                'message': cpf_clean
            }), 400

        logger.info(f"Buscando cliente com CPF: {cpf_clean}")
        
        # Verificar cache primeiro
        if cpf_clean in dados_cache:
            logger.info(f"Dados encontrados no cache para CPF: {cpf_clean}")
            cached_data = dados_cache[cpf_clean]
            
            return jsonify({
                'success': True,
                'data': cached_data['cliente'],
                'tem_dados_financeiros': cached_data['tem_dados_financeiros'],
                'registros_encontrados': cached_data['registros_encontrados'],
                'receita_total': cached_data['receita_total'],
                'despesas_total': cached_data['despesas_total'],
                'fontes_dados': cached_data['fontes_dados'],
                'erro_consistencia': cached_data['erro_consistencia'],
                'pode_gerar_pdf': cached_data['pode_gerar_pdf'],
                'total_valores': cached_data['total_valores'],
                'from_cache': True
            })

        # Buscar dados do cliente
        dados_cliente = buscar_cliente_por_cpf(cpf_clean)
        
        if not dados_cliente:
            logger.warning(f"Cliente não encontrado para CPF: {cpf_clean}")
            return jsonify({
                'success': False,
                'message': 'Cliente não encontrado na base de dados'
            }), 404
        
        # Calcular valores financeiros
        valores_calculados = calcular_valores_financeiros_manual(cpf_clean, dados_cliente)
        
        # Combinar dados
        response_data = {
            **dados_cliente,
            **valores_calculados
        }
        
        # Verificar se há dados financeiros
        tem_dados_financeiros = valores_calculados['registros_encontrados'] > 0
        receita_total = valores_calculados['receita_bruta']
        despesas_total = valores_calculados['despesas_acessorias']
        
        logger.info(f"Cliente encontrado: {dados_cliente['cliente']}")
        logger.info(f"Registros encontrados na UNION: {valores_calculados['registros_encontrados']}")
        logger.info(f"Receita: R$ {receita_total:,.2f}, Despesas: R$ {despesas_total:,.2f}")
        
        # Salvar no cache para futuras consultas
        dados_cache[cpf_clean] = {
            'cliente': response_data,
            'tem_dados_financeiros': tem_dados_financeiros,
            'registros_encontrados': valores_calculados['registros_encontrados'],
            'receita_total': receita_total,
            'despesas_total': despesas_total,
            'fontes_dados': valores_calculados.get('fontes_dados', []),
            'erro_consistencia': valores_calculados.get('erro_consistencia'),
            'pode_gerar_pdf': valores_calculados.get('pode_gerar_pdf', True),
            'total_valores': valores_calculados.get('total_valores', 0),
            'valores_calculados': valores_calculados,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Dados salvos no cache para CPF: {cpf_clean}")

        return jsonify({
            'success': True,
            'data': response_data,
            'tem_dados_financeiros': tem_dados_financeiros,
            'registros_encontrados': valores_calculados['registros_encontrados'],
            'receita_total': receita_total,
            'despesas_total': despesas_total,
            'fontes_dados': valores_calculados.get('fontes_dados', []),
            'erro_consistencia': valores_calculados.get('erro_consistencia'),
            'pode_gerar_pdf': valores_calculados.get('pode_gerar_pdf', True),
            'total_valores': valores_calculados.get('total_valores', 0),
            'from_cache': False
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar cliente: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@app.route('/api/buscar-e-gerar-pdf', methods=['POST'])
@limiter.limit("3 per minute")
def buscar_e_gerar_pdf():
    """API para buscar cliente e gerar PDF em uma única operação"""
    logger.info(f"Recebida requisição para buscar-e-gerar-pdf")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Content-Type: {request.content_type}")
    
    try:
        # Validar dados de entrada
        if not request.is_json:
            logger.warning("Content-Type não é application/json")
            return jsonify({
                'success': False,
                'message': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        
        # Validar estrutura JSON
        is_valid, message = validate_json_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Sanitizar e validar CPF
        cpf_raw = sanitize_input(data.get('cpf', ''))
        is_valid_cpf, cpf_clean = validate_cpf(cpf_raw)
        
        if not is_valid_cpf:
            return jsonify({
                'success': False,
                'message': cpf_clean
            }), 400

        logger.info(f"Buscando cliente e gerando PDF para CPF: {cpf_clean}")
        
        # Buscar dados do cliente (usar cache se disponível)
        logger.info(f"Verificando cache para CPF: {cpf_clean}")
        if cpf_clean in dados_cache:
            logger.info(f"Usando dados do cache: {cpf_clean}")
            cached_data = dados_cache[cpf_clean]
            dados_cliente = cached_data['cliente']
            valores_calculados = cached_data['valores_calculados']
        else:
            # Buscar e calcular tudo
            logger.info(f"Buscando cliente no banco de dados: {cpf_clean}")
            dados_cliente = buscar_cliente_por_cpf(cpf_clean)
            
            if not dados_cliente:
                logger.warning(f"Cliente não encontrado para CPF: {cpf_clean}")
                return jsonify({
                    'success': False,
                    'message': 'Cliente não encontrado na base de dados'
                }), 404
            
            logger.info(f"Cliente encontrado: {dados_cliente['cliente']}")
            logger.info(f"Calculando valores financeiros...")
            valores_calculados = calcular_valores_financeiros_manual(cpf_clean, dados_cliente)
        
        # Gerar PDF
        nome_pdf = gerar_pdf_declaracao(cpf_clean, dados_cliente, valores_calculados)
        
        if not nome_pdf:
            logger.error(f"Erro ao gerar PDF para CPF: {cpf_clean}")
            return jsonify({
                'success': False,
                'message': 'Erro ao gerar PDF'
            }), 500
        
        logger.info(f"PDF gerado com sucesso: {nome_pdf}")
        
        return jsonify({
            'success': True,
            'message': 'Cliente encontrado e PDF gerado com sucesso',
            'filename': nome_pdf,
            'cliente': dados_cliente,
            'valores': {
                'receita_total': valores_calculados.get('receita_bruta', 0),
                'despesas_total': valores_calculados.get('despesas_acessorias', 0),
                'registros_encontrados': valores_calculados.get('registros_encontrados', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao buscar e gerar PDF: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Retornar erro mais específico para debug
        error_details = {
            'success': False,
            'message': 'Erro interno do servidor',
            'error_type': type(e).__name__,
            'error_message': str(e),
            'timestamp': datetime.now().isoformat()
        }
        
        # Log adicional para debug
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Error args: {e.args if hasattr(e, 'args') else 'N/A'}")
        
        return jsonify(error_details), 500

@app.route('/api/gerar-pdf', methods=['POST'])
@limiter.limit("5 per minute")
def gerar_pdf():
    """API para gerar PDF da declaração de IR"""
    try:
        # Validar dados de entrada
        if not request.is_json:
            return jsonify({
                'success': False,
                'message': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        
        # Validar estrutura JSON
        is_valid, message = validate_json_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Sanitizar e validar CPF
        cpf_raw = sanitize_input(data.get('cpf', ''))
        is_valid_cpf, cpf_clean = validate_cpf(cpf_raw)
        
        if not is_valid_cpf:
            return jsonify({
                'success': False,
                'message': cpf_clean
            }), 400
        
        logger.info(f"Gerando PDF para CPF: {cpf_clean}")
        
        # Tentar usar dados do cache primeiro
        if cpf_clean in dados_cache:
            logger.info(f"Usando dados do cache para gerar PDF: {cpf_clean}")
            cached_data = dados_cache[cpf_clean]
            dados_cliente = cached_data['cliente']
            valores_calculados = cached_data['valores_calculados']
        else:
            # Buscar dados do cliente se não estiver no cache
            dados_cliente = buscar_cliente_por_cpf(cpf_clean)
            
            if not dados_cliente:
                logger.warning(f"Cliente não encontrado para CPF: {cpf_clean}")
                return jsonify({
                    'success': False,
                    'message': 'Cliente não encontrado na base de dados'
                }), 404
            
            # Calcular valores financeiros
            valores_calculados = calcular_valores_financeiros_manual(cpf_clean, dados_cliente)
        
        # Gerar PDF
        nome_pdf = gerar_pdf_declaracao(cpf_clean, dados_cliente, valores_calculados)
        
        if not nome_pdf:
            logger.error(f"Erro ao gerar PDF para CPF: {cpf_clean}")
            return jsonify({
                'success': False,
                'message': 'Erro ao gerar PDF'
            }), 500
        
        logger.info(f"PDF gerado com sucesso: {nome_pdf}")
        
        return jsonify({
            'success': True,
            'message': 'PDF gerado com sucesso',
            'filename': nome_pdf
        })
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@app.route('/api/download-pdf/<filename>')
@limiter.limit("20 per minute")
def download_pdf(filename):
    """API para download do PDF gerado"""
    try:
        # Validar nome do arquivo
        if not filename or not re.match(r'^Declaracao_IR_\d{11}_\d{8}_\d{6}\.pdf$', filename):
            logger.warning(f"Tentativa de download com nome de arquivo inválido: {filename}")
            return jsonify({
                'success': False,
                'message': 'Nome de arquivo inválido'
            }), 400
        
        file_path = os.path.join(os.path.dirname(__file__), filename)
        
        # Verificar se o arquivo existe e está no diretório correto
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            logger.warning(f"Tentativa de download de arquivo inexistente: {filename}")
            return jsonify({
                'success': False,
                'message': 'Arquivo não encontrado'
            }), 404
        
        # Verificar se o arquivo é um PDF válido
        if not filename.lower().endswith('.pdf'):
            logger.warning(f"Tentativa de download de arquivo não-PDF: {filename}")
            return jsonify({
                'success': False,
                'message': 'Tipo de arquivo não permitido'
            }), 400
        
        logger.info(f"Download do PDF: {filename}")
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Erro ao fazer download do PDF: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Erro ao fazer download do arquivo'
        }), 500

@app.route('/api/health')
def health_check():
    """Health check da API"""
    try:
        # Verificar se arquivos essenciais existem
        files_to_check = [
            config['FILES']['EXCEL_FILE'],
            config['FILES']['SCRIPT_FILE']
        ]
        
        missing_files = []
        for file_path in files_to_check:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        status = 'healthy' if not missing_files else 'degraded'
        
        return jsonify({
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'version': config['APP']['VERSION'],
            'missing_files': missing_files if missing_files else None,
            'environment': 'production' if not config['SERVER']['DEBUG'] else 'development'
        })
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'version': config['APP']['VERSION'],
            'error': str(e)
        }), 500

@app.route('/api/test')
def test_endpoint():
    """Endpoint de teste simples"""
    return jsonify({
        'message': 'API funcionando corretamente',
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    })

@app.route('/api/test-pdf', methods=['POST'])
def test_pdf_generation():
    """Teste específico para geração de PDF"""
    try:
        logger.info("Teste de geração de PDF iniciado")
        
        # Verificar se os módulos estão disponíveis
        try:
            from Scripts.gerador_ir_refatorado import buscar_cliente_por_cpf
            logger.info("✅ Módulo gerador_ir_refatorado importado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao importar módulo: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erro ao importar módulo: {str(e)}'
            }), 500
        
        # Testar busca de cliente
        try:
            dados_cliente = buscar_cliente_por_cpf('43445950091')
            if dados_cliente:
                logger.info(f"✅ Cliente encontrado: {dados_cliente['cliente']}")
                return jsonify({
                    'success': True,
                    'message': 'Teste de busca de cliente passou',
                    'cliente': dados_cliente['cliente']
                })
            else:
                logger.warning("⚠️ Cliente não encontrado no teste")
                return jsonify({
                    'success': False,
                    'message': 'Cliente não encontrado no teste'
                }), 404
        except Exception as e:
            logger.error(f"❌ Erro na busca de cliente: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erro na busca de cliente: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Erro geral no teste: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro geral: {str(e)}'
        }), 500

# Handlers de erro
@app.errorhandler(400)
def bad_request(error):
    """Handler para requisições malformadas"""
    logger.warning(f"Bad Request: {error}")
    return jsonify({
        'success': False,
        'message': 'Requisição inválida'
    }), 400

@app.errorhandler(404)
def not_found(error):
    """Handler para rotas não encontradas"""
    logger.warning(f"Not Found: {request.url}")
    return jsonify({
        'success': False,
        'message': 'Endpoint não encontrado'
    }), 404

@app.errorhandler(429)
def too_many_requests(error):
    """Handler para rate limiting"""
    logger.warning(f"Rate limit excedido: {request.remote_addr}")
    return jsonify({
        'success': False,
        'message': 'Muitas requisições. Tente novamente em alguns minutos.'
    }), 429

@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos"""
    logger.error(f"Erro interno: {str(error)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return jsonify({
        'success': False,
        'message': 'Erro interno do servidor'
    }), 500

@app.errorhandler(Exception)
def handle_exception(error):
    """Handler genérico para exceções não tratadas"""
    logger.error(f"Exceção não tratada: {str(error)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return jsonify({
        'success': False,
        'message': 'Erro interno do servidor'
    }), 500

if __name__ == '__main__':
    try:
        # Validar configurações
        print("🔧 Validando configurações...")
        validate_config()
        print("✅ Configurações validadas com sucesso")
        
        # Configurações do servidor
        host = config['SERVER']['HOST']
        port = config['SERVER']['PORT']
        debug = config['SERVER']['DEBUG']
        
        print(f"🚀 Iniciando servidor em {host}:{port}")
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=config['SERVER']['THREADED']
        )
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {str(e)}")
        sys.exit(1) 