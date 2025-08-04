# 🚀 Guia de Deploy - Railway + Redis Cloud

## 📋 Pré-requisitos

1. **Conta Railway**: [railway.app](https://railway.app)
2. **Redis Cloud**: Já configurado ✅
3. **Repositório GitHub**: Conectado

## 🔧 Configuração Railway

### 1. Conectar Repositório

1. Acesse [railway.app](https://railway.app)
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha seu repositório

### 2. Configurar Variáveis de Ambiente

No Railway, vá em **Variables** e adicione:

```env
# Redis Cloud (substitua pelos seus dados)
REDIS_URL=redis://default:SUA_SENHA@SEU_HOST:PORTA
REDIS_HOST=SEU_HOST_REDIS
REDIS_PORT=PORTA_REDIS
REDIS_PASSWORD=SUA_SENHA_REDIS
REDIS_DB=0

# Servidor
PORT=10000
HOST=0.0.0.0
DEBUG=false
WORKERS=2
TIMEOUT=300
MAX_REQUESTS=100
MAX_REQUESTS_JITTER=10
```

### 3. Configurar Serviços

O Railway detectará automaticamente os serviços do `railway.json`:

- **Web Service**: Aplicação Flask
- **Worker Service**: Celery worker

## 🚀 Deploy

### 1. Deploy Automático

1. Railway detectará o `railway.json`
2. Build será executado automaticamente
3. Dois serviços serão criados:
   - **Web**: `https://seu-app.railway.app`
   - **Worker**: Processamento em background

### 2. Verificar Deploy

```bash
# Ver logs do web service
railway logs --service web

# Ver logs do worker
railway logs --service worker

# Ver status dos serviços
railway status
```

## 🧪 Teste da Aplicação

### 1. Health Check

```bash
curl https://seu-app.railway.app/api/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "redis_status": "healthy",
  "timestamp": "2024-01-XX...",
  "version": "2.0.0"
}
```

### 2. Teste Redis

```bash
# Conectar ao Redis (substitua pelos seus dados)
redis-cli -u redis://default:SUA_SENHA@SEU_HOST:PORTA

# Testar conexão
PING
# Deve retornar: PONG
```

### 3. Teste de Processamento

1. Acesse: `https://seu-app.railway.app`
2. Digite um CPF válido
3. Verifique se o processamento assíncrono funciona

## 🔍 Monitoramento

### Logs em Tempo Real

```bash
# Logs do web service
railway logs --service web --follow

# Logs do worker
railway logs --service worker --follow
```

### Métricas

- **Uptime**: Railway dashboard
- **Performance**: Logs de aplicação
- **Redis**: Redis Cloud dashboard

## 🛠️ Troubleshooting

### Problema: Worker não inicia

**Solução:**
```bash
# Verificar logs do worker
railway logs --service worker

# Verificar se Redis está acessível
railway run --service worker python -c "
import redis
r = redis.Redis.from_url('SUA_URL_REDIS')
print('Redis OK:', r.ping())
"
```

### Problema: Web service não responde

**Solução:**
```bash
# Verificar logs
railway logs --service web

# Verificar variáveis de ambiente
railway variables

# Reiniciar serviço
railway restart --service web
```

### Problema: Redis não conecta

**Solução:**
1. Verifique se a URL do Redis está correta
2. Teste conexão local:
```bash
redis-cli -u SUA_URL_REDIS
```

## 📊 Vantagens Railway vs Render

| Aspecto | Render | Railway |
|---------|--------|---------|
| RAM | 512MB | 1GB+ |
| Workers | 1 | 2+ |
| Timeout | 120s | 300s |
| Cold Start | Lento | Rápido |
| Redis | Não | Sim |
| Processamento | Síncrono | Assíncrono |

## 🎯 Próximos Passos

1. ✅ **Deploy Railway** - Concluído
2. ✅ **Redis Cloud** - Configurado
3. ✅ **Processamento Assíncrono** - Implementado
4. 🧪 **Teste Completo** - Em andamento
5. 📊 **Monitoramento** - Configurar

## 📞 Suporte

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Redis Cloud**: [redis.com/docs](https://redis.com/docs)
- **Projeto**: suporte@hype.com.br 