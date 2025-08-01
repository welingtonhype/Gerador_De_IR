@echo off
title SISTEMA GERADOR IR - NEVER DOWN
color 0F
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║            🚀 SISTEMA COMPLETO - NEVER DOWN             ║
echo ║                  Gerador IR - Hype                      ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🧹 Limpando processos antigos...

:: Matar processos antigos gentilmente
taskkill /f /im python.exe 2>nul
taskkill /f /im ngrok.exe 2>nul

:: Aguardar limpeza completa
echo ⏳ Aguardando limpeza completa...
timeout /t 5 /nobreak >nul

echo.
echo 🚀 Iniciando sistema com proteção total...
echo.

:: 1. Iniciar servidor imortal (minimizado)
echo ⚡ Iniciando Servidor Imortal...
start /min "Servidor Imortal" servidor-imortal.bat

:: Aguardar servidor inicializar
echo ⏳ Aguardando servidor Flask inicializar...
timeout /t 8 /nobreak >nul

:: 2. Iniciar ngrok imortal (minimizado)  
echo 🌐 Iniciando ngrok Imortal...
start /min "ngrok Imortal" ngrok-imortal.bat

:: Aguardar ngrok inicializar
echo ⏳ Aguardando ngrok inicializar...
timeout /t 10 /nobreak >nul

:: 3. Iniciar monitor do sistema
echo 📊 Iniciando Monitor Inteligente...
start "Monitor Sistema" monitor-sistema.bat

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              ✅ SISTEMA INICIADO COM SUCESSO!           ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🛡️ Proteções ativas:
echo    ✅ Restart automático do servidor Flask
echo    ✅ Restart automático do ngrok
echo    ✅ Monitor inteligente (verificação a cada 30s)
echo    ✅ Logs detalhados com data/hora
echo.
echo 💡 COMO USAR:
echo    👀 Para ver a URL pública: Verifique janela "ngrok Imortal"
echo    📊 Para ver status: Verifique janela "Monitor Sistema"
echo    🛑 Para parar tudo: Execute "PARAR-SISTEMA.bat"
echo.
echo 🌐 O sistema está SEMPRE ONLINE agora!
echo.
pause