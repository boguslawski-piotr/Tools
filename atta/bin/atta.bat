@set ATTA_HOME=%~dp0..
@call python -3 "%ATTA_HOME%\main.py" %*
@exit /B %ERRORLEVEL% 
