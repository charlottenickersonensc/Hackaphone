@echo off
cd /d "%~dp0"

start "" "Visualisations/Hallucination.pyw"
start "" "Programmes/Instrument Manette Bluetooth.pyw"

:: Pause légère pour laisser le temps à la deuxième fenêtre de s’ouvrir
timeout /t 2 >nul