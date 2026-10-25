# -*- coding: utf-8 -*-
"""
Script tự động đóng gói ứng dụng Đếm Tôm Thông Minh thành 1 file .EXE duy nhất bằng PyInstaller
"""

import os
import sys
import subprocess
import shutil

if sys.stdout and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def build_single_exe():
    print("=====================================================================")
    print("=== BẮT ĐẦU ĐÓNG GÓI ỨNG DỤNG THÀNH 1 FILE .EXE DUY NHẤT (PYINSTALLER) ===")
    print("=====================================================================")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_py = os.path.join(base_dir, "app.py")
    tts_cache_dir = os.path.join(base_dir, "tts_cache")
    dist_dir = os.path.join(base_dir, "dist")
    build_dir = os.path.join(base_dir, "build")

    exe_name = "ShrimpSmartCounter"

    # Kiểm tra PyInstaller
    try:
        import PyInstaller
        print(f"  -> Đã tìm thấy PyInstaller phiên bản: {PyInstaller.__version__}")
    except ImportError:
        print("  ❌ Chưa cài đặt PyInstaller! Đang cài đặt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Xây dựng danh sách datas
    datas = []
    if os.path.exists(tts_cache_dir):
        datas.append(f"{tts_cache_dir};tts_cache")

    # Danh sách hidden imports quan trọng
    hidden_imports = [
        "openpyxl",
        "openpyxl.styles",
        "openpyxl.utils",
        "speech_recognition",
        "gtts",
        "av",
        "av.filter",
        "numpy",
        "sounddevice",
        "win32com",
        "win32com.client",
        "pyttsx3",
        "pyttsx3.drivers",
        "pyttsx3.drivers.sapi5",
        "ctypes",
        "wave",
        "tkinter",
        "tkinter.ttk",
    ]

    # Danh sách các module nặng không sử dụng (Loại trừ để file EXE siêu nhẹ và build cực nhanh)
    excludes = [
        "torch",
        "torchaudio",
        "torchvision",
        "tensorflow",
        "scipy",
        "pandas",
        "matplotlib",
        "gradio",
        "sympy",
        "whisper",
        "openai-whisper",
        "cv2",
        "PIL",
        "IPython",
        "jupyter",
        "networkx",
        "pytest",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",              # Đóng gói thành 1 file .EXE duy nhất
        "--windowed",             # Không hiện cửa sổ dòng lệnh đen (GUI Mode)
        f"--name={exe_name}",
        f"--distpath={dist_dir}",
        f"--workpath={build_dir}",
    ]

    # Thêm datas
    for d in datas:
        cmd.append(f"--add-data={d}")

    # Thêm hidden imports
    for h in hidden_imports:
        cmd.append(f"--hidden-import={h}")

    # Thêm excludes
    for ex in excludes:
        cmd.append(f"--exclude-module={ex}")

    # File script chính
    cmd.append(app_py)

    print("\n  -> Đang thực thi lệnh đóng gói:")
    print("     " + " ".join(cmd[:10]) + " ...")

    ret = subprocess.call(cmd)

    if ret == 0:
        final_exe = os.path.join(dist_dir, f"{exe_name}.exe")
        print("\n=====================================================================")
        print("🎉 ĐÓNG GÓI THÀNH CÔNG RỰC RỠ!")
        print(f"👉 File .EXE đã hoàn thành tại: {final_exe}")
        if os.path.exists(final_exe):
            size_mb = os.path.getsize(final_exe) / (1024 * 1024)
            print(f"📦 Dung lượng file: {size_mb:.2f} MB")
        print("=====================================================================")
        return True
    else:
        print(f"\n❌ Đóng gói thất bại với mã lỗi: {ret}")
        return False

if __name__ == '__main__':
    build_single_exe()
