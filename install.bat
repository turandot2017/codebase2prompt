@echo off
echo =====================================
echo  安装 CodebaseToPrompt 依赖
echo =====================================
echo.

echo 正在安装所需的 Python 包...
echo.

pip install -r requirements.txt

echo.
echo =====================================
echo  安装完成！
echo =====================================
echo.
echo 现在可以运行程序：
echo   python main.py
echo.
echo 或运行测试脚本：
echo   python test_json_repair.py
echo.
pause

