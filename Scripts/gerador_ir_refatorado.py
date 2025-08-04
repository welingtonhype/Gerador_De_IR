"""
Gerador de IR Refatorado - Versão 3.0
"""

import openpyxl
from openpyxl import load_workbook
import os
import re
import logging
from datetime import datetime
from pathlib import Path
import sys
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import get_config

config = get_config()

def setup_logging():
    """Configura logging"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'gerador_ir_refatorado.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class ValidadorCPF:
    """Classe para validação de CPF"""
    
    @staticmethod
    def limpar_cpf(cpf):
        """Remove caracteres não numéricos do CPF"""
        if not cpf:
            return ""
        return re.sub(r'[^\d]', '', str(cpf))
    
    @staticmethod
    def validar_cpf(cpf):
        """Valida CPF com algoritmo oficial"""
        cpf_limpo = ValidadorCPF.limpar_cpf(cpf)
        
        if len(cpf_limpo) != 11:
            return False, "CPF deve ter 11 dígitos"
        
        if len(set(cpf_limpo)) == 1:
            return False, "CPF inválido"
        
        try:
            soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto
            
            soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto
            
            if int(cpf_limpo[9]) == digito1 and int(cpf_limpo[10]) == digito2:
                return True, cpf_limpo
            else:
                return False, "CPF inválido"
        except (ValueError, IndexError):
            return False, "CPF inválido"

class BuscadorCliente:
    """Classe para busca de dados do cliente"""
    
    def __init__(self, arquivo_excel):
        self.arquivo_excel = arquivo_excel
    
    def _converter_valor(self, valor):
        """Converte valor para float, tratando casos especiais"""
        if valor is None:
            return 0.0
        if isinstance(valor, (int, float)):
            return float(valor)
        if isinstance(valor, str):
            valor_str = valor.strip().upper()
            if valor_str in ['VERIFICAR', 'N/A', 'N/A.', '']:
                return 0.0
            try:
                return float(valor_str)
            except ValueError:
                return 0.0
        return 0.0
    
    def _extrair_dados_cliente(self, ws, row):
        """Extrai dados do cliente da planilha"""
        return {
            'cpf': str(ws.cell(row=row, column=4).value or ''),
            'cliente': str(ws.cell(row=row, column=3).value or ''),
            'empreendimento': str(ws.cell(row=row, column=5).value or ''),
            'unidade': str(ws.cell(row=row, column=7).value or ''),
            'sigla': str(ws.cell(row=row, column=6).value or ''),
            'endereco': str(ws.cell(row=row, column=10).value or ''),
            'numero': str(ws.cell(row=row, column=11).value or ''),
            'bairro': str(ws.cell(row=row, column=12).value or ''),
            'estado': str(ws.cell(row=row, column=13).value or ''),
            'cidade': str(ws.cell(row=row, column=14).value or ''),
            'codigo': str(ws.cell(row=row, column=15).value or ''),
            'nome_empresa': str(ws.cell(row=row, column=9).value or 'HYPE EMPREENDIMENTOS'),
            'cnpj_empresa': str(ws.cell(row=row, column=8).value or '41.081.989/0001-92'),
            'valor_venda': self._converter_valor(ws.cell(row=row, column=16).value),
            'saldo_union': self._converter_valor(ws.cell(row=row, column=17).value),
            'saldo_erp': self._converter_valor(ws.cell(row=row, column=18).value),
            'diferenca': self._converter_valor(ws.cell(row=row, column=19).value)
        }
    
    def buscar_por_cpf(self, cpf_busca):
        """Busca CPF na Base de Clientes e retorna dados do cliente - VERSÃO MELHORADA"""
        is_valid, cpf_clean = ValidadorCPF.validar_cpf(cpf_busca)
        if not is_valid:
            logger.error(f"CPF inválido: {cpf_busca}")
            return None
        
        try:
            wb = load_workbook(self.arquivo_excel, data_only=True)
            
            if 'Base de Clientes' not in wb.sheetnames:
                logger.error("Planilha 'Base de Clientes' não encontrada")
                wb.close()
                return None
            
            ws = wb['Base de Clientes']
            
            # BUSCA MELHORADA: múltiplas estratégias
            for row in range(3, ws.max_row + 1):
                cpf_cell = ws.cell(row=row, column=4).value
                nome_cliente = ws.cell(row=row, column=3).value
                
                # Estratégia 1: CPF exato
                if cpf_cell:
                    cpf_cell_limpo = ValidadorCPF.limpar_cpf(cpf_cell)
                    if cpf_cell_limpo == cpf_clean:
                        dados = self._extrair_dados_cliente(ws, row)
                        wb.close()
                        logger.info(f"Cliente encontrado por CPF exato: {dados['cliente']}")
                        return dados
                
                # Estratégia 2: CPF parcial (caso tenha formatação diferente)
                elif cpf_cell and cpf_clean in str(cpf_cell).replace('.', '').replace('-', ''):
                    dados = self._extrair_dados_cliente(ws, row)
                    dados['cpf'] = cpf_clean  # Normalizar CPF
                    wb.close()
                    logger.info(f"Cliente encontrado por CPF parcial: {dados['cliente']}")
                    return dados
                
                # Estratégia 3: CPF no nome (caso esteja incorreto na planilha)
                elif nome_cliente and cpf_clean in str(nome_cliente):
                    dados = self._extrair_dados_cliente(ws, row)
                    dados['cpf'] = cpf_clean
                    wb.close()
                    logger.info(f"Cliente encontrado por CPF no nome: {dados['cliente']}")
                    return dados
            
            wb.close()
            logger.warning(f"CPF não encontrado: {cpf_clean}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar cliente: {str(e)}")
            return None
    
    def buscar_por_nome(self, nome_cliente):
        """Busca cliente por nome na Base de Clientes"""
        try:
            wb = load_workbook(self.arquivo_excel, data_only=True)
            
            if 'Base de Clientes' not in wb.sheetnames:
                logger.error("Planilha 'Base de Clientes' não encontrada")
                wb.close()
                return None
            
            ws = wb['Base de Clientes']
            
            for row in range(3, ws.max_row + 1):
                nome_cell = ws.cell(row=row, column=3).value
                
                if nome_cell and nome_cliente.lower() in str(nome_cell).lower():
                    dados = self._extrair_dados_cliente(ws, row)
                    wb.close()
                    logger.info(f"Cliente encontrado por nome: {dados['cliente']}")
                    return dados
            
            wb.close()
            logger.warning(f"Nome não encontrado: {nome_cliente}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por nome: {str(e)}")
            return None

class CalculadorFinanceiro:
    """Classe para cálculos financeiros"""
    
    def __init__(self, arquivo_excel):
        self.arquivo_excel = arquivo_excel
        self.buscador = BuscadorCliente(arquivo_excel)
    
    def _normalizar_nome(self, nome):
        """Normaliza nome para comparação"""
        import unicodedata
        if not nome:
            return ""
        # Remover acentos
        nome_normalizado = unicodedata.normalize('NFD', str(nome))
        nome_sem_acentos = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')
        return nome_sem_acentos.upper().strip()
    
    def _nomes_sao_similares(self, nome1, nome2, threshold=0.8):
        """Verifica se dois nomes são similares o suficiente"""
        nome1_norm = self._normalizar_nome(nome1)
        nome2_norm = self._normalizar_nome(nome2)
        
        # Se são exatamente iguais
        if nome1_norm == nome2_norm:
            return True
        
        # Dividir em palavras
        palavras1 = [p for p in nome1_norm.split() if len(p) > 2]
        palavras2 = [p for p in nome2_norm.split() if len(p) > 2]
        
        if not palavras1 or not palavras2:
            return False
        
        # Contar palavras em comum
        palavras_comuns = 0
        for palavra1 in palavras1:
            for palavra2 in palavras2:
                if palavra1 == palavra2:
                    palavras_comuns += 1
                    break
        
        # Calcular similaridade
        max_palavras = max(len(palavras1), len(palavras2))
        similaridade = palavras_comuns / max_palavras
        
        return similaridade >= threshold

    def _calcular_valor_por_tipo(self, cpf_cliente, tipo_busca):
        """
        Calcula valor baseado no tipo de busca - VERSÃO CORRIGIDA
        
        Receita Bruta: =SOMASES('UNION - 2024'!G:G;'UNION - 2024'!P:P;"RECEITA BRUTA";'UNION - 2024'!E:E;NOME_CLIENTE)
        Despesas: =SOMASES('UNION - 2024'!G:G,'UNION - 2024'!P:P,"ATIVO CIRCULANTE",'UNION - 2024'!E:E,NOME_CLIENTE)
        """
        try:
            wb = load_workbook(self.arquivo_excel, data_only=True)
            
            if 'UNION - 2024' not in wb.sheetnames:
                logger.error("Planilha 'UNION - 2024' não encontrada")
                wb.close()
                return 0
            
            ws = wb['UNION - 2024']
            total = 0
            registros_encontrados = 0
            
            dados_cliente = self.buscador.buscar_por_cpf(cpf_cliente)
            if not dados_cliente:
                wb.close()
                return 0
            
            nome_cliente = dados_cliente['cliente']
            logger.info(f"Calculando {tipo_busca} para cliente: {nome_cliente}")
            
            # BUSCA MELHORADA: usar similaridade de nomes
            for row in range(2, ws.max_row + 1):
                cliente_col_e = ws.cell(row=row, column=5).value  # Coluna E - Nome do cliente
                tipo_col_p = ws.cell(row=row, column=16).value    # Coluna P - Tipo (RECEITA BRUTA, ATIVO CIRCULANTE)
                valor_col_g = ws.cell(row=row, column=7).value    # Coluna G - Valor a somar
                
                # Verificar se o tipo está correto
                if not (tipo_col_p and tipo_busca in str(tipo_col_p).upper()):
                    continue
                
                # Verificar se há valor válido
                if not (valor_col_g and isinstance(valor_col_g, (int, float))):
                    continue
                
                # CORREÇÃO: verificar apenas por CPF (mais seguro)
                cpf_col_f = ws.cell(row=row, column=6).value  # Coluna F - CPF
                if cpf_col_f and str(cpf_cliente).replace('.', '').replace('-', '') in str(cpf_col_f).replace('.', '').replace('-', ''):
                    nome_planilha = str(cliente_col_e).strip() if cliente_col_e else "N/A"
                    total += float(valor_col_g)
                    registros_encontrados += 1
                    logger.debug(f"{tipo_busca} encontrado por CPF: R$ {valor_col_g:,.2f} para {nome_planilha} (CPF: {cpf_col_f})")
            
            wb.close()
            logger.info(f"{tipo_busca} total: R$ {total:,.2f} ({registros_encontrados} registros)")
            return total
            
        except Exception as e:
            logger.error(f"Erro ao calcular {tipo_busca}: {str(e)}")
            return 0
    
    def calcular_receita_bruta(self, cpf_cliente):
        """Calcula receita bruta"""
        return self._calcular_valor_por_tipo(cpf_cliente, "RECEITA BRUTA")
    
    def calcular_despesas_acessorias(self, cpf_cliente):
        """Calcula despesas acessórias"""
        return self._calcular_valor_por_tipo(cpf_cliente, "ATIVO CIRCULANTE")
    
    def calcular_saldo_union(self, cpf_cliente):
        """Calcula saldo Union"""
        return self._calcular_valor_por_tipo(cpf_cliente, "RECEITA BRUTA")
    
    def verificar_saldo_paggo_dunning(self, cpf_cliente):
        """Verifica saldo Paggo e Dunning - Implementa fórmula Excel"""
        try:
            wb = load_workbook(self.arquivo_excel, data_only=True)
            
            if 'UNIFICADA ERP (paggo e dunning)' not in wb.sheetnames:
                logger.error("Planilha 'UNIFICADA ERP (paggo e dunning)' não encontrada")
                wb.close()
                return 0
            
            # Buscar dados do cliente primeiro
            dados_cliente = self.buscador.buscar_por_cpf(cpf_cliente)
            if not dados_cliente:
                wb.close()
                return 0
            
            ws = wb['UNIFICADA ERP (paggo e dunning)']
            saldo_total = 0
            
            logger.info(f"Verificando saldo Paggo/Dunning para cliente: {dados_cliente['cliente']}")
            
            # Implementa: =SOMASES('UNIFICADA ERP (paggo e dunning)'!Q:Q;'UNIFICADA ERP (paggo e dunning)'!F:F;CPF;'UNIFICADA ERP (paggo e dunning)'!B:B;EMPREENDIMENTO)
            for row in range(2, ws.max_row + 1):
                cpf_col_f = ws.cell(row=row, column=6).value  # Coluna F
                empreend_col_b = ws.cell(row=row, column=2).value  # Coluna B
                valor_col_q = ws.cell(row=row, column=17).value  # Coluna Q
                
                if (cpf_col_f and str(dados_cliente['cpf']) in str(cpf_col_f) and
                    empreend_col_b and dados_cliente['empreendimento'] in str(empreend_col_b) and
                    valor_col_q and isinstance(valor_col_q, (int, float))):
                    saldo_total += float(valor_col_q)
                    logger.debug(f"Saldo Paggo/Dunning encontrado: R$ {valor_col_q:,.2f} - CPF: {cpf_col_f}, Empreend: {empreend_col_b}")
            
            wb.close()
            logger.info(f"Saldo Paggo/Dunning total: R$ {saldo_total:,.2f}")
            return saldo_total
            
        except Exception as e:
            logger.error(f"Erro ao verificar saldo Paggo/Dunning: {str(e)}")
            return 0

class ValidadorConsistencia:
    """Classe para validação de consistência dos dados"""
    
    @staticmethod
    def validar_saldos(saldo_union, saldo_paggo_dunning):
        """Valida se saldo Union é diferente de saldo Paggo e Dunning"""
        if abs(saldo_union - saldo_paggo_dunning) > 0.01:
            diferenca = saldo_union - saldo_paggo_dunning
            logger.warning(f"Inconsistência detectada: Saldo Union ({saldo_union:,.2f}) != Saldo Paggo/Dunning ({saldo_paggo_dunning:,.2f})")
            logger.warning(f"Diferença: R$ {diferenca:,.2f}")
            return False, diferenca
        else:
            logger.info("Saldos consistentes")
            return True, 0

class GeradorPDF:
    """Classe para geração de PDF"""
    
    def __init__(self):
        self.config = config
    
    def _criar_estilos(self):
        """Cria estilos para o PDF"""
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=5,
            alignment=TA_CENTER,
            textColor=colors.black,
            leading=16
        )
        
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=10,
            spaceAfter=8,
            spaceBefore=15,
            textColor=colors.black,
            leading=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            spaceAfter=6,
            textColor=colors.black,
            leading=12
        )
        
        return title_style, section_style, normal_style
    
    def _criar_cabecalho(self):
        """Cria cabeçalho com logos da Hype e Ministério da Fazenda"""
        try:
            # Verificar se as imagens existem
            logo_hype_path = "Imagens/Imagem2.png"
            logo_ministerio_path = "Imagens/Imagem1.png"
            
            if not os.path.exists(logo_hype_path):
                logger.warning(f"Logo da Hype não encontrado: {logo_hype_path}")
                logo_hype = None
            else:
                logo_hype = Image(logo_hype_path, width=1.2*inch, height=0.8*inch)
            
            if not os.path.exists(logo_ministerio_path):
                logger.warning(f"Logo do Ministério não encontrado: {logo_ministerio_path}")
                logo_ministerio = None
            else:
                # Brasão menor conforme solicitado
                logo_ministerio = Image(logo_ministerio_path, width=0.5*inch, height=0.5*inch)
            
            # Criar texto central
            texto_central = Paragraph(
                """<para align=center>
                <b>ANO-CALENDÁRIO DE 2024<br/>
                IMPOSTO DE RENDA - PESSOA FÍSICA</b>
                </para>""",
                ParagraphStyle(
                    'HeaderCenter',
                    fontName='Helvetica-Bold',
                    fontSize=11,
                    alignment=TA_CENTER,
                    textColor=colors.black,
                    leading=13
                )
            )
            
            # Criar seção direita com texto e brasão lado a lado
            if logo_ministerio:
                # Criar tabela interna para texto + brasão lado a lado
                texto_ministerio = Paragraph(
                    """<para align=center>
                    <b>MINISTÉRIO DA<br/>
                    FAZENDA<br/>
                    SECRETARIA<br/>
                    DA<br/>
                    RECEITA FEDERAL</b>
                    </para>""",
                    ParagraphStyle(
                        'HeaderRight',
                        fontName='Helvetica-Bold',
                        fontSize=8,
                        alignment=TA_CENTER,
                        textColor=colors.black,
                        leading=10
                    )
                )
                
                # Tabela interna para texto + brasão
                ministerio_data = [[texto_ministerio, logo_ministerio]]
                ministerio_table = Table(ministerio_data, colWidths=[1.3*inch, 0.6*inch])
                ministerio_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Texto
                    ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # Brasão
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('TOPPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                ]))
                
                # Dados da tabela principal (3 colunas: Hype, Centro, Ministério+Brasão)
                if logo_hype:
                    header_data = [[logo_hype, texto_central, ministerio_table]]
                    col_widths = [1.2*inch, 3.9*inch, 1.9*inch]
                else:
                    header_data = [[texto_central, ministerio_table]]
                    col_widths = [5.1*inch, 1.9*inch]
            else:
                # Sem brasão, apenas texto
                texto_direito = Paragraph(
                    """<para align=center>
                    <b>MINISTÉRIO DA<br/>
                    FAZENDA<br/>
                    SECRETARIA<br/>
                    DA<br/>
                    RECEITA FEDERAL</b>
                    </para>""",
                    ParagraphStyle(
                        'HeaderRight',
                        fontName='Helvetica-Bold',
                        fontSize=8,
                        alignment=TA_CENTER,
                        textColor=colors.black,
                        leading=10
                    )
                )
                
                if logo_hype:
                    header_data = [[logo_hype, texto_central, texto_direito]]
                    col_widths = [1.2*inch, 4.5*inch, 1.3*inch]
                else:
                    header_data = [[texto_central, texto_direito]]
                    col_widths = [5.7*inch, 1.3*inch]
            
            # Criar tabela principal do cabeçalho
            header_table = Table(header_data, colWidths=col_widths)
            header_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            return header_table
            
        except Exception as e:
            logger.error(f"Erro ao criar cabeçalho: {str(e)}")
            # Retornar cabeçalho simples em caso de erro
            return Paragraph(
                "<para align=center><b>ANO-CALENDÁRIO DE 2024<br/>IMPOSTO DE RENDA - PESSOA FÍSICA</b></para>",
                ParagraphStyle(
                    'SimpleHeader',
                    fontName='Helvetica-Bold',
                    fontSize=14,
                    alignment=TA_CENTER,
                    textColor=colors.black,
                    leading=16
                )
            )
    
    def _criar_tabela_pj(self, dados_cliente):
        """Cria tabela da pessoa jurídica"""
        nome_empresa = dados_cliente.get('nome_empresa', 'HYPE EMPREENDIMENTOS')
        cnpj_empresa = dados_cliente.get('cnpj_empresa', '41.081.989/0001-92')
        
        pj_data = [[f"Nome Empresarial: {nome_empresa} - {cnpj_empresa}"]]
        pj_table = Table(pj_data, colWidths=[7*inch])
        pj_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, 0), 0.5, colors.black),
            ('MINIMUMHEIGHT', (0, 0), (-1, 0), 25),
            ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('LEFTPADDING', (0, 0), (-1, 0), 8),
            ('RIGHTPADDING', (0, 0), (-1, 0), 8),
        ]))
        return pj_table
    
    def _criar_tabela_fonte(self, dados_cliente):
        """Cria tabela da fonte pagadora"""
        cliente_nome = dados_cliente.get('cliente', '')
        cliente_cpf = dados_cliente.get('cpf', '')
        
        fonte_data = [[cliente_nome, 'CPF:', cliente_cpf]]
        fonte_table = Table(fonte_data, colWidths=[5.5*inch, 0.5*inch, 1*inch])
        fonte_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'LEFT'),
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEBEFORE', (0, 0), (0, 0), 0.5, colors.black),
            ('LINEAFTER', (-1, 0), (-1, 0), 0.5, colors.black),
            ('MINIMUMHEIGHT', (0, 0), (-1, 0), 25),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('LEFTPADDING', (0, 0), (-1, 0), 8),
            ('RIGHTPADDING', (0, 0), (-1, 0), 8),
        ]))
        return fonte_table
    
    def _criar_tabela_bem(self, dados_cliente):
        """Cria tabela dos dados do bem"""
        endereco = dados_cliente.get('endereco', '')
        numero = dados_cliente.get('numero', '')
        bairro = dados_cliente.get('bairro', '')
        cidade = dados_cliente.get('cidade', '')
        estado = dados_cliente.get('estado', '')
        endereco_completo = f"{endereco}, {numero} - {bairro}, {cidade} - {estado}"
        
        valor_venda = dados_cliente.get('valor_venda', 0)
        valor_imovel = f"R$ {valor_venda:,.2f}" if valor_venda > 0 else "Verificar"
        
        empreendimento = dados_cliente.get('empreendimento', '')
        unidade = dados_cliente.get('unidade', '')
        produto_texto = f"{empreendimento} - {unidade}"
        
        bem_data = [
            ['Produto', produto_texto],
            ['Endereço', endereco_completo],
            ['Valor do Imóvel', valor_imovel]
        ]
        bem_table = Table(bem_data, colWidths=[2*inch, 5*inch])
        bem_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.black),
            ('LINEBEFORE', (0, 0), (0, -1), 0.5, colors.black),
            ('LINEAFTER', (-1, 0), (-1, -1), 0.5, colors.black),
            ('MINIMUMHEIGHT', (0, 0), (-1, -1), 25),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return bem_table
    
    def _criar_tabela_pagamentos(self, valores_calculados):
        """Cria tabela de pagamentos"""
        receita_bruta = valores_calculados.get('receita_bruta', 0)
        despesas_acessorias = valores_calculados.get('despesas_acessorias', 0)
        
        pagamentos_data = [
            ['ESPECIFICAÇÃO', 'VALORES PAGOS EM 2024'],
            ['RECEITA', f"R$ {receita_bruta:,.2f}"],
            ['DESPESAS ACESSÓRIAS', f"R$ {despesas_acessorias:,.2f}"]
        ]
        
        pagamentos_table = Table(pagamentos_data, colWidths=[4*inch, 3*inch])
        pagamentos_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        return pagamentos_table
    
    def gerar_declaracao(self, cpf, dados_cliente, valores_calculados):
        """Gera PDF da declaração de IR"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            nome_pdf = f"Declaracao_IR_{cpf}_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(nome_pdf, pagesize=A4, 
                                  leftMargin=0.3*inch, rightMargin=0.8*inch,
                                  topMargin=0.8*inch, bottomMargin=0.8*inch)
            story = []
            
            title_style, section_style, normal_style = self._criar_estilos()
            
            # Cabeçalho com logos
            header_table = self._criar_cabecalho()
            story.append(header_table)
            story.append(Spacer(1, 20))
            
            # Seção 1 - PESSOA JURÍDICA
            story.append(Paragraph("1. PESSOA JURÍDICA:", section_style))
            story.append(self._criar_tabela_pj(dados_cliente))
            story.append(Spacer(1, 15))
            
            # Seção 2 - FONTE PAGADORA PESSOA FÍSICA
            story.append(Paragraph("2. FONTE PAGADORA PESSOA FÍSICA:", section_style))
            story.append(self._criar_tabela_fonte(dados_cliente))
            story.append(Spacer(1, 15))
            
            # Seção 3 - DADOS DO BEM
            story.append(Paragraph("3. DADOS DO BEM:", section_style))
            story.append(self._criar_tabela_bem(dados_cliente))
            story.append(Spacer(1, 15))
            
            # Seção 4 - INFORME DE PAGAMENTOS
            story.append(Paragraph("4. INFORME DE PAGAMENTOS EFETUADOS PARA FINS DE IMPOSTO DE RENDA:", section_style))
            story.append(self._criar_tabela_pagamentos(valores_calculados))
            story.append(Spacer(1, 30))
            
            # Footer
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D9D9D9'), spaceAfter=10))
            
            data_emissao = datetime.now().strftime('%d de %B de %Y')
            meses_pt = {
                'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
                'April': 'abril', 'May': 'maio', 'June': 'junho',
                'July': 'julho', 'August': 'agosto', 'September': 'setembro',
                'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
            }
            
            for mes_en, mes_pt in meses_pt.items():
                data_emissao = data_emissao.replace(mes_en, mes_pt)
            
            story.append(Paragraph(f"Emitido em {data_emissao}", normal_style))
            story.append(Spacer(1, 15))
            
            # Linha de assinatura centralizada
            story.append(HRFlowable(width="50%", thickness=0.5, color=colors.black, spaceAfter=5))
            
            # Texto da empresa centralizado embaixo da linha
            empresa_style = ParagraphStyle(
                'EmpresaStyle',
                parent=normal_style,
                fontName='Helvetica',
                fontSize=10,
                alignment=TA_CENTER,  # Centralizar o texto
                textColor=colors.black,
                leading=12
            )
            story.append(Paragraph("Hyperion Empreendimentos e Incorporações SA", empresa_style))
            
            doc.build(story)
            
            logger.info(f"PDF gerado com sucesso: {nome_pdf}")
            return nome_pdf
            
        except Exception as e:
            import traceback
            logger.error(f"Erro ao gerar PDF: {str(e)}")
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            return None

