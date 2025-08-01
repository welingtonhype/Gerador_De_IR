@echo off
title NGROK IMORTAL - Gerador IR
color 0B
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              🌐 NGROK IMORTAL                           ║
echo ║         Tunnel sempre ativo para internet              ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:LOOP_NGROK
echo ⏰ %date% %time% - 🌐 Iniciando ngrok tunnel para porta 5000...
echo ⏰ Aguardando servidor estar pronto...
timeout /t 10 /nobreak >nul

.\ngrok.exe http 5000 --request-header-add="User-Agent:HypeIR/1.0"

echo.
echo ⏰ %date% %time% - ❌ ngrok parou! Reiniciando em 10 segundos...
echo ⏰ Aguardando para restart automático...
timeout /t 10 /nobreak >nul

echo ⏰ %date% %time% - 🔄 Reiniciando ngrok...
echo.
goto LOOP_NGROK