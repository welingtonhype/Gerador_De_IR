@echo off
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║          🚀 DEPLOY RÁPIDO COM NGROK                     ║
echo ║             Exposição instantânea para internet         ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Baixar ngrok se não existir
if not exist "ngrok.exe" (
    echo 📥 Baixando ngrok...
    powershell -Command "Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'"
    powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force"
    del ngrok.zip
    ngrok.exe config add-authtoken 30gnNeg3NvO7qe9CK75SPP1LJUc_7TcjWADDBMv5Y9rauKnwh
)

echo ✅ ngrok configurado!
echo.

REM Verificar se servidor está rodando
netstat -an | findstr ":5000" >nul
if errorlevel 1 (
    echo 🚀 Iniciando servidor...
    start /B python server.py
    echo ⏳ Aguardando servidor iniciar...
    timeout /t 5 /nobreak >nul
)

echo ✅ Servidor rodando!
echo.
echo 🌐 Expondo para internet...
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                  🎉 SISTEMA ONLINE!                     ║
echo ║          Aguarde a URL aparecer abaixo...               ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

ngrok.exe http 5000