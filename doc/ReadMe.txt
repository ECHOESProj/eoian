rem Path set's are quoted to account for spaces in the paths.

rem PYTHON_PATH should match the python version on your local machine.


set "PYTHON_PATH=C:\Python\Python39\python"
set "VIRTUALENV_PATH=D:\Python\VirtualEnvs\Echoes"
set "OUTPUT_PATH=C:\inetpub\wwwroot\EchoesSphinx"



rem VIRTUALENV_PATH should match the path to the python virtual environment on your local machine.


rem OUTPUT_PATH should match the IIS site you have created on your local machine, this can also just be a normal folder.
rem We may instead build to the _build folder which will be committed to the repo and used in CICD pipelines. If so use the following commented line.
rem set OUTPUT_PATH="%CURRENT_PATH%\docs\_build"

w12-iis\Inetpub\wwwroot\Echoes


\\W12-IIS\Inetpub\wwwroot\Echoes