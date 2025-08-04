# Gerador de IR - Hype Empreendimentos

Sistema web para geração automática de declarações de Imposto de Renda para clientes da Hype Empreendimentos.

## 🚀 Deploy no Railway

Este projeto está otimizado para deploy no Railway. Para fazer o deploy:

### 1. Conectar ao Railway
- Acesse [railway.app](https://railway.app)
- Conecte seu repositório GitHub
- Selecione este repositório

### 2. Configurar o Serviço
- **Tipo**: Web Service
- **Runtime**: Python 3.9
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --max-requests 100 --max-requests-jitter 10 --worker-class sync --preload server:app`

### 3. Variáveis de Ambiente
```
PORT=10000
HOST=0.0.0.0
DEBUG=false
WORKERS=2
TIMEOUT=300
MAX_REQUESTS=100
MAX_REQUESTS_JITTER=10
```

## 📋 Funcionalidades

- **Busca de Clientes**: Busca clientes por CPF na base de dados
- **Geração de PDF**: Gera declarações de IR em PDF
- **Download Seguro**: Sistema de download com validação
- **Health Check**: Monitoramento de saúde da aplicação
- **Rate Limiting**: Proteção contra spam
- **Logs Estruturados**: Sistema completo de logging

## 🔧 Tecnologias

- **Backend**: Flask 2.3.3
- **PDF**: ReportLab 4.0.4
- **Excel**: OpenPyXL 3.1.2
- **Servidor**: Gunicorn 21.2.0
- **CORS**: Flask-CORS 4.0.0
- **Rate Limiting**: Flask-Limiter 3.5.0
- **Redis**: redis 5.0.1
- **Celery**: celery 5.3.4

## 📁 Estrutura do Projeto

```
├── server.py              # Servidor principal Flask
├── celery_app.py          # Configuração Celery
├── tasks.py               # Tasks assíncronas
├── config.py              # Configurações centralizadas
├── requirements.txt        # Dependências Python
├── railway.json           # Configuração Railway
├── Procfile               # Comandos de produção
├── index.html             # Interface web
├── styles.css             # Estilos CSS
├── script.js              # JavaScript frontend
├── Scripts/
│   └── gerador_ir_refatorado.py  # Lógica de geração de PDF
├── Imagens/
│   ├── Imagem1.png        # Logo brasão
│   └── Imagem2.png        # Logo Hype
└── IR 2024 - NÃO ALTERAR.xlsx  # Base de dados
```

## 🔒 Segurança

- Validação de CPF
- Sanitização de inputs
- Rate limiting
- Headers de segurança
- CORS configurado
- Logs de auditoria

## 📊 Monitoramento

- Health check endpoint: `/api/health`
- Logs estruturados
- Métricas de performance
- Tratamento de erros

## 🚀 Endpoints

- `GET /` - Página principal
- `POST /api/buscar-cliente` - Buscar cliente por CPF
- `POST /api/gerar-pdf` - Gerar PDF da declaração
- `GET /api/download-pdf/<filename>` - Download do PDF
- `GET /api/health` - Health check

## 📝 Logs

Os logs são salvos em:
- `logs/server.log` - Logs do servidor

## 🔧 Configuração Local

Para desenvolvimento local:

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python server.py
```

O servidor estará disponível em `http://localhost:5000`

## 📞 Suporte

- **Email**: suporte@hype.com.br
- **Telefone**: (11) 9999-9999
- **Empresa**: Hype Empreendimentos e Incorporações SA

## 📄 Licença

Sistema proprietário da Hype Empreendimentos.