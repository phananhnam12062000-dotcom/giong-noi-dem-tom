# -*- coding: utf-8 -*-
"""
Test script to rigorously verify all 3 operational bug fixes in app.py:
LỖI 1: Nhận diện các số từ 1 đến 10 ở Chế độ 2 ("một", "hai", "năm", "sáu", "tám", "mười", "chục"...)
LỖI 2: Hands-free check từ khóa "xóa" / "hủy" ("Xóa", "Hủy", "xóa hộ", "hủy mẻ này")
LỖI 3: Cơ chế khóa an toàn Debounce / Cooldown Lock chống Double Trigger
"""

import os
import sys
import time

if sys.stdout and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import app as app_module
from app import ShrimpSmartCounterApp

def test_operational_bugfixes():
    print("=====================================================================")
    print("=== BẮT ĐẦU KIỂM THỬ TRIỆT ĐỂ 3 LỖI VẬN HÀNH TRONG APP.PY ===")
    print("=====================================================================")

    counter_app = ShrimpSmartCounterApp()
    counter_app.withdraw()  # Chạy headless ẩn cửa sổ

    # Chọn Tab 2: Chế độ đếm số lượng cộng dồn
    counter_app.notebook.select(1)
    # Tắt tạm thời âm thanh loa ngoài để chạy test nhanh không delay
    counter_app.tts.enabled = False

    # -----------------------------------------------------------------
    # KIỂM THỬ LỖI 1: NHẬN DIỆN CÁC SỐ TỪ 1 ĐẾN 10 Ở CHẾ ĐỘ 2
    # -----------------------------------------------------------------
    print("\n--- [KIỂM THỬ LỖI 1] Nhận diện các số từ 1 đến 10 ở Chế độ 2 ---")
    counter_app._reset_total_shrimp_count()
    app_module.is_processing = False
    counter_app.is_processing = False

    test_numbers_1_to_10 = [
        ("một", 1),
        ("mốt", 1),
        ("hai", 2),
        ("ba", 3),
        ("bốn", 4),
        ("năm", 5),
        ("lăm", 5),
        ("sáu", 6),
        ("bảy", 7),
        ("tám", 8),
        ("chín", 9),
        ("mười", 10),
        ("chục", 10),
        ("thêm năm con", 5),
        ("mẻ sáu", 6),
        ("bốc tám con", 8)
    ]

    expected_running_total = 0
    for text_input, expected_val in test_numbers_1_to_10:
        # Reset lock thủ công trước mỗi lượt kiểm tra đơn lập logic
        app_module.is_processing = False
        counter_app.is_processing = False

        counter_app._handle_mode2_speech(text_input)
        expected_running_total += expected_val

        assert counter_app.total_batch_count == expected_running_total, (
            f"Lỗi: Đọc '{text_input}' mong đợi cộng +{expected_val} (Tổng {expected_running_total}), "
            f"nhưng thực tế tổng là {counter_app.total_batch_count}"
        )
        print(f"  -> Nhận diện '{text_input}' -> +{expected_val} con | Tổng tích lũy hiện tại: {counter_app.total_batch_count} con")

    print(f"  => LỖI 1 ĐÃ ĐƯỢC KHẮC PHỤC HOÀN TOÀN: 16/16 từ khóa số 1-10 nhận diện chính xác!")

    # -----------------------------------------------------------------
    # KIỂM THỬ LỖI 2: NHẬN DIỆN TỪ KHÓA "XÓA" HOẶC "HỦY" (HANDS-FREE CHECK)
    # -----------------------------------------------------------------
    print("\n--- [KIỂM THỬ LỖI 2] Hands-free check từ khóa 'xóa' / 'hủy' & Xóa dòng cuối ---")
    # Hiện tại bảng có 16 mẻ, tổng số là expected_running_total
    initial_total = counter_app.total_batch_count
    initial_rows_count = len(counter_app.tree_batch.get_children())
    assert initial_rows_count == 16, f"Expected 16 rows, got {initial_rows_count}"

    test_undo_commands = [
        ("Xóa", 8),            # Viết hoa "Xóa", mẻ cuối là "bốc tám con" (+8)
        ("Hủy", 6),            # Viết hoa "Hủy", mẻ tiếp theo là "mẻ sáu" (+6)
        ("xóa hộ", 5),         # Cụm từ "xóa hộ", mẻ tiếp theo là "thêm năm con" (+5)
        ("hủy mẻ này", 10),    # Cụm từ dài "hủy mẻ này", mẻ tiếp theo là "chục" (+10)
        ("xóa đi", 10),        # Cụm từ "xóa đi", mẻ tiếp theo là "mười" (+10)
        ("hủy bỏ", 9)          # Cụm từ "hủy bỏ", mẻ tiếp theo là "chín" (+9)
    ]

    current_total = initial_total
    current_rows = initial_rows_count

    for undo_text, reverted_amount in test_undo_commands:
        app_module.is_processing = False
        counter_app.is_processing = False

        counter_app._handle_mode2_speech(undo_text)
        current_total -= reverted_amount
        current_rows -= 1

        tree_rows = len(counter_app.tree_batch.get_children())
        records_rows = len(counter_app.batch_records)

        assert counter_app.total_batch_count == current_total, (
            f"Lỗi Undo '{undo_text}': Mong đợi tổng còn {current_total}, nhưng thực tế là {counter_app.total_batch_count}"
        )
        assert tree_rows == current_rows, (
            f"Lỗi: Dòng cuối trong bảng Treeview chưa bị xóa! Mong đợi {current_rows} dòng, thực tế {tree_rows} dòng"
        )
        assert records_rows == current_rows, (
            f"Lỗi: Danh sách batch_records chưa xóa phần tử cuối! Mong đợi {current_rows}, thực tế {records_rows}"
        )
        print(f"  -> Lệnh Undo: '{undo_text}' => Trừ thành công -{reverted_amount} con & Đã xóa dòng cuối! Tổng còn: {current_total} (Bảng còn {tree_rows} dòng)")

    print("  => LỖI 2 ĐÃ ĐƯỢC KHẮC PHỤC HOÀN TOÀN: Bắt nhạy mọi biến thể chữ hoa, cụm từ dài và xóa dòng bảng chuẩn xác!")

    # -----------------------------------------------------------------
    # KIỂM THỬ LỖI 3: DEBOUNCE / COOLDOWN LOCK CHỐNG DOUBLE TRIGGER
    # -----------------------------------------------------------------
    print("\n--- [KIỂM THỬ LỖI 3] Cơ chế khóa an toàn Debounce chống Double Trigger ---")
    counter_app._reset_total_shrimp_count()
    app_module.is_processing = False
    counter_app.is_processing = False

    # 1. Gọi câu đầu tiên
    print("  -> Bước 1: Google STT kích hoạt câu: 'mười'")
    counter_app._on_speech_text_received("mười")
    counter_app._process_msg_queue()
    counter_app.update()

    assert counter_app.total_batch_count == 10, f"Expected total 10, got {counter_app.total_batch_count}"
    assert app_module.is_processing is True, "Cơ chế khóa Debounce chưa kích hoạt (is_processing phải là True)!"
    assert counter_app.is_processing is True, "Instance is_processing phải là True!"
    print(f"     ✅ Khóa an toàn Debounce đã BẬT (is_processing = True). Tổng tôm: {counter_app.total_batch_count}")

    # 2. Ngay lập tức (trong vòng 50ms), Google STT gửi câu trùng lặp y hệt do luồng song song
    print("  -> Bước 2: Google STT gửi trùng lặp câu 'mười' sau 30ms (Double Trigger)...")
    counter_app._on_speech_text_received("mười")
    counter_app.update()

    # Tổng tôm PHẢI VẪN LÀ 10, KHÔNG ĐƯỢC TĂNG LÊN 20!
    assert counter_app.total_batch_count == 10, (
        f"LỖI DOUBLE TRIGGER: Tổng tôm bị tăng trùng lặp thành {counter_app.total_batch_count} thay vì 10!"
    )
    assert len(counter_app.batch_records) == 1, (
        f"LỖI DOUBLE TRIGGER: Đã chèn trùng {len(counter_app.batch_records)} dòng thay vì 1 dòng!"
    )
    print("     ✅ Đã CHẶN THÀNH CÔNG Double Trigger! Bảng chỉ có duy nhất 1 dòng (+10 con).")

    # 3. Đợi 0.6 giây để Cooldown Timer (0.5s) tự động mở khóa
    print("  -> Bước 3: Đang đợi 0.6 giây để hết thời gian Cooldown (0.5s)...")
    time.sleep(0.65)
    counter_app.update()

    assert app_module.is_processing is False, "Hết thời gian Cooldown nhưng is_processing chưa được mở khóa về False!"
    print("     ✅ Khóa an toàn Debounce đã TỰ ĐỘNG MỞ (is_processing = False). Sẵn sàng nhận câu tiếp theo!")

    # 4. Gửi câu tiếp theo sau cooldown -> Phải được nhận thành công
    print("  -> Bước 4: Đọc câu tiếp theo: 'năm'...")
    counter_app._on_speech_text_received("năm")
    counter_app._process_msg_queue()
    counter_app.update()

    assert counter_app.total_batch_count == 15, f"Expected total 15, got {counter_app.total_batch_count}"
    assert len(counter_app.batch_records) == 2, f"Expected 2 rows, got {len(counter_app.batch_records)}"
    print(f"     ✅ Câu tiếp theo được xử lý thành công! Tổng tôm: {counter_app.total_batch_count} con.")

    print("\n=====================================================================")
    print("=== TOÀN BỘ 3 LỖI VẬN HÀNH ĐÃ ĐƯỢC KHẮC PHỤC VÀ KIỂM THỬ PASS 100%! ===")
    print("=====================================================================")
    counter_app.destroy()

if __name__ == '__main__':
    test_operational_bugfixes()
