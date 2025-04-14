@echo off
cd /d "%~dp0"

start "" "Visualiseurs/Hallucination.pyw"
start "" "Programmes/Instrument iPhone.pyw"

:: Pause légère pour laisser le temps à la deuxième fenêtre de s’ouvrir
timeout /t 2 >nul