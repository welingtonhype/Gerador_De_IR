# Gerador de Declaração de IR

Sistema web para geração de declarações de Imposto de Renda baseado em dados de planilha Excel.

## Funcionalidades

- Busca de clientes por CPF
- Cálculo automático de receita bruta e despesas acessórias
- Geração de PDF com declaração de IR
- Interface web responsiva

## Tecnologias

- **Backend**: Python/Flask
- **Frontend**: HTML/CSS/JavaScript
- **PDF**: ReportLab
- **Excel**: OpenPyXL
- **Deploy**: Railway

## Estrutura do Projeto

```
├── simple_server.py      # Servidor Flask principal
├── Scripts/
│   └── gerador_ir_refatorado.py  # Gerador de PDF
├── index.html           # Interface web
├── styles.css           # Estilos CSS
├── script.js            # JavaScript frontend
├── requirements.txt     # Dependências Python
├── railway.json         # Configuração Railway
└── IR 2024 - NÃO ALTERAR.xlsx  # Planilha de dados
```

## Deploy

O projeto está configurado para deploy no Railway:

1. **Railway.json**: Configuração do serviço web
2. **Requirements.txt**: Dependências Python
3. **Simple_server.py**: Servidor Flask principal

## Uso

1. Acesse a interface web
2. Digite o CPF do cliente
3. O sistema busca os dados na planilha
4. Calcula receita bruta e despesas acessórias
5. Gera PDF com a declaração

## Planilha de Dados

A planilha Excel deve conter:
- **Base de Clientes**: Dados dos clientes (CPF, nome, empreendimento, etc.)
- **UNION - 2024**: Dados financeiros para cálculos

## Desenvolvimento

Para rodar localmente:

```bash
pip install -r requirements.txt
python simple_server.py
```

Acesse: http://localhost:10000 