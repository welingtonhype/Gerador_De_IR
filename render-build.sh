#!/bin/bash

# Script de build para Render
echo "🚀 Iniciando build no Render..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p logs
mkdir -p generated_pdfs

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

echo "✅ Build concluído com sucesso!" 