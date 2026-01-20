@echo off

REM 确保我们在正确的目录
cd /d %~dp0

REM 激活虚拟环境（如果存在）
if exist .venv\Scripts\activate (
    echo activate virtual environment...
    call .venv\Scripts\activate
)

REM 执行编译脚本
echo compiling OddAgent MCP...
python compile.py build_ext --inplace

echo compiling complete

pause