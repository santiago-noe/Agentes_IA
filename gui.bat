@echo off
title Sistema de Agentes IA - Interfaz Grafica
color 0A

echo.
echo ========================================
echo 🤖 SISTEMA DE AGENTES DE IA
echo ========================================
echo 🎨 Iniciando interfaz grafica...
echo.

cd /d "%~dp0"

python launcher.py

echo.
echo 👋 Sistema cerrado. Presiona cualquier tecla para salir...
pause >nul