class GeradorIR:
    """Classe principal do gerador de IR"""
    
    def __init__(self):
        from config import FILES_CONFIG
        self.config = config
        self.arquivo_excel = FILES_CONFIG['EXCEL_FILE']
        self.buscador = BuscadorCliente(self.arquivo_excel)
        self.calculador = CalculadorFinanceiro(self.arquivo_excel)
        self.gerador_pdf = GeradorPDF()
    
    def gerar_declaracao(self, cpf):
        """Função principal para gerar declaração de IR"""
        logger.info(f"Iniciando geração de declaração para CPF: {cpf}")
        
        # Validar CPF
        is_valid, cpf_clean = ValidadorCPF.validar_cpf(cpf)
        if not is_valid:
            logger.error(f"CPF inválido: {cpf}")
            return False, "CPF inválido"
        
        # Buscar dados do cliente
        dados_cliente = self.buscador.buscar_por_cpf(cpf_clean)
        if not dados_cliente:
            logger.error(f"Cliente não encontrado para CPF: {cpf_clean}")
            return False, "Cliente não encontrado"
        
        logger.info(f"Cliente encontrado: {dados_cliente['cliente']}")
        
        # Calcular valores financeiros
        receita_bruta = self.calculador.calcular_receita_bruta(cpf_clean)
        despesas_acessorias = self.calculador.calcular_despesas_acessorias(cpf_clean)
        
        valores_calculados = {
            'receita_bruta': receita_bruta,
            'despesas_acessorias': despesas_acessorias
        }
        
        logger.info(f"Valores calculados - Receita: R$ {receita_bruta:,.2f}, Despesas: R$ {despesas_acessorias:,.2f}")
        
        # Validar consistência dos saldos
        saldo_union = self.calculador.calcular_saldo_union(cpf_clean)
        saldo_paggo_dunning = self.calculador.verificar_saldo_paggo_dunning(cpf_clean)
        
        is_consistente, diferenca = ValidadorConsistencia.validar_saldos(saldo_union, saldo_paggo_dunning)
        
        if not is_consistente:
            logger.warning(f"Inconsistência nos saldos detectada. Diferença: R$ {diferenca:,.2f}")
            print(f"⚠️  ATENÇÃO: Inconsistência nos saldos detectada. Diferença: R$ {diferenca:,.2f}")
        
        # Gerar PDF
        nome_pdf = self.gerador_pdf.gerar_declaracao(cpf_clean, dados_cliente, valores_calculados)
        
        if nome_pdf:
            logger.info(f"Declaração gerada com sucesso: {nome_pdf}")
            return True, nome_pdf
        else:
            logger.error("Erro ao gerar PDF")
            return False, "Erro ao gerar PDF"

