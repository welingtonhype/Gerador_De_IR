@echo off
title SERVIDOR IMORTAL - Gerador IR
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║              🛡️ SERVIDOR IMORTAL                        ║
echo ║          Restart automático em caso de falha            ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:LOOP_SERVIDOR
echo ⏰ %date% %time% - 🚀 Iniciando servidor Flask na porta 5000...
python server.py

echo.
echo ⏰ %date% %time% - ❌ Servidor parou! Reiniciando em 5 segundos...
echo ⏰ Aguardando para restart automático...
timeout /t 5 /nobreak >nul

echo ⏰ %date% %time% - 🔄 Reiniciando servidor...
echo.
goto LOOP_SERVIDOR