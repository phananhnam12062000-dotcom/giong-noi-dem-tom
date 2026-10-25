# -*- coding: utf-8 -*-
import os
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def test_web_logic():
    from web_app import (
        detect_shrimp_gender,
        parse_weight_value,
        parse_accumulate_batch,
        export_excel_report,
        create_shrimp_app,
        generate_tts_feedback_audio
    )

    print("--- 1. Kiểm tra nhận diện giới tính ---")
    assert detect_shrimp_gender("45 gram đực") == "Male"
    assert detect_shrimp_gender("35 chai") == "Male"
    assert detect_shrimp_gender("50 trai") == "Male"
    assert detect_shrimp_gender("40 tai") == "Male"
    assert detect_shrimp_gender("30 cái") == "Female"
    assert detect_shrimp_gender("35 gái") == "Female"
    assert detect_shrimp_gender("28 ái") == "Female"
    assert detect_shrimp_gender("55 male") == "Male"
    assert detect_shrimp_gender("60 female") == "Female"
    assert detect_shrimp_gender("chỉ có số 50") == "Chưa rõ"
    print("PASS: Nhận diện giới tính chính xác 100%!")

    print("--- 2. Kiểm tra bóc tách trọng lượng ---")
    assert parse_weight_value("45 gram") == 45.0
    assert parse_weight_value("42.5 g") == 42.5
    assert parse_weight_value("ba mươi lăm") == 35.0
    assert parse_weight_value("năm mươi gram") == 50.0
    print("PASS: Bóc tách trọng lượng chính xác 100%!")

    print("--- 3. Kiểm tra Chế độ 2 đếm cộng dồn ---")
    assert parse_accumulate_batch("năm") == ('ADD', 5)
    assert parse_accumulate_batch("mười") == ('ADD', 10)
    assert parse_accumulate_batch("mười lăm") == ('ADD', 15)
    assert parse_accumulate_batch("hai mươi lăm") == ('ADD', 25)
    assert parse_accumulate_batch("xóa") == ('UNDO', None)
    assert parse_accumulate_batch("hủy") == ('UNDO', None)
    assert parse_accumulate_batch("xóa hết") == ('RESET', None)
    assert parse_accumulate_batch("reset") == ('RESET', None)
    print("PASS: Logic Chế độ 2 chính xác 100%!")

    print("--- 4. Kiểm tra xuất Excel ---")
    dummy_m1 = [
        {"stt": 1, "gender": "Male", "weight": 45.0, "time": "10:00:00"},
        {"stt": 2, "gender": "Female", "weight": 55.0, "time": "10:01:00"}
    ]
    dummy_m2 = [
        {"stt": 1, "batch": 10, "total": 10, "time": "10:05:00"},
        {"stt": 2, "batch": 15, "total": 25, "time": "10:06:00"}
    ]
    excel_path = export_excel_report("Ao Test", "Kỹ sư A", dummy_m1, dummy_m2)
    assert os.path.exists(excel_path)
    assert os.path.getsize(excel_path) > 1000
    print(f"PASS: Xuất Excel thành công: {excel_path} ({os.path.getsize(excel_path)} bytes)")

    print("--- 5. Kiểm tra khởi tạo Gradio Blocks ---")
    demo = create_shrimp_app()
    assert demo is not None
    print("PASS: Khởi tạo Gradio App Responsive thành công!")

if __name__ == "__main__":
    test_web_logic()
    print("\n>>> TẤT CẢ CÁC BÀI TEST WEB ĐỀU ĐẠT 100% <<<")
