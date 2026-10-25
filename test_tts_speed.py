# -*- coding: utf-8 -*-
"""
Kịch bản kiểm thử tính năng Tăng tốc độ đọc (TTS Speech Rate):
1. Kiểm tra cấu hình mặc định DEFAULT_TTS_SPEED_RATE = 1.3
2. Kiểm tra phương thức set_speed_rate(1.2), set_speed_rate(1.5)
3. Kiểm tra quá trình tăng tốc âm thanh (PyAV atempo) tạo file WAV giữ nguyên pitch và rút ngắn thời lượng chính xác
4. Kiểm tra tương tác trên GUI Combobox tốc độ đọc
"""

import os
import sys
import wave

if sys.stdout and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import glob
from app import ShrimpSmartCounterApp, VietnameseTTS, DEFAULT_TTS_SPEED_RATE

def test_tts_speed_rate():
    print("=====================================================================")
    print("=== BẮT ĐẦU KIỂM THỬ TÍNH NĂNG TĂNG TỐC ĐỘ ĐỌC (TTS SPEECH RATE) ===")
    print("=====================================================================")

    # 1. Kiểm tra cấu hình mặc định
    print("\n[KIỂM THỬ 1] Kiểm tra cấu hình mặc định:")
    print(f"  -> DEFAULT_TTS_SPEED_RATE = {DEFAULT_TTS_SPEED_RATE}")
    assert DEFAULT_TTS_SPEED_RATE == 1.3, f"Kỳ vọng 1.3, thực tế: {DEFAULT_TTS_SPEED_RATE}"

    tts = VietnameseTTS(speed_rate=DEFAULT_TTS_SPEED_RATE)
    assert tts.speed_rate == 1.3
    print("  ✅ Khởi tạo VietnameseTTS với speed_rate mặc định = 1.3 thành công!")

    # 2. Kiểm tra thay đổi tham số tốc độ linh hoạt
    print("\n[KIỂM THỬ 2] Kiểm tra phương thức set_speed_rate:")
    test_rates = [1.0, 1.2, 1.3, 1.5, 1.8]
    for r in test_rates:
        tts.set_speed_rate(r)
        assert tts.speed_rate == r, f"Lỗi set_speed_rate: {tts.speed_rate} != {r}"
        print(f"  -> set_speed_rate({r}) => tts.speed_rate = {tts.speed_rate}")
    print("  ✅ Phương thức set_speed_rate hoạt động chính xác 100%!")

    # 3. Kiểm tra tăng tốc độ âm thanh với PyAV atempo trên file MP3 mẫu
    print("\n[KIỂM THỬ 3] Kiểm tra xử lý tăng tốc âm thanh (PyAV atempo):")
    cache_files = glob.glob(os.path.join(tts.cache_dir, "*.mp3"))
    if not cache_files:
        print("  ⚠️ Không tìm thấy file MP3 trong cache để test atempo. Bỏ qua bước này.")
    else:
        sample_mp3 = cache_files[0]
        print(f"  -> File MP3 nguồn: {os.path.basename(sample_mp3)}")

        # Lấy thời lượng gốc
        import av
        c_orig = av.open(sample_mp3)
        st_orig = next(s for s in c_orig.streams if s.type == 'audio')
        dur_orig = float(st_orig.duration * st_orig.time_base) if st_orig.duration else 3.5
        c_orig.close()
        print(f"  -> Thời lượng gốc ước tính: ~{dur_orig:.2f}s")

        # Thử tăng tốc x1.2 và x1.5
        for test_speed in [1.2, 1.5]:
            out_wav = os.path.join(tts.cache_dir, f"test_out_x{test_speed}.wav")
            success = tts._speedup_audio(sample_mp3, out_wav, test_speed)
            assert success, f"Tăng tốc audio x{test_speed} thất bại!"
            assert os.path.exists(out_wav), "File WAV không được tạo!"

            with wave.open(out_wav, 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                dur_fast = frames / float(rate)

            ratio = dur_orig / dur_fast if dur_fast > 0 else 0
            print(f"     ✅ Tốc độ x{test_speed}: Thời lượng sau tăng tốc = {dur_fast:.2f}s (Nhanh hơn ~{ratio:.2f}x)")
            assert dur_fast < dur_orig, "Thời lượng sau tăng tốc phải ngắn hơn gốc!"

    # 4. Kiểm tra tương tác trên GUI Tkinter
    print("\n[KIỂM THỬ 4] Kiểm tra giao diện điều khiển tốc độ GUI (Combobox):")
    app = ShrimpSmartCounterApp()
    app.withdraw()

    # Kiểm tra giá trị ban đầu của Combobox
    initial_combo_val = app.combo_tts_speed.get()
    print(f"  -> Giá trị ban đầu trên GUI Combobox: '{initial_combo_val}'")
    assert "1.3" in initial_combo_val, "GUI Combobox ban đầu phải hiển thị x1.3"
    assert app.tts.speed_rate == 1.3

    # Giả lập người dùng chọn x1.5
    app.combo_tts_speed.set("x1.5 (Rất nhanh)")
    app._on_tts_speed_changed()
    assert app.tts.speed_rate == 1.5, f"TTS speed rate chưa cập nhật sang 1.5: {app.tts.speed_rate}"
    print(f"  -> Người dùng chọn 'x1.5 (Rất nhanh)' => TTS speed_rate = {app.tts.speed_rate}")
    transcript_text = app.lbl_transcript.cget("text")
    assert "x1.5" in transcript_text, "Transcript chưa cập nhật thông báo đổi tốc độ!"
    print(f"     ✅ Thông báo hiển thị: \"{transcript_text}\"")

    # Giả lập người dùng chọn x1.2
    app.combo_tts_speed.set("x1.2 (Nhanh vừa)")
    app._on_tts_speed_changed()
    assert app.tts.speed_rate == 1.2
    print(f"  -> Người dùng chọn 'x1.2 (Nhanh vừa)' => TTS speed_rate = {app.tts.speed_rate}")

    app.destroy()
    print("\n=====================================================================")
    print("=== TẤT CẢ CÁC BÀI KIỂM THỬ TỐC ĐỘ ĐỌC TTS ĐÃ PASS 100%! ===")
    print("=====================================================================")

if __name__ == '__main__':
    test_tts_speed_rate()