def main():
    """Função principal"""
    print("🏢 GERADOR DE DECLARAÇÃO DE IR - VERSÃO REFATORADA 3.0")
    print("=" * 60)
    
    gerador = GeradorIR()
    
    while True:
        print(f"\n📋 Opções:")
        print(f"   1. Gerar declaração para CPF específico")
        print(f"   2. Testar com CPF da planilha")
        print(f"   3. Sair")
        
        try:
            opcao = input(f"\nEscolha uma opção (1-3): ").strip()
            
            if opcao == "1":
                cpf = input(f"Digite o CPF: ").strip()
                if cpf:
                    sucesso, resultado = gerador.gerar_declaracao(cpf)
                    if sucesso:
                        print(f"✅ Declaração gerada com sucesso: {resultado}")
                    else:
                        print(f"❌ Erro: {resultado}")
            
            elif opcao == "2":
                cpf_teste = config['TEST']['TEST_CPF']
                print(f"Testando com CPF: {cpf_teste}")
                sucesso, resultado = gerador.gerar_declaracao(cpf_teste)
                if sucesso:
                    print(f"✅ Declaração gerada com sucesso: {resultado}")
                else:
                    print(f"❌ Erro: {resultado}")
            
            elif opcao == "3":
                print(f"👋 Saindo...")
                break
            
            else:
                print(f"❌ Opção inválida!")
                
        except KeyboardInterrupt:
            print(f"\n👋 Saindo...")
            break
        except Exception as e:
            logger.error(f"Erro no menu principal: {str(e)}")
            print(f"❌ Erro: {str(e)}")

