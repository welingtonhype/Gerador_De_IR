# Dockerfile para Produção - Gerador de IR
FROM python:3.9-slim

# Configurar timezone
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar gunicorn para produção
RUN pip install gunicorn==21.2.0

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p logs generated_pdfs && \
    chown -R app:app /app

# Mudar para usuário não-root
USER app

# Expor porta
EXPOSE 8000

# Variáveis de ambiente para produção
ENV FLASK_ENV=production
ENV DEBUG=False
ENV HOST=0.0.0.0
ENV PORT=8000

# Comando para iniciar em produção
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--max-requests", "1000", "--max-requests-jitter", "100", "server:app"]