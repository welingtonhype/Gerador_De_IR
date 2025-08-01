@echo off
title STATUS SISTEMA - Gerador IR
color 0D
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              📊 STATUS DO SISTEMA                       ║
echo ║                  Gerador IR - Hype                      ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo ⏰ Data/Hora: %date% %time%
echo.

:: Verificar servidor Flask
echo 🔍 Verificando Servidor Flask...
netstat -an | findstr ":5000" | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo ✅ Servidor Flask ONLINE na porta 5000
) else (
    echo ❌ Servidor Flask OFFLINE
)

:: Verificar ngrok
echo.
echo 🔍 Verificando ngrok...
tasklist | findstr "ngrok.exe" >nul
if not errorlevel 1 (
    echo ✅ ngrok ONLINE e rodando
    echo 📋 Processos ngrok:
    tasklist | findstr "ngrok.exe"
) else (
    echo ❌ ngrok OFFLINE
)

:: Verificar processos Python
echo.
echo 🔍 Verificando processos Python...
tasklist | findstr "python.exe" >nul
if not errorlevel 1 (
    echo ✅ Processos Python encontrados:
    tasklist | findstr "python.exe"
) else (
    echo ❌ Nenhum processo Python rodando
)

:: Verificar scripts imortais
echo.
echo 🔍 Verificando scripts de proteção...
tasklist | findstr "cmd.exe" | findstr /i "servidor-imortal\|ngrok-imortal\|monitor-sistema" >nul 2>nul
if not errorlevel 1 (
    echo ✅ Scripts de proteção ativos
) else (
    echo ❌ Scripts de proteção não encontrados
)

:: Verificar conectividade local
echo.
echo 🔍 Testando conectividade local...
curl -s http://localhost:5000/api/health >nul 2>nul
if not errorlevel 1 (
    echo ✅ API local respondendo corretamente
) else (
    echo ❌ API local não está respondendo
)

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                     📋 RESUMO                           ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 💡 Para ver URL pública do ngrok:
echo    - Abra a janela "ngrok Imortal"
echo    - Procure por "Forwarding: https://...ngrok-free.app"
echo.
echo 🛠️ Ações disponíveis:
echo    🚀 INICIAR-SISTEMA.bat  - Inicia sistema completo
echo    🛑 PARAR-SISTEMA.bat    - Para sistema completo  
echo    📊 STATUS-SISTEMA.bat   - Verifica status (este arquivo)
echo.
pause