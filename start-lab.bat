@echo off
echo Starting Novel Reading Platform...
docker compose up -d --build
echo Waiting for services to be healthy...
timeout /t 30 /nobreak >nul
echo All services started!
echo Frontend: http://localhost
echo Backend API: http://localhost/api
echo Grafana: http://localhost:3000
