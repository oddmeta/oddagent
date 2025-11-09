@echo off

REM 检查是否存在Python虚拟环境
if exist venv (    
    echo 激活Python虚拟环境...
    call venv\Scripts\activate
) else (
    echo Python虚拟环境不存在，使用系统Python...
)

REM 安装依赖（如果需要）
if exist requirements.txt (
    echo 安装项目依赖...
    pip install -r requirements.txt
)

REM 启动Flask应用
echo 启动OddAgent服务...
python app.py

pause