# 🚀 Deploy no Render (Gratuito + Permanente)

## Passo 1: Criar conta Render
1. Acesse: https://render.com
2. Signup com GitHub

## Passo 2: Conectar repositório
1. "New" → "Web Service"
2. Connect GitHub repository
3. Selecionar repositório do projeto

## Passo 3: Configurações do deploy
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 server:app
```

## Passo 4: Variáveis de ambiente
- FLASK_ENV=production
- DEBUG=False
- HOST=0.0.0.0

## ✅ Resultado
URL permanente: `https://seuapp.onrender.com`

## 💰 Custos
- **GRATUITO** até 512MB RAM
- Sleep após 15min inativo (acorda automático)
- SSL automático