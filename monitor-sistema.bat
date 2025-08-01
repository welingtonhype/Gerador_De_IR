@echo off
title MONITOR SISTEMA - Gerador IR
color 0E
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              📊 MONITOR INTELIGENTE                     ║
echo ║        Verificação automática a cada 30 segundos       ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:MONITOR_LOOP
echo ⏰ %date% %time% - 🔍 Verificando sistema...

:: Verificar se servidor Flask está rodando na porta 5000
netstat -an | findstr ":5000" | findstr "LISTENING" >nul
if errorlevel 1 (
    echo ❌ %time% - Servidor Flask offline na porta 5000!
    echo 🔄 Verificando se processo servidor-imortal está rodando...
    tasklist | findstr "servidor-imortal" >nul
    if errorlevel 1 (
        echo 🚀 Iniciando servidor-imortal.bat...
        start /min "Servidor Imortal" servidor-imortal.bat
        timeout /t 5 /nobreak >nul
    ) else (
        echo ✅ servidor-imortal já está rodando, aguardando reinicialização...
    )
) else (
    echo ✅ %time% - Servidor Flask OK na porta 5000
)

:: Verificar se ngrok está rodando  
tasklist | findstr "ngrok.exe" >nul
if errorlevel 1 (
    echo ❌ %time% - ngrok offline!
    echo 🔄 Verificando se processo ngrok-imortal está rodando...
    tasklist | findstr "ngrok-imortal" >nul
    if errorlevel 1 (
        echo 🌐 Iniciando ngrok-imortal.bat...
        start /min "ngrok Imortal" ngrok-imortal.bat
        timeout /t 5 /nobreak >nul
    ) else (
        echo ✅ ngrok-imortal já está rodando, aguardando reinicialização...
    )
) else (
    echo ✅ %time% - ngrok OK e rodando
)

echo ⏰ %time% - 💤 Próxima verificação em 30 segundos...
echo ----------------------------------------
timeout /t 30 /nobreak >nul
goto MONITOR_LOOP