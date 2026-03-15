@echo off
cd /d "%~dp0"
echo.
echo === PostgreSQL setup for Employee Management ===
echo.
set /p PGPASS="Enter PostgreSQL password for user 'postgres': "
if "%PGPASS%"=="" (
  echo No password entered. Edit backend\.env and set DATABASE_URL with your password, then run create_db.py and seed.py.
  exit /b 1
)
set PGPASSWORD=%PGPASS%
call venv\Scripts\activate.bat 2>nul
echo Writing DATABASE_URL to .env...
python update_env_with_password.py
python create_db.py
if %ERRORLEVEL% neq 0 (
  echo Database creation failed. Check password and that PostgreSQL is running on port 5432.
  pause
  exit /b 1
)
echo Seeding tables and admin...
python seed.py
if %ERRORLEVEL% neq 0 (
  echo Seed failed.
  pause
  exit /b 1
)
echo.
echo === Done. Database ready. Run: python app.py ===
pause
