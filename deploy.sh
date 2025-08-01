#!/bin/bash

# Script de Deploy para Produção - Gerador de IR
# Hype Empreendimentos

set -e  # Parar em caso de erro

echo "🚀 DEPLOY PARA PRODUÇÃO - GERADOR DE IR"
echo "========================================"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

print_status "Docker e Docker Compose encontrados"

# Parar containers existentes
print_status "Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down

# Fazer backup dos PDFs gerados (se existirem)
if [ -d "generated_pdfs" ]; then
    print_status "Fazendo backup dos PDFs gerados..."
    cp -r generated_pdfs generated_pdfs_backup_$(date +%Y%m%d_%H%M%S)
fi

# Build da imagem
print_status "Construindo imagem Docker..."
docker build -t gerador-ir:latest .

# Iniciar serviços
print_status "Iniciando serviços em produção..."
docker-compose -f docker-compose.prod.yml up -d

# Aguardar containers iniciarem
print_status "Aguardando containers iniciarem..."
sleep 10

# Verificar se os containers estão rodando
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_status "Containers iniciados com sucesso!"
    echo ""
    echo "🌐 Aplicação disponível em:"
    echo "   HTTP:  http://localhost"
    echo "   HTTPS: https://localhost (após configurar SSL)"
    echo ""
    echo "📊 Para monitorar os logs:"
    echo "   docker-compose -f docker-compose.prod.yml logs -f"
    echo ""
    echo "🛑 Para parar os serviços:"
    echo "   docker-compose -f docker-compose.prod.yml down"
else
    print_error "Falha ao iniciar containers. Verificando logs..."
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

# Limpeza de imagens antigas
print_status "Limpando imagens Docker antigas..."
docker image prune -f

print_status "Deploy concluído com sucesso! 🎉"