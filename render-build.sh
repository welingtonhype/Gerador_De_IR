#!/bin/bash

# Script de build para Render
echo "🚀 Iniciando build no Render..."

# Atualizar sistema e instalar dependências do sistema
echo "📦 Atualizando sistema..."
apt-get update -qq
apt-get install -y -qq \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libxrandr-dev \
    liblcms2-dev \
    libtiff5-dev \
    zlib1g-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev

# Instalar dependências Python
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p logs
mkdir -p generated_pdfs

# Definir permissões adequadas
echo "🔐 Configurando permissões..."
chmod 755 render-build.sh
chmod -R 755 Scripts/
chmod -R 755 Imagens/

# Verificar arquivos essenciais
echo "🔍 Verificando arquivos essenciais..."
if [ ! -f "IR 2024 - NÃO ALTERAR.xlsx" ]; then
    echo "❌ Arquivo Excel não encontrado"
    exit 1
fi

if [ ! -f "Scripts/gerador_ir_refatorado.py" ]; then
    echo "❌ Script do gerador não encontrado"
    exit 1
fi

if [ ! -f "Imagens/Imagem1.png" ] || [ ! -f "Imagens/Imagem2.png" ]; then
    echo "❌ Imagens não encontradas"
    exit 1
fi

# Testar importação dos módulos
echo "🧪 Testando importações..."
python -c "from Scripts.gerador_ir_refatorado import buscar_cliente_por_cpf; print('✅ Módulos importados com sucesso')"

echo "✅ Build concluído com sucesso!" 