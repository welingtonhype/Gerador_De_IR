"""
Tasks assíncronas para processamento
"""

import redis
import json
import logging
from celery_app import celery_app
from config import get_config
import sys
import os

# Adicionar Scripts ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Scripts'))

from gerador_ir_refatorado import buscar_cliente_por_cpf, calcular_valores_financeiros_manual, gerar_pdf_declaracao

config = get_config()

# Configurar Redis
redis_client = redis.Redis(
    host=config['REDIS']['HOST'],
    port=config['REDIS']['PORT'],
    password=config['REDIS']['PASSWORD'],
    db=config['REDIS']['DB'],
    decode_responses=True
)

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def processar_cliente_async(self, cpf):
    """
    Task assíncrona para processar cliente e gerar PDF
    """
    try:
        logger.info(f"Iniciando processamento assíncrono para CPF: {cpf}")
        
        # Atualizar status
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Buscando cliente...', 'progress': 20}
        )
        
        # Buscar cliente
        dados_cliente = buscar_cliente_por_cpf(cpf)
        if not dados_cliente:
            return {
                'success': False,
                'message': 'Cliente não encontrado',
                'status': 'FAILURE'
            }
        
        # Atualizar status
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Calculando valores...', 'progress': 50}
        )
        
        # Calcular valores financeiros
        valores_calculados = calcular_valores_financeiros_manual(cpf, dados_cliente)
        
        # Atualizar status
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Gerando PDF...', 'progress': 80}
        )
        
        # Gerar PDF
        nome_pdf = gerar_pdf_declaracao(cpf, dados_cliente, valores_calculados)
        
        if not nome_pdf:
            return {
                'success': False,
                'message': 'Erro ao gerar PDF',
                'status': 'FAILURE'
            }
        
        # Salvar resultado no Redis
        resultado = {
            'success': True,
            'message': 'Processamento concluído',
            'filename': nome_pdf,
            'cliente': dados_cliente,
            'valores': valores_calculados,
            'status': 'SUCCESS'
        }
        
        # Cache por 1 hora
        redis_client.setex(
            f"resultado:{cpf}",
            config['REDIS']['TTL'],
            json.dumps(resultado, default=str)
        )
        
        logger.info(f"Processamento concluído para CPF: {cpf}")
        
        return resultado
        
    except Exception as e:
        logger.error(f"Erro no processamento assíncrono: {str(e)}")
        return {
            'success': False,
            'message': f'Erro interno: {str(e)}',
            'status': 'FAILURE'
        }

@celery_app.task
def limpar_cache_antigo():
    """
    Task para limpar cache antigo
    """
    try:
        # Limpar resultados antigos (mais de 1 hora)
        keys = redis_client.keys("resultado:*")
        for key in keys:
            ttl = redis_client.ttl(key)
            if ttl < 0:  # Sem TTL ou expirado
                redis_client.delete(key)
        
        logger.info("Cache antigo limpo")
        return {'success': True, 'message': 'Cache limpo'}
        
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        return {'success': False, 'message': str(e)}

@celery_app.task
def verificar_arquivo_excel():
    """
    Task para verificar se arquivo Excel está acessível
    """
    try:
        excel_file = config['FILES']['EXCEL_FILE']
        if os.path.exists(excel_file):
            size = os.path.getsize(excel_file)
            return {
                'success': True,
                'message': 'Arquivo Excel encontrado',
                'size': size
            }
        else:
            return {
                'success': False,
                'message': 'Arquivo Excel não encontrado'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Erro ao verificar arquivo: {str(e)}'
        } 