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

exit