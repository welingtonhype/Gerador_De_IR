@echo off
title PARAR SISTEMA - Gerador IR
color 0C
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              🛑 PARANDO SISTEMA COMPLETO                ║
echo ║                  Gerador IR - Hype                      ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

echo 🛑 Parando todos os processos do sistema...
echo.

:: Parar processos Python (servidor Flask)
echo ⚡ Parando servidor Flask...
taskkill /f /im python.exe 2>nul
if not errorlevel 1 (
    echo ✅ Servidor Flask parado
) else (
    echo ℹ️ Servidor Flask não estava rodando
)

:: Parar processos ngrok
echo 🌐 Parando ngrok...
taskkill /f /im ngrok.exe 2>nul
if not errorlevel 1 (
    echo ✅ ngrok parado
) else (
    echo ℹ️ ngrok não estava rodando
)

:: Fechar janelas dos scripts batch
echo 📊 Fechando janelas do sistema...
taskkill /f /fi "WindowTitle eq Servidor Imortal*" 2>nul
taskkill /f /fi "WindowTitle eq ngrok Imortal*" 2>nul  
taskkill /f /fi "WindowTitle eq Monitor Sistema*" 2>nul

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              ✅ SISTEMA PARADO COM SUCESSO!             ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🛑 Todos os processos foram parados:
echo    ❌ Servidor Flask
echo    ❌ ngrok
echo    ❌ Monitor do sistema
echo    ❌ Scripts de restart automático
echo.
echo 💡 Para iniciar novamente: Execute "INICIAR-SISTEMA.bat"
echo.
pause