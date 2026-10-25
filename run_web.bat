@echo off
chcp 65001 >nul
title Smart Shrimp Counter - Web App Responsive

echo ============================================================
echo   🦐 SMART SHRIMP COUNTER - PHẦN MỀM ĐẾM TÔM WEB APP
echo   Hỗ trợ Micro Trình Duyệt Điện Thoại (iOS & Android)
echo ============================================================
echo.
echo Đang khởi động máy chủ Web...
echo Bạn có thể mở trên máy tính tại: http://localhost:7860
echo Và quét mã QR hoặc mở link HTTPS (xxxx.gradio.live) trên điện thoại!
echo.

python web_app.py

pause
