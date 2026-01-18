@echo off
title JetBank Server (Port 8001)
color 0A
cd /d "%~dp0"

echo ==================================================
echo      JETBANK FINANCIAL SYSTEMS - SERVER LAUNCH
echo ==================================================
echo.

:: 1. Check for Virtual Environment
if exist .venv goto :ACTIVATE

echo [SYSTEM] Criando ambiente virtual dedicado (.venv)...
python -m venv .venv
if %errorlevel% neq 0 goto :ERROR_VENV

:ACTIVATE
:: 2. Activate Environment
echo [SYSTEM] Ativando ambiente virtual...
call .venv\Scripts\activate

:: 3. Install Dependencies
echo.
echo [SYSTEM] Instalando bibliotecas (Isso pode levar alguns minutos)...
echo [SYSTEM] Por favor, AGUARDE e nao feche a janela.
echo.
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 goto :ERROR_PIP

:: 4. Run Migrations (Ensure DB is ready)
echo.
echo [SYSTEM] Criando migracoes (Recriando estrutura do banco)...
echo [SYSTEM] Criando migracoes (Recriando estrutura do banco)...
python manage.py makemigrations fintech
echo [SYSTEM] Sincronizando Banco de Dados...
python manage.py migrate --noinput
if %errorlevel% neq 0 goto :ERROR_DB

:: 5. Create Superuser (Auto-Admin)
echo [SYSTEM] Verificando usuario admin...
python scripts\create_superuser.py

:: 6. Start Server
echo.
echo ==================================================
echo [SUCCESS] SISTEMA OPERACIONAL
echo ==================================================
echo.
echo  * Mobile App Simulator: http://127.0.0.1:8001/fintech/app/
echo  * API Swagger Docs:     http://127.0.0.1:8001/fintech/api/docs/
echo.
echo Pressione CTRL+C para parar o servidor.
echo.

python manage.py runserver 8001
goto :END

:ERROR_VENV
echo.
echo [ERROR] Falha ao criar o ambiente virtual.
echo Verifique se o Python esta instalado e no PATH.
pause
exit /b

:ERROR_PIP
echo.
echo [ERROR] Falha na instalacao das bibliotecas.
echo Verifique sua conexao com a internet e tente novamente.
pause
exit /b

:ERROR_DB
echo.
echo [ERROR] Falha na migracao do banco de dados.
pause
exit /b

:END
pause