def testar_implementacao():
    """Função para testar a implementação completa"""
    print("🧪 TESTANDO IMPLEMENTAÇÃO COMPLETA")
    print("=" * 50)
    
    gerador = GeradorIR()
    
    # Teste 1: CPF válido da configuração
    cpf_teste = config['TEST']['TEST_CPF']
    print(f"\n📋 Teste 1: CPF da configuração ({cpf_teste})")
    
    sucesso, resultado = gerador.gerar_declaracao(cpf_teste)
    if sucesso:
        print(f"✅ SUCESSO: {resultado}")
    else:
        print(f"❌ FALHA: {resultado}")
    
    # Teste 2: CPF conhecido dos logs
    cpf_conhecido = "91446260968"
    print(f"\n📋 Teste 2: CPF conhecido ({cpf_conhecido})")
    
    sucesso, resultado = gerador.gerar_declaracao(cpf_conhecido)
    if sucesso:
        print(f"✅ SUCESSO: {resultado}")
    else:
        print(f"❌ FALHA: {resultado}")
    
    # Teste 3: Busca por nome
    print(f"\n📋 Teste 3: Busca por nome")
    dados_cliente = gerador.buscador.buscar_por_nome("Fabio Roberto")
    if dados_cliente:
        print(f"✅ Cliente encontrado: {dados_cliente['cliente']}")
        print(f"   CPF: {dados_cliente['cpf']}")
        print(f"   Empreendimento: {dados_cliente['empreendimento']}")
    else:
        print(f"❌ Cliente não encontrado")
    
    print(f"\n🏁 TESTE CONCLUÍDO")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        testar_implementacao()
    else:
        main()

