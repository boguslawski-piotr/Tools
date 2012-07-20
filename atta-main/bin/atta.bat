@set ATTA_HOME=%~dp0..
@call python -OO "%ATTA_HOME%\main.py" %*
@exit /B %ERRORLEVEL% 
