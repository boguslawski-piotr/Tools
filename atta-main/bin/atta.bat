@set ATTA_HOME=%~dp0..
@call python "%ATTA_HOME%\main.py" %*
@exit /B %ERRORLEVEL% 
