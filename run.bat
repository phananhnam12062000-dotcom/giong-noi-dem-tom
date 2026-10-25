@echo off
chcp 65001 > nul
title HỆ THỐNG QUẢN LÝ VÀ ĐẾM TÔM THÔNG MINH (GOOGLE SPEECH RECOGNITION)
color 0B

echo ===============================================================================
echo   🦐 HỆ THỐNG QUẢN LÝ VÀ ĐẾM SỐ LƯỢNG TÔM THÔNG MINH BẰNG GIỌNG NÓI TIẾNG VIỆT
echo   🌐 Google Speech Recognition Trực Tuyến - Siêu Mượt, Nhẹ CPU, Chuẩn Xác Cao
echo ===============================================================================
echo.

:: 1. Kiểm tra Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [LỖI] Không tìm thấy Python trong hệ thống!
    echo Vui lòng cài đặt Python (phiên bản 3.10 trở lên) và tích chọn "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: 2. Kiểm tra và tự động cài đặt thư viện nếu thiếu
echo [1/2] Đang kiểm tra môi trường và thư viện...
python -c "import speech_recognition, openpyxl, pyaudio, gtts" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [THÔNG BÁO] Đang cài đặt thư viện cần thiết (SpeechRecognition, openpyxl, pyaudio, gtts, pyttsx3)...
    python -m pip install -r requirements.txt
)

:: 3. Khởi động phần mềm chính
echo [2/2] Đang khởi động giao diện phần mềm Đếm Tôm Thông Minh...
echo.
python app.py

:: 4. Bắt lỗi khi thoát
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ===============================================================================
    echo [LỖI] Phần mềm đã dừng lại với mã lỗi %ERRORLEVEL%.
    echo Vui lòng kiểm tra lại thông báo lỗi ở trên!
    echo ===============================================================================
    echo.
    pause
)
