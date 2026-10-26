# -*- coding: utf-8 -*-
"""
=============================================================================
SCRIPT TRIỂN KHAI TỰ ĐỘNG LÊN HUGGING FACE SPACES
Tác giả: Antigravity AI
Chức năng: Đưa toàn bộ thư mục hf_space lên Hugging Face Spaces để lấy đường
link trang web vĩnh viễn, bảo mật HTTPS chạy trên mọi điện thoại di động.
=============================================================================
"""

import os
import sys
import argparse

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def deploy():
    parser = argparse.ArgumentParser(description="Triển khai Smart Shrimp Counter lên Hugging Face Spaces")
    parser.add_argument("--token", type=str, help="Hugging Face Access Token (loại WRITE)")
    parser.add_argument("--space", type=str, help="Tên Space (VD: 'dem-tom-thong-minh' hoặc 'username/dem-tom-thong-minh')")
    parser.add_argument("--private", action="store_true", help="Đặt Space ở chế độ riêng tư (Private)")
    args = parser.parse_args()

    print("=" * 65)
    print("🚀 BẮT ĐẦU TRIỂN KHAI LÊN HUGGING FACE SPACES")
    print("=" * 65)

    try:
        from huggingface_hub import HfApi, get_token, whoami
    except ImportError:
        print("❌ Lỗi: Thư viện huggingface_hub chưa được cài đặt.")
        print("Vui lòng chạy lệnh: pip install huggingface_hub")
        return

    # 1. Lấy Token
    token = args.token or get_token()
    if not token:
        print("\n🔑 BẠN CHƯA CUNG CẤP HUGGING FACE TOKEN.")
        print("Hướng dẫn lấy token:")
        print("  1. Đăng nhập https://huggingface.co/settings/tokens")
        print("  2. Bấm 'Create new token' -> Chọn quyền 'WRITE'")
        print("  3. Sao chép mã token (bắt đầu bằng hf_...)")
        try:
            token = input("\n👉 Nhập Token Hugging Face của bạn: ").strip()
        except EOFError:
            token = ""

    if not token:
        print("❌ Lỗi: Không có Token xác thực. Hủy thao tác.")
        return

    api = HfApi(token=token)

    # 2. Xác thực tài khoản
    try:
        user_info = whoami(token=token)
        username = user_info.get("name", "")
        print(f"✅ Xác thực tài khoản thành công: @{username}")
    except Exception as e:
        print(f"❌ Lỗi xác thực Token: {e}")
        return

    # 3. Xác định tên Space ID
    space_name = args.space
    if not space_name:
        try:
            space_name = input("👉 Nhập tên Space muốn đặt (Mặc định: 'dem-tom-thong-minh'): ").strip()
        except EOFError:
            space_name = ""
        if not space_name:
            space_name = "dem-tom-thong-minh"

    if "/" in space_name:
        full_space_id = space_name
    else:
        full_space_id = f"{username}/{space_name}"

    # 4. Kiểm tra thư mục nguồn
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_folder = os.path.join(base_dir, "hf_space")

    if not os.path.exists(source_folder) or not os.path.exists(os.path.join(source_folder, "app.py")):
        print(f"❌ Không tìm thấy thư mục hf_space hợp lệ tại: {source_folder}")
        return

    # 5. Tạo Space trên Hugging Face
    print(f"\n📦 Đang khởi tạo Space: {full_space_id}...")
    try:
        api.create_repo(
            repo_id=full_space_id,
            repo_type="space",
            space_sdk="gradio",
            private=args.private,
            exist_ok=True
        )
        print(f"✅ Space đã sẵn sàng trên Hugging Face!")
    except Exception as e:
        print(f"⚠️ Chú ý khi tạo repo: {e}")

    # 6. Tải toàn bộ mã nguồn lên Space
    print(f"📤 Đang đồng bộ và tải toàn bộ mã nguồn lên Space (Có thể mất 15-40 giây)...")
    try:
        api.upload_folder(
            folder_path=source_folder,
            repo_id=full_space_id,
            repo_type="space",
            commit_message="Deploy Smart Shrimp Counter Web App with mobile mic support"
        )
        print("✅ Tải dữ liệu lên Hugging Face Space thành công 100%!")
    except Exception as e:
        print(f"❌ Lỗi khi tải thư mục: {e}")
        return

    # 7. Hiển thị đường link vĩnh viễn
    repo_pure_name = full_space_id.split("/")[-1].replace("_", "-")
    author_pure_name = username.replace("_", "-")
    direct_subdomain_url = f"https://{author_pure_name}-{repo_pure_name}.hf.space"
    space_page_url = f"https://huggingface.co/spaces/{full_space_id}"

    print("\n" + "=" * 65)
    print("🎉 CHÚC MỪNG BẠN! ỨNG DỤNG ĐÃ ĐƯỢC TRIỂN KHAI THÀNH CÔNG!")
    print("=" * 65)
    print(f"🌐 1. Link trang Space chính thức: {space_page_url}")
    print(f"📱 2. Link trực tiếp toàn màn hình (Dùng cho điện thoại):")
    print(f"   👉 {direct_subdomain_url}")
    print("\n💡 GHI CHÚ QUAN TRỌNG:")
    print("- Link trên là VĨNH VIỄN, miễn phí 24/7 và có HTTPS bảo mật tuyệt đối.")
    print("- Trình duyệt điện thoại (Safari / Chrome) sẽ cho phép bật Micro ngay lập tức.")
    print("- Hugging Face đang tiến hành build container trong khoảng 1-2 phút đầu tiên.")
    print("=" * 65)

if __name__ == "__main__":
    deploy()