# Funções de interface para o servidor Flask
def buscar_cliente_por_cpf(cpf):
    """Interface para buscar cliente por CPF - VERSÃO OTIMIZADA"""
    try:
        # Cache para busca de clientes
        if not hasattr(buscar_cliente_por_cpf, '_client_cache'):
            buscar_cliente_por_cpf._client_cache = {}
            buscar_cliente_por_cpf._cache_timestamp = None
        
        # Verificar cache
        cache_key = f"client_{cpf}"
        if cache_key in buscar_cliente_por_cpf._client_cache:
            return buscar_cliente_por_cpf._client_cache[cache_key]
        
        # Carregar dados se cache expirado
        if not buscar_cliente_por_cpf._cache_timestamp:
            logger.info("Carregando cache de clientes...")
            buscar_cliente_por_cpf._client_cache = {}
            
            from config import FILES_CONFIG
            from openpyxl import load_workbook
            
            wb = load_workbook(FILES_CONFIG['EXCEL_FILE'], data_only=True, read_only=True)
            
            if 'Base de Clientes' in wb.sheetnames:
                ws = wb['Base de Clientes']
                
                # Ler apenas as primeiras 1000 linhas para performance
                for row in range(2, min(ws.max_row + 1, 1000)):
                    cpf_col = ws.cell(row=row, column=3).value  # Coluna C - CPF
                    nome_col = ws.cell(row=row, column=2).value  # Coluna B - Nome
                    empreendimento_col = ws.cell(row=row, column=4).value  # Coluna D - Empreendimento
                    
                    if cpf_col and nome_col:
                        cpf_clean = str(cpf_col).replace('.', '').replace('-', '')
                        cache_key_client = f"client_{cpf_clean}"
                        
                        buscar_cliente_por_cpf._client_cache[cache_key_client] = {
                            'cliente': str(nome_col).strip(),
                            'cpf': str(cpf_col).strip(),
                            'empreendimento': str(empreendimento_col).strip() if empreendimento_col else ''
                        }
            
            wb.close()
            buscar_cliente_por_cpf._cache_timestamp = True
        
        # Buscar no cache
        cpf_clean = str(cpf).replace('.', '').replace('-', '')
        cache_key_clean = f"client_{cpf_clean}"
        
        if cache_key_clean in buscar_cliente_por_cpf._client_cache:
            logger.info(f"Cliente encontrado por CPF exato: {buscar_cliente_por_cpf._client_cache[cache_key_clean]['cliente']}")
            return buscar_cliente_por_cpf._client_cache[cache_key_clean]
        
        # Busca por similaridade de CPF se não encontrou exato
        for cached_cpf, cliente_data in buscar_cliente_por_cpf._client_cache.items():
            if cpf_clean in cached_cpf or cached_cpf in cpf_clean:
                logger.info(f"Cliente encontrado por CPF similar: {cliente_data['cliente']}")
                return cliente_data
        
        logger.warning(f"Cliente não encontrado para CPF: {cpf}")
        return None
        
    except Exception as e:
        logger.error(f"Erro ao buscar cliente por CPF {cpf}: {str(e)}")
        return None

