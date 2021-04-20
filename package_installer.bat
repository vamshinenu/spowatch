@echo off

:start
cls

set python_ver=36

python ./get-pip.py

cd \

cd \python%python_ver%\Scripts\
pip install win32gui
cd \

cd \python%python_ver%\Scripts\
pip install pywin32
cd \

cd \python%python_ver%\Scripts\
pip install psutil
cd \

@REM cd \python%python_ver%\Scripts\
@REM pip install pynput
@REM cd \

cd \python%python_ver%\Scripts\
pip install asyncio
cd \

cd \python%python_ver%\Scripts\
pip install winrt
cd \

exit