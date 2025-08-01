# 🏢 Gerador de IR - Hype Empreendimentos

Sistema web para geração automática de declarações de Imposto de Renda baseado em dados de clientes.

## 📋 Visão Geral

Este sistema permite gerar declarações de IR em PDF a partir do CPF do cliente, consultando dados em planilha Excel e calculando automaticamente os valores financeiros necessários.

## 🚀 Deploy Rápido

### Windows:
```bash
deploy.bat
```

### Linux/Mac:
```bash
chmod +x deploy.sh
./deploy.sh
```

## 📁 Estrutura do Projeto

```
Declaração de IR/
├── 🐳 DOCKER & DEPLOY
│   ├── Dockerfile              # Configuração Docker para produção
│   ├── docker-compose.prod.yml # Orquestração com Nginx
│   ├── nginx.conf              # Configuração Nginx com SSL
│   ├── deploy.sh               # Script deploy Linux/Mac
│   └── deploy.bat              # Script deploy Windows
│
├── 🖥️ BACKEND
│   ├── server.py               # Servidor Flask principal
│   ├── config.py               # Configurações centralizadas
│   ├── start.py                # Script de inicialização
│   └── requirements.txt        # Dependências Python
│
├── 🎨 FRONTEND
│   ├── index.html              # Interface principal
│   ├── script.js               # Lógica JavaScript
│   └── styles.css              # Estilos CSS
│
├── 📊 DADOS
│   ├── IR 2024 - NÃO ALTERAR.xlsx  # Base de dados clientes
│   ├── Scripts/
│   │   └── gerador_ir_refatorado.py # Lógica de geração PDF
│   └── Imagens/
│       ├── Imagem1.png         # Logo brasão
│       └── Imagem2.png         # Logo Hype
│
└── 📖 DOCUMENTAÇÃO
    ├── README.md               # Este arquivo
    └── DEPLOY_GUIDE.md         # Guia detalhado de deploy
```

## ⚡ Início Rápido (Desenvolvimento)

1. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

2. **Iniciar servidor:**
```bash
python start.py
```

3. **Acessar:** http://localhost:5000

## 🔧 Funcionalidades

- ✅ Busca de cliente por CPF
- ✅ Cálculo automático de valores financeiros
- ✅ Geração de PDF com layout profissional
- ✅ Interface web responsiva
- ✅ Validação de dados
- ✅ Rate limiting e segurança
- ✅ Logs estruturados
- ✅ Health checks

## 🐳 Deploy em Produção

### Opção 1: Docker (Recomendado)
```bash
# Windows
deploy.bat

# Linux/Mac
./deploy.sh
```

### Opção 2: Servidor Tradicional
```bash
# Instalar dependências
pip install -r requirements.txt

# Iniciar com Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 2 server:app
```

### Opção 3: Cloud
- **AWS EC2:** Upload + `./deploy.sh`
- **Google Cloud Run:** `gcloud run deploy`
- **Heroku:** `git push heroku main`

## 🔒 Segurança

- HTTPS obrigatório em produção
- Rate limiting configurado
- Headers de segurança
- Validação de entradas
- Logs de auditoria

## 📊 Monitoramento

### Health Check:
```bash
curl http://localhost/health
```

### Logs:
```bash
# Docker
docker-compose -f docker-compose.prod.yml logs -f

# Tradicional
tail -f logs/server.log
```

## 🛠️ Configurações

### Variáveis de Ambiente:
```bash
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=8000
SECRET_KEY=sua-chave-secreta
```

### Arquivos Configuração:
- `config.py` - Configurações da aplicação
- `nginx.conf` - Configurações do proxy reverso
- `docker-compose.prod.yml` - Orquestração dos serviços

## 📞 Suporte

**Hype Empreendimentos e Incorporações SA**
- 📧 Email: suporte@hype.com.br
- 📱 Telefone: (11) 9999-9999

## 📄 Licença

Sistema proprietário - Hype Empreendimentos e Incorporações SA

---

**Versão:** 1.0.0  
**Última atualização:** $(date +%Y-%m-%d)