def _normalizar_nome_global(nome):
    """Normaliza nome para comparação - função global"""
    import unicodedata
    if not nome:
        return ""
    # Remover acentos
    nome_normalizado = unicodedata.normalize('NFD', str(nome))
    nome_sem_acentos = ''.join(c for c in nome_normalizado if unicodedata.category(c) != 'Mn')
    return nome_sem_acentos.upper().strip()

def _nomes_sao_similares_global(nome1, nome2, threshold=0.9):
    """Verifica se dois nomes são similares o suficiente - função global"""
    nome1_norm = _normalizar_nome_global(nome1)
    nome2_norm = _normalizar_nome_global(nome2)
    
    # Se são exatamente iguais
    if nome1_norm == nome2_norm:
        return True
    
    # Dividir em palavras
    palavras1 = [p for p in nome1_norm.split() if len(p) > 2]
    palavras2 = [p for p in nome2_norm.split() if len(p) > 2]
    
    if not palavras1 or not palavras2:
        return False
    
    # Contar palavras em comum
    palavras_comuns = 0
    for palavra1 in palavras1:
        for palavra2 in palavras2:
            if palavra1 == palavra2:
                palavras_comuns += 1
                break
    
    # Calcular similaridade
    max_palavras = max(len(palavras1), len(palavras2))
    similaridade = palavras_comuns / max_palavras
    
    return similaridade >= threshold

# Cache global para dados processados
_excel_cache = {}
_cache_timestamp = None
_cache_file_path = None

def _get_cache_key(cpf, dados_cliente):
    """Gera chave única para cache"""
    return f"{cpf}_{dados_cliente['cliente']}_{dados_cliente.get('empreendimento', '')}"

def _is_cache_valid():
    """Verifica se o cache ainda é válido"""
    global _cache_timestamp, _cache_file_path
    from config import FILES_CONFIG
    import os
    
    if not _cache_timestamp or not _cache_file_path:
        return False
    
    # Verificar se o arquivo Excel foi modificado
    try:
        current_mtime = os.path.getmtime(FILES_CONFIG['EXCEL_FILE'])
        return current_mtime <= _cache_timestamp
    except:
        return False

