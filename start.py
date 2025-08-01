#!/usr/bin/env python3
"""
Script de inicialização do Gerador de IR
Verifica dependências e inicia o servidor
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        print("❌ Erro: Python 3.8 ou superior é necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} - OK")
    return True

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    required_packages = [
        'flask',
        'flask_cors', 
        'openpyxl',
        'reportlab',
        'PIL'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANDO")
    
    if missing_packages:
        print(f"\n📦 Instalando dependências faltantes...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ])
            print("✅ Dependências instaladas com sucesso!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências")
            return False
    
    return True

def check_files():
    """Verifica se os arquivos necessários estão presentes"""
    required_files = [
        'IR 2024 - NÃO ALTERAR.xlsx',
        'Scripts/gerador_ir_refatorado.py',
        'Imagens/Imagem1.png',
        'Imagens/Imagem2.png'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} - OK")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - FALTANDO")
    
    if missing_files:
        print(f"\n⚠️  Arquivos faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n💡 Certifique-se de que todos os arquivos estão no local correto")
        return False
    
    return True

def start_server():
    """Inicia o servidor Flask"""
    print("\n🚀 Iniciando servidor...")
    print("=" * 50)
    
    try:
        # Importar e executar o servidor
        from server import app
        
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        print(f"🌐 Servidor rodando em: http://localhost:{port}")
        print(f"📱 Acesse no navegador para usar o sistema")
        print(f"🛑 Pressione Ctrl+C para parar o servidor")
        print("=" * 50)
        
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False
    
    return True

def main():
    """Função principal"""
    print("🏢 GERADOR DE IR - HYPE EMPREENDIMENTOS")
    print("=" * 50)
    print("🔍 Verificando sistema...")
    print()
    
    # Verificar versão do Python
    if not check_python_version():
        return False
    
    print()
    
    # Verificar dependências
    if not check_dependencies():
        return False
    
    print()
    
    # Verificar arquivos
    if not check_files():
        print("\n❌ Verificação falhou. Corrija os problemas acima e tente novamente.")
        return False
    
    print()
    print("✅ Todas as verificações passaram!")
    
    # Iniciar servidor
    return start_server()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 