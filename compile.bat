python compile.py build_ext --inplace

@REM REM 清理Cython临时文件
@REM REM 删除生成的.c文件
@REM del /s /q *.c 2>nul
@REM del /s /q *.pyd 2>nul

@REM REM 清理__pycache__目录
@REM for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

@REM REM 清理临时构建文件，包括.c文件和.pyd文件
@REM del /s /q logic\*.pyd 2>nul
@REM del /s /q tools\*.pyd 2>nul
@REM del /s /q router\*.pyd 2>nul
@REM del /s /q modules\*.pyd 2>nul
@REM del /s /q docs\*.pyd 2>nul

@REM del /s /q logic\*.c 2>nul
@REM del /s /q tools\*.c 2>nul
@REM del /s /q router\*.c 2>nul
@REM del /s /q modules\*.c 2>nul
@REM del /s /q docs\*.c 2>nul

@REM echo 清理完成！