def _load_excel_data():
    """Carrega dados do Excel de forma otimizada com cache"""
    global _excel_cache, _cache_timestamp, _cache_file_path
    from config import FILES_CONFIG
    import os
    
    # Verificar se cache é válido
    if _is_cache_valid():
        logger.info("Usando cache de dados do Excel")
        return _excel_cache
    
    logger.info("Carregando dados do Excel (cache expirado)")
    
    try:
        # Carregar workbook
        wb = load_workbook(FILES_CONFIG['EXCEL_FILE'], data_only=True, read_only=True)
        
        # Estrutura de dados otimizada
        union_data = []
        erp_data = []
        
        # Processar UNION-2024 de forma otimizada
        if 'UNION - 2024' in wb.sheetnames:
            ws_union = wb['UNION - 2024']
            logger.info("Indexando dados UNION-2024...")
            
            # Ler apenas as colunas necessárias
            for row in range(2, min(ws_union.max_row + 1, 2000)):  # Limitar a 2000 linhas
                cliente = ws_union.cell(row=row, column=5).value
                cpf = ws_union.cell(row=row, column=6).value
                tipo = ws_union.cell(row=row, column=16).value
                valor = ws_union.cell(row=row, column=7).value
                
                if cliente and tipo and valor and isinstance(valor, (int, float)):
                    union_data.append({
                        'cliente': str(cliente).strip(),
                        'cpf': str(cpf).strip() if cpf else '',
                        'tipo': str(tipo).upper(),
                        'valor': float(valor)
                    })
        
        # Processar UNIFICADA ERP de forma otimizada
        if 'UNIFICADA ERP (paggo e dunning)' in wb.sheetnames:
            ws_erp = wb['UNIFICADA ERP (paggo e dunning)']
            logger.info("Indexando dados ERP...")
            
            # Ler apenas as colunas necessárias
            for row in range(2, min(ws_erp.max_row + 1, 2000)):  # Limitar a 2000 linhas
                empreendimento = ws_erp.cell(row=row, column=2).value
                cpf = ws_erp.cell(row=row, column=6).value
                valor = ws_erp.cell(row=row, column=17).value
                
                if valor and isinstance(valor, (int, float)):
                    erp_data.append({
                        'empreendimento': str(empreendimento).strip() if empreendimento else '',
                        'cpf': str(cpf).strip() if cpf else '',
                        'valor': float(valor)
                    })
        
        wb.close()
        
        # Atualizar cache
        _excel_cache = {
            'union': union_data,
            'erp': erp_data
        }
        _cache_timestamp = os.path.getmtime(FILES_CONFIG['EXCEL_FILE'])
        _cache_file_path = FILES_CONFIG['EXCEL_FILE']
        
        logger.info(f"Cache atualizado: {len(union_data)} registros UNION, {len(erp_data)} registros ERP")
        return _excel_cache
        
    except Exception as e:
        logger.error(f"Erro ao carregar dados do Excel: {str(e)}")
        return {'union': [], 'erp': []}

def _match_cliente(nome_cliente, cpf_cliente, nome_planilha, cpf_planilha):
    """Função otimizada para matching de cliente"""
    # 1. Match por CPF (mais rápido)
    if cpf_cliente and cpf_planilha:
        cpf_clean = str(cpf_cliente).replace('.', '').replace('-', '')
        cpf_planilha_clean = str(cpf_planilha).replace('.', '').replace('-', '')
        if cpf_clean in cpf_planilha_clean or cpf_planilha_clean in cpf_clean:
            return True, "CPF"
    
    # 2. Match por nome exato
    if nome_cliente and nome_planilha:
        if nome_cliente.strip().upper() == nome_planilha.strip().upper():
            return True, "NOME_EXATO"
    
    # 3. Match por palavras-chave (otimizado)
    if nome_cliente and nome_planilha:
        palavras_cliente = set(p.strip().upper() for p in nome_cliente.split() if len(p.strip()) > 2)
        palavras_planilha = set(p.strip().upper() for p in nome_planilha.split() if len(p.strip()) > 2)
        
        if len(palavras_cliente & palavras_planilha) >= 2:  # Interseção de conjuntos
            return True, "NOME_SIMILAR"
    
    return False, ""

def calcular_todos_valores_otimizado(cpf, dados_cliente):
    """Calcula todos os valores financeiros com performance ultra-otimizada"""
    try:
        logger.info(f"Iniciando cálculo otimizado para {dados_cliente['cliente']}")
        
        # Carregar dados do Excel (com cache)
        excel_data = _load_excel_data()
        
        receita_bruta = 0
        despesas_acessorias = 0
        saldo_union = 0
        saldo_paggo_dunning = 0
        
        nome_cliente = dados_cliente['cliente']
        cpf_cliente = dados_cliente['cpf']
        empreendimento_cliente = dados_cliente.get('empreendimento', '')
        
        # Processar dados UNION (otimizado)
        logger.info("Processando dados UNION...")
        for registro in excel_data['union']:
            match, match_type = _match_cliente(
                nome_cliente, cpf_cliente,
                registro['cliente'], registro['cpf']
            )
            
            if match:
                valor = registro['valor']
                tipo = registro['tipo']
                
                if "RECEITA BRUTA" in tipo:
                    receita_bruta += valor
                    saldo_union += valor
                    logger.debug(f"Receita encontrada ({match_type}): R$ {valor:,.2f}")
                elif "ATIVO CIRCULANTE" in tipo:
                    despesas_acessorias += valor
                    logger.debug(f"Despesa encontrada ({match_type}): R$ {valor:,.2f}")
        
        # Processar dados ERP (otimizado)
        logger.info("Processando dados ERP...")
        for registro in excel_data['erp']:
            # Match por CPF primeiro (mais rápido)
            if cpf_cliente and registro['cpf']:
                cpf_clean = str(cpf_cliente).replace('.', '').replace('-', '')
                cpf_planilha_clean = str(registro['cpf']).replace('.', '').replace('-', '')
                
                if cpf_clean in cpf_planilha_clean or cpf_planilha_clean in cpf_clean:
                    # Verificar empreendimento se disponível
                    if empreendimento_cliente and registro['empreendimento']:
                        if empreendimento_cliente in registro['empreendimento']:
                            saldo_paggo_dunning += registro['valor']
                            logger.debug(f"Saldo ERP encontrado (CPF+Emp): R$ {registro['valor']:,.2f}")
                    else:
                        # Aceitar só por CPF se não tem empreendimento
                        saldo_paggo_dunning += registro['valor']
                        logger.debug(f"Saldo ERP encontrado (CPF): R$ {registro['valor']:,.2f}")
        
        logger.info(f"Cálculo concluído - Receita: R$ {receita_bruta:,.2f}, Despesas: R$ {despesas_acessorias:,.2f}")
        return receita_bruta, despesas_acessorias, saldo_union, saldo_paggo_dunning
        
    except Exception as e:
        logger.error(f"Erro no cálculo otimizado: {str(e)}")
        return 0, 0, 0, 0

