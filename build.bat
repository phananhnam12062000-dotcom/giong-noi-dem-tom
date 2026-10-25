@echo off
chcp 65001 >nul
title Đóng gói Ứng dụng Đếm Tôm Thông Minh thành File .EXE

echo =====================================================================
echo    HỆ THỐNG QUẢN LÝ & ĐẾM TÔM THÔNG MINH BẰNG GIỌNG NÓI TIẾNG VIỆT
echo    CÔNG CỤ ĐÓNG GÓI ỨNG DỤNG THÀNH 1 FILE .EXE DUY NHẤT (PYINSTALLER)
echo =====================================================================
echo.

cd /d "%~dp0"

echo [1/3] Kiểm tra môi trường Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LỖI] Không tìm thấy Python trên máy tính! Vui lòng cài đặt Python 3.10 trở lên.
    pause
    exit /b 1
)

echo [2/3] Kiểm tra thư viện PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Đang tự động cài đặt PyInstaller...
    pip install pyinstaller
)

echo [3/3] Đang tiến hành đóng gói toàn bộ dự án thành file .EXE duy nhất...
python build_exe.py

echo.
if %errorlevel% equ 0 (
    echo =====================================================================
    echo    ĐÓNG GÓI HOÀN TẤT!
    echo    File ShrimpSmartCounter.exe nằm trong thư mục: dist\
    echo =====================================================================
    explorer dist
) else (
    echo [LỖI] Quá trình đóng gói gặp lỗi! Vui lòng kiểm tra lại.
)

pause
