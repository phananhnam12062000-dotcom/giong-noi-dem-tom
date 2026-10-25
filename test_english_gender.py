# -*- coding: utf-8 -*-
"""
Test script for English gender recognition in Mode 1 (Chế độ 1):
1. "male", "mail", "meo", "mê", "mel" -> "Đực"
2. "female", "phi meo", "pheme", "femail", "phi" -> "Cái"
3. Traditional: "đực" -> "Đực", "cái" -> "Cái", neither -> "Chưa rõ"
"""

import sys
if sys.stdout and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app import ShrimpSmartCounterApp, detect_shrimp_gender_mode1, is_relevant_shrimp_command
from vietnamese_parser import parse_mode1_weighing_and_gender

def test_english_gender_keywords():
    print("=====================================================================")
    print("=== KIỂM THỬ TỪ KHÓA GIỚI TÍNH TIẾNG ANH CHO TÔM Ở CHẾ ĐỘ 1 ===")
    print("=====================================================================")

    # 1. Kiểm thử hàm detect_shrimp_gender_mode1
    male_test_cases = [
        ("male", "Đực"),
        ("mail", "Đực"),
        ("meo", "Đực"),
        ("mê", "Đực"),
        ("mel", "Đực"),
        ("35 male", "Đực"),
        ("40 mail", "Đực"),
        ("52 meo", "Đực"),
        ("28 mê", "Đực"),
        ("33 mel", "Đực"),
        ("ba lăm male", "Đực"),
        ("năm hai meo", "Đực"),
        ("bốn lăm mail", "Đực"),
    ]

    print("\n[TEST 1] Kiểm tra từ khóa Giới tính Đực (male, mail, meo, mê, mel):")
    for text, expected in male_test_cases:
        gender = detect_shrimp_gender_mode1(text)
        print(f"  -> '{text}' => Giới tính: {gender} (Mong đợi: {expected})")
        assert gender == expected, f"Thất bại: '{text}' trả về '{gender}', mong đợi '{expected}'"

    female_test_cases = [
        ("female", "Cái"),
        ("phi meo", "Cái"),
        ("pheme", "Cái"),
        ("femail", "Cái"),
        ("phi", "Cái"),
        ("45 female", "Cái"),
        ("30 phi meo", "Cái"),
        ("25 pheme", "Cái"),
        ("50 femail", "Cái"),
        ("38 phi", "Cái"),
        ("bốn lăm female", "Cái"),
        ("ba lăm phi meo", "Cái"),
        ("hai lăm pheme", "Cái"),
    ]

    print("\n[TEST 2] Kiểm tra từ khóa Giới tính Cái (female, phi meo, pheme, femail, phi):")
    for text, expected in female_test_cases:
        gender = detect_shrimp_gender_mode1(text)
        print(f"  -> '{text}' => Giới tính: {gender} (Mong đợi: {expected})")
        assert gender == expected, f"Thất bại: '{text}' trả về '{gender}', mong đợi '{expected}'"

    unspecified_test_cases = [
        ("35", "Chưa rõ"),
        ("ba mươi lăm", "Chưa rõ"),
        ("45 gram", "Chưa rõ"),
        ("hai lăm phẩy năm", "Chưa rõ"),
    ]

    print("\n[TEST 3] Kiểm tra khi không có từ khóa giới tính (Mặc định 'Chưa rõ'):")
    for text, expected in unspecified_test_cases:
        gender = detect_shrimp_gender_mode1(text)
        print(f"  -> '{text}' => Giới tính: {gender} (Mong đợi: {expected})")
        assert gender == expected, f"Thất bại: '{text}' trả về '{gender}', mong đợi '{expected}'"

    # 2. Kiểm thử tích hợp hàm _handle_mode1_speech trong app
    print("\n[TEST 4] Kiểm thử tích hợp Chế độ 1 trong giao diện ứng dụng:")
    app = ShrimpSmartCounterApp()
    app.withdraw()
    app.notebook.select(0)
    app.tts.enabled = False  # Tắt phát âm để test nhanh

    full_samples = [
        ("35 male", 35.0, "Đực"),
        ("45 female", 45.0, "Cái"),
        ("30 mail", 30.0, "Đực"),
        ("25 phi meo", 25.0, "Cái"),
        ("52 meo", 52.0, "Đực"),
        ("40 pheme", 40.0, "Cái"),
        ("28 mê", 28.0, "Đực"),
        ("33 femail", 33.0, "Cái"),
        ("38 mel", 38.0, "Đực"),
        ("42 phi", 42.0, "Cái"),
        ("35 đực", 35.0, "Đực"),
        ("45 cái", 45.0, "Cái"),
        ("50", 50.0, "Chưa rõ"),
    ]

    for speech, exp_weight, exp_gender in full_samples:
        app._handle_mode1_speech(speech)
        last_rec = app.weight_records[-1]
        print(f"  -> Speech: '{speech}' => Lưu: {last_rec['weight']}g - {last_rec['gender']}")
        assert last_rec['weight'] == exp_weight, f"Sai trọng lượng: {last_rec['weight']} != {exp_weight}"
        assert last_rec['gender'] == exp_gender, f"Sai giới tính: {last_rec['gender']} != {exp_gender}"

    tree_items = app.tree_weight.get_children()
    assert len(tree_items) == len(full_samples), f"Bảng Treeview thiếu dòng: {len(tree_items)}"
    print(f"  => Bảng Treeview đã hiển thị đầy đủ {len(tree_items)} dòng mẫu cân!")

    app.destroy()
    print("\n=====================================================================")
    print("=== TẤT CẢ TỪ KHÓA GIỚI TÍNH TIẾNG ANH ĐÃ ĐƯỢC KIỂM THỬ PASS 100%! ===")
    print("=====================================================================")

if __name__ == '__main__':
    test_english_gender_keywords()