def calcular_valores_financeiros_manual(cpf, dados_cliente):
    """Interface para calcular valores financeiros com diagnóstico detalhado - OTIMIZADO"""
    try:
        # Calcular todos os valores de uma vez (otimizado)
        receita_bruta, despesas_acessorias, saldo_union, saldo_paggo_dunning = calcular_todos_valores_otimizado(cpf, dados_cliente)
        
        # Contar registros encontrados
        registros_encontrados = 0
        fontes_dados = []
        
        if receita_bruta > 0:
            registros_encontrados += 1
            fontes_dados.append(f"Receita Bruta: R$ {receita_bruta:,.2f} (UNION-2024)")
        
        if despesas_acessorias > 0:
            registros_encontrados += 1
            fontes_dados.append(f"Despesas: R$ {despesas_acessorias:,.2f} (UNION-2024)")
        
        if saldo_union > 0:
            registros_encontrados += 1
            fontes_dados.append(f"Saldo Union: R$ {saldo_union:,.2f} (UNION-2024)")
        
        if saldo_paggo_dunning > 0:
            registros_encontrados += 1
            fontes_dados.append(f"Saldo Paggo/Dunning: R$ {saldo_paggo_dunning:,.2f} (ERP)")
        
        # Verificar se existe diferença calculada na Base de Clientes (coluna S)
        diferenca_base_clientes = None
        try:
            from config import FILES_CONFIG
            from openpyxl import load_workbook
            wb = load_workbook(FILES_CONFIG['EXCEL_FILE'], data_only=True, read_only=True)
            if 'Base de Clientes' in wb.sheetnames:
                ws_base = wb['Base de Clientes']
                for row in range(2, ws_base.max_row + 1):
                    cpf_col_c = ws_base.cell(row=row, column=3).value  # Coluna C - CPF
                    diferenca_col_s = ws_base.cell(row=row, column=19).value  # Coluna S - Diferença
                    
                    if (cpf_col_c and str(cpf) in str(cpf_col_c) and 
                        diferenca_col_s and isinstance(diferenca_col_s, (int, float)) and diferenca_col_s != 0):
                        diferenca_base_clientes = float(diferenca_col_s)
                        break
            wb.close()
        except Exception as e:
            logger.warning(f"Erro ao verificar diferença na Base de Clientes: {str(e)}")
        
        # Preparar informações de consistência
        erro_consistencia = None
        pode_gerar_pdf = True  # SEMPRE pode gerar PDF agora
        
        # Se existe diferença na Base de Clientes, mostrar como informação
        if diferenca_base_clientes is not None:
            erro_consistencia = {
                'tipo': 'DIFERENCA_INFORMATIVA',
                'descricao': 'Diferença identificada entre Union e ERP',
                'diferenca': diferenca_base_clientes,
                'saldo_union': saldo_union,
                'saldo_paggo': saldo_paggo_dunning,
                'fonte': 'Base de Clientes - Coluna S',
                'observacao': 'Esta diferença não impede a geração do PDF'
            }
        
        # Verificar se tem dados suficientes
        total_valores = receita_bruta + despesas_acessorias + saldo_union + saldo_paggo_dunning
        
        if total_valores == 0:
            erro_consistencia = {
                'tipo': 'SEM_DADOS_FINANCEIROS',
                'descricao': 'Nenhum dado financeiro encontrado nas planilhas',
                'detalhes': [
                    'Cliente existe na Base de Clientes',
                    'Mas não possui registros nas planilhas UNION-2024',
                    'Nem na planilha UNIFICADA ERP (paggo e dunning)',
                    'Verifique se os dados estão nas planilhas corretas'
                ]
            }
            pode_gerar_pdf = False
        
        return {
            'receita_bruta': receita_bruta,
            'despesas_acessorias': despesas_acessorias,
            'saldo_union': saldo_union,
            'saldo_paggo_dunning': saldo_paggo_dunning,
            'registros_encontrados': registros_encontrados,
            'fontes_dados': fontes_dados,
            'erro_consistencia': erro_consistencia,
            'pode_gerar_pdf': pode_gerar_pdf,
            'total_valores': total_valores
        }
        
    except Exception as e:
        logger.error(f"Erro ao calcular valores financeiros para CPF {cpf}: {str(e)}")
        return {
            'receita_bruta': 0,
            'despesas_acessorias': 0,
            'saldo_union': 0,
            'saldo_paggo_dunning': 0,
            'registros_encontrados': 0,
            'fontes_dados': [],
            'erro_consistencia': {
                'tipo': 'ERRO_SISTEMA',
                'descricao': f'Erro interno ao processar dados: {str(e)}',
                'detalhes': ['Contate o suporte técnico']
            },
            'pode_gerar_pdf': False,
            'total_valores': 0
        }

def gerar_pdf_declaracao(cpf, dados_cliente, valores_calculados):
    """Interface para gerar PDF da declaração - VERSÃO OTIMIZADA"""
    try:
        # Cache para gerador de PDF
        if not hasattr(gerar_pdf_declaracao, '_pdf_generator'):
            gerar_pdf_declaracao._pdf_generator = GeradorPDF()
        
        # Gerar PDF usando cache
        nome_pdf = gerar_pdf_declaracao._pdf_generator.gerar_declaracao(cpf, dados_cliente, valores_calculados)
        return nome_pdf
    except Exception as e:
        logger.error(f"Erro ao gerar PDF para CPF {cpf}: {str(e)}")
        return None 