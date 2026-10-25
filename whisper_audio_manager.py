# -*- coding: utf-8 -*-
"""
Module: whisper_audio_manager.py
Chức năng: Quản lý Micro, thu âm liên tục rảnh tay bằng SoundDevice / PyAudio,
triệt tiêu tiếng ồn ao nuôi (sục khí oxy, quạt nước, tiếng nước reo) bằng bộ lọc
ngưỡng năng lượng (Noise Thresholding & Gating) và giải mã bằng OpenAI Whisper (Offline).
"""

import time
import queue
import threading
import numpy as np
from typing import Callable, Optional, List

# Bộ lọc âm thanh tần số thấp (Mechanical Rumble Filter)
try:
    from scipy.signal import butter, sosfilt
    HAVE_SCIPY = True
    # Lọc bỏ tiếng ù cơ học dưới 120Hz của máy bơm, máy nổ và cánh quạt nước
    HP_SOS = butter(4, 120, 'hp', fs=16000, output='sos')
except Exception:
    HAVE_SCIPY = False
    HP_SOS = None

def play_audio_feedback(sound_type: str = 'beep'):
    """
    Phát âm thanh phản hồi nhanh bằng luồng riêng:
    - 'beep': Nhận diện thành công (1200Hz, 130ms)
    - 'undo': Hoàn tác mẻ (900Hz -> 650Hz)
    - 'warning': Cảnh báo hoặc lỗi (500Hz, 200ms)
    - 'start': Bật micro (850Hz -> 1250Hz)
    - 'stop': Tắt micro (1200Hz -> 750Hz)
    """
    def _run():
        try:
            import winsound
            if sound_type == 'beep':
                winsound.Beep(1200, 130)
            elif sound_type == 'undo':
                winsound.Beep(900, 100)
                time.sleep(0.04)
                winsound.Beep(650, 160)
            elif sound_type == 'warning':
                winsound.Beep(500, 200)
            elif sound_type == 'start':
                winsound.Beep(850, 90)
                winsound.Beep(1250, 130)
            elif sound_type == 'stop':
                winsound.Beep(1200, 90)
                winsound.Beep(750, 140)
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()

class WhisperModelManager:
    """Quản lý tải và suy luận mô hình OpenAI Whisper OFFLINE."""
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.current_model = None
        self.current_model_name = None
        self.device = "cpu"
        self._check_device()

    def _check_device(self):
        try:
            import torch
            if torch.cuda.is_available():
                self.device = "cuda"
            else:
                self.device = "cpu"
        except Exception:
            self.device = "cpu"

    def get_or_load_model(self, model_name: str = "base", on_progress: Optional[Callable[[str], None]] = None):
        """Tải mô hình Whisper nếu chưa có trong bộ nhớ cache."""
        with self._lock:
            if self.current_model is not None and self.current_model_name == model_name:
                return self.current_model

            if on_progress:
                on_progress(f"Đang tải mô hình Whisper '{model_name}' ({self.device.upper()}) vào RAM...")

            try:
                import whisper
                import torch
                # Tải mô hình cục bộ hoặc từ cache (~/.cache/whisper)
                model = whisper.load_model(model_name, device=self.device)

                # ÉP KIỂU DỮ LIỆU ĐỒNG NHẤT TRÊN CPU (torch.float32)
                # Triệt tiêu hoàn toàn lỗi: "expected m1 and m2 to have the same dtype"
                if self.device == "cpu" or not (torch.cuda.is_available() and self.device == "cuda"):
                    model = model.float()

                self.current_model = model
                self.current_model_name = model_name

                if on_progress:
                    on_progress(f"Mô hình Whisper '{model_name}' đã sẵn sàng ({self.device.upper()} - float32)!")

                return self.current_model
            except ModuleNotFoundError:
                if on_progress:
                    on_progress("⚠️ Chưa cài xong OpenAI Whisper/Torch. Chạy 'run.bat' để hoàn tất cài đặt.")
                return None
            except Exception as e:
                if on_progress:
                    on_progress(f"Lỗi tải Whisper: {str(e)[:40]}")
                return None

    def transcribe_audio(self, audio_data: np.ndarray, model_name: str = "base") -> str:
        """
        Nhận diện văn bản tiếng Việt từ mảng âm thanh 16kHz float32.
        Ép kiểu dữ liệu âm thanh và mô hình Whisper đồng nhất (float32, fp16=False) trên CPU.
        """
        model = self.get_or_load_model(model_name)
        
        # Nếu chưa có thư viện Whisper, sử dụng fallback dự phòng bằng SpeechRecognition (nếu có)
        if model is None:
            try:
                import speech_recognition as sr
                # Chuyển đổi numpy float32 sang wav bytes cho speech_recognition
                import io
                import wave
                int16_data = (audio_data * 32767).astype(np.int16)
                byte_io = io.BytesIO()
                with wave.open(byte_io, 'wb') as wav_f:
                    wav_f.setnchannels(1)
                    wav_f.setsampwidth(2)
                    wav_f.setframerate(self.sample_rate if hasattr(self, 'sample_rate') else 16000)
                    wav_f.writeframes(int16_data.tobytes())
                byte_io.seek(0)
                r = sr.Recognizer()
                with sr.AudioFile(byte_io) as source:
                    audio_sr = r.record(source)
                return r.recognize_google(audio_sr, language="vi-VN")
            except Exception:
                return ""

        # 1. ÉP KIỂU DỮ LIỆU ÂM THANH ĐẦU VÀO VỀ float32
        audio_data = np.asarray(audio_data, dtype=np.float32)

        # 2. ÉP KIỂU MÔ HÌNH VỀ float32 NẾU CHẠY TRÊN CPU
        import torch
        if self.device == "cpu" and hasattr(model, 'float'):
            model = model.float()

        # 3. CẤU HÌNH fp16=False TRÊN CPU ĐỂ TRÁNH LỖI LỆCH DTYPE
        use_fp16 = False if (self.device == "cpu" or not torch.cuda.is_available()) else True

        # Initial prompt giúp Whisper ưu tiên nhận diện chuẩn các con số và thuật ngữ ao tôm
        shrimp_prompt = "Một, hai, ba, bốn, năm, mười, mười lăm, ba lăm, bốn lăm, năm hai, đực, cái, tôm, mẻ, xóa, hủy."

        with torch.no_grad():
            result = model.transcribe(
                audio_data,
                language="vi",
                fp16=use_fp16, # Bắt buộc fp16=False trên CPU
                temperature=0.0,
                initial_prompt=shrimp_prompt,
                no_speech_threshold=0.6,
                condition_on_previous_text=False
            )
        return result.get("text", "").strip()

# Singleton Whisper Manager
whisper_manager = WhisperModelManager()

class WhisperVoiceListener:
    """
    Bộ lắng nghe micro liên tục rảnh tay, áp dụng thuật toán cắt ngưỡng ồn
    (Noise Thresholding & Gating) để loại bỏ hoàn toàn tiếng nước và sục khí ao trước khi đưa vào Whisper.
    """
    def __init__(
        self,
        on_text_recognized: Callable[[str], None],
        on_status_changed: Callable[[str, str], None],
        on_noise_adjusted: Optional[Callable[[float], None]] = None
    ):
        self.on_text_recognized = on_text_recognized
        self.on_status_changed = on_status_changed
        self.on_noise_adjusted = on_noise_adjusted

        self.sample_rate = 16000
        self.chunk_size = 800  # 50ms mỗi khối âm thanh
        self.is_listening = False
        self.device_index: Optional[int] = None
        self.model_name = "base"  # 'base', 'turbo', 'tiny', 'small'

        # =====================================================================
        # THUẬT TOÁN CẮT NGƯỠNG ỒN (NOISE THRESHOLDING & GATING)
        # =====================================================================
        # Ngưỡng năng lượng hiệu dụng RMS (0.005 đến 0.15)
        # Tiếng sục khí oxy / quạt nước thường dao động quanh 0.015 - 0.035
        # Tiếng người nói trực tiếp vào mic thường từ 0.060 - 0.250
        self.noise_threshold_rms = 0.030
        
        # Số frame tối thiểu để xác nhận là giọng nói thật (tránh tiếng lách cách ngắn < 0.2s)
        self.min_speech_frames = int(0.25 * self.sample_rate / self.chunk_size)  # ~5 frames
        
        # Khoảng lặng ngắt câu (Pause threshold): 0.65 giây
        self.pause_frames_limit = int(0.65 * self.sample_rate / self.chunk_size) # ~13 frames
        
        # Bộ đệm đón đầu (Pre-speech buffer) lưu trước 0.35s âm thanh để không bị nuốt phụ âm đầu
        self.pre_buffer_size = int(0.35 * self.sample_rate / self.chunk_size)    # ~7 frames
        self.pre_speech_ring = []

        self._thread: Optional[threading.Thread] = None
        self._is_calibrating = False

    def set_device_index(self, index: Optional[int]):
        """Chọn micro theo chỉ số thiết bị."""
        self.device_index = index

    def set_model_name(self, name: str):
        """Chọn mô hình Whisper: 'base', 'turbo', 'tiny', 'small'."""
        self.model_name = name

    def set_noise_threshold_pct(self, pct_val: float):
        """
        Quy đổi giá trị thanh trượt (1 - 100) thành ngưỡng RMS thực tế:
        Giá trị 1  -> 0.005
        Giá trị 50 -> 0.040
        Giá trị 100 -> 0.150
        """
        clamped = max(1.0, min(100.0, float(pct_val)))
        # Ánh xạ phi tuyến tính nhẹ
        self.noise_threshold_rms = 0.005 + (clamped / 100.0) ** 1.3 * 0.145

    def get_noise_threshold_pct(self) -> float:
        """Quy đổi ngược từ RMS sang thang điểm 1-100 cho thanh trượt GUI."""
        val = ((self.noise_threshold_rms - 0.005) / 0.145) ** (1 / 1.3) * 100.0
        return max(1.0, min(100.0, val))

    def calibrate_ambient_noise(self, duration: float = 1.5):
        """
        Thuật toán hiệu chuẩn lọc ồn môi trường ao nuôi:
        Đo mức năng lượng nền (tiếng quạt nước, sục khí) trong 1.5s,
        tự động đặt ngưỡng cắt cao hơn tiếng ồn nền 1.8 - 2.2 lần.
        """
        if self._is_calibrating:
            return

        def _worker():
            self._is_calibrating = True
            self.on_status_changed("CALIBRATING", "Đang đo tiếng ồn dàn sục khí/quạt nước (Vui lòng không nói)...")
            try:
                samples_needed = int(duration * self.sample_rate)
                recorded_samples = []

                # Sử dụng sounddevice nếu có, hoặc pyaudio
                try:
                    import sounddevice as sd
                    rec = sd.rec(
                        samples_needed,
                        samplerate=self.sample_rate,
                        channels=1,
                        dtype='float32',
                        device=self.device_index
                    )
                    sd.wait()
                    audio_block = rec.flatten()
                except Exception:
                    # Fallback sang pyaudio
                    audio_block = self._record_raw_pyaudio(duration)

                if audio_block is not None and len(audio_block) > 0:
                    # Lọc bớt tần số cơ học cực thấp
                    if HAVE_SCIPY and HP_SOS is not None:
                        audio_block = sosfilt(HP_SOS, audio_block)

                    # Tính RMS tiếng ồn nền
                    noise_rms = float(np.sqrt(np.mean(np.square(audio_block))))
                    peak_noise = float(np.max(np.abs(audio_block)))

                    # Đặt ngưỡng cắt cao hơn tiếng ồn nền nhưng đảm bảo bắt được tiếng người
                    new_threshold = max(0.015, min(0.120, noise_rms * 2.2))
                    self.noise_threshold_rms = new_threshold

                    pct = self.get_noise_threshold_pct()
                    msg = f"Đã triệt tiêu ồn ao! RMS ồn: {noise_rms:.4f} -> Ngưỡng cắt: {new_threshold:.4f} ({pct:.0f}%)"
                    self.on_status_changed("READY", msg)
                    if self.on_noise_adjusted:
                        self.on_noise_adjusted(pct)
                    play_audio_feedback('beep')
                else:
                    self.on_status_changed("ERROR", "Không đọc được tín hiệu từ micro.")
            except Exception as e:
                self.on_status_changed("ERROR", f"Lỗi hiệu chuẩn lọc ồn: {str(e)[:40]}")
            finally:
                self._is_calibrating = False

        threading.Thread(target=_worker, daemon=True).start()

    def start_listening(self):
        """Bật chế độ rảnh tay liên tục."""
        if self.is_listening:
            return

        self.is_listening = True
        play_audio_feedback('start')
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop_listening(self):
        """Tắt micro."""
        if not self.is_listening:
            return

        self.is_listening = False
        play_audio_feedback('stop')
        self.on_status_changed("STOPPED", "Đã tắt Micro.")

    def _listen_loop(self):
        """Vòng lặp thu âm liên tục & thuật toán cắt ngưỡng ồn (Thresholding)."""
        # Khởi động trước mô hình Whisper trong nền nếu chưa tải
        threading.Thread(
            target=lambda: whisper_manager.get_or_load_model(
                self.model_name,
                lambda msg: self.on_status_changed("READY", msg)
            ),
            daemon=True
        ).start()

        # Thử sử dụng sounddevice trước
        try:
            import sounddevice as sd
            self._listen_sounddevice(sd)
        except Exception as e_sd:
            # Fallback sang pyaudio
            try:
                self._listen_pyaudio()
            except Exception as e_py:
                self.is_listening = False
                self.on_status_changed("ERROR", f"Lỗi khởi động Micro: {str(e_py)[:40]}")

    def _listen_sounddevice(self, sd):
        """Thu âm liên tục qua sounddevice."""
        self.on_status_changed("LISTENING", f"Whisper [{self.model_name.upper()}] - Micro ĐANG BẬT (Đã lọc ồn ao)")

        audio_queue = queue.Queue()

        def callback(indata, frames, time_info, status):
            if self.is_listening:
                audio_queue.put(indata.copy())

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            blocksize=self.chunk_size,
            device=self.device_index,
            callback=callback
        ):
            self._process_audio_stream(audio_queue)

    def _listen_pyaudio(self):
        """Thu âm liên tục qua pyaudio (kênh dự phòng)."""
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.chunk_size
        )
        self.on_status_changed("LISTENING", f"Whisper [{self.model_name.upper()}] - Micro ĐANG BẬT (PyAudio)")

        audio_queue = queue.Queue()

        def reader():
            while self.is_listening:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    arr = np.frombuffer(data, dtype=np.float32)
                    audio_queue.put(arr)
                except Exception:
                    break

        t = threading.Thread(target=reader, daemon=True)
        t.start()

        try:
            self._process_audio_stream(audio_queue)
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    def _process_audio_stream(self, audio_queue: queue.Queue):
        """
        Xử lý từng khối âm thanh bằng thuật toán Cắt ngưỡng ồn (Noise Thresholding):
        - Lọc tần số cơ học cực thấp (< 120Hz)
        - Tính RMS từng block
        - Bỏ qua tiếng sục khí/nước reo (RMS < noise_threshold_rms)
        - Tích lũy câu nói khi vượt ngưỡng
        - Tự động ngắt khi phát hiện khoảng lặng (Pause detection)
        """
        is_speaking = False
        speaking_frames = []
        silence_frame_count = 0
        speech_frame_count = 0
        self.pre_speech_ring.clear()

        while self.is_listening:
            try:
                chunk = audio_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            chunk = chunk.flatten()

            # 1. Lọc bỏ tiếng ù cơ học cánh quạt/máy sục khí dưới 120Hz
            if HAVE_SCIPY and HP_SOS is not None:
                filtered_chunk = sosfilt(HP_SOS, chunk)
            else:
                filtered_chunk = chunk

            # 2. Tính mức năng lượng hiệu dụng (RMS)
            rms = float(np.sqrt(np.mean(np.square(filtered_chunk))))

            # 3. Thuật toán Cắt ngưỡng ồn (Thresholding Gate)
            if rms > self.noise_threshold_rms:
                # ÂM THANH VƯỢT NGƯỠNG ỒN: Có dấu hiệu người đang đọc
                if not is_speaking:
                    is_speaking = True
                    speaking_frames = list(self.pre_speech_ring)  # Ghép đệm đón đầu
                    speech_frame_count = 0
                    self.on_status_changed("LISTENING", "🗣️ Đang ghi nhận giọng nói...")

                speaking_frames.append(filtered_chunk)
                speech_frame_count += 1
                silence_frame_count = 0
            else:
                # ÂM THANH DƯỚI NGƯỠNG: Là tiếng ồn sục khí/nước reo hoặc khoảng lặng
                if is_speaking:
                    speaking_frames.append(filtered_chunk)
                    silence_frame_count += 1

                    # Khi khoảng lặng vượt quá giới hạn -> CẮT CÂU VÀ GỬI VÀO WHISPER
                    if silence_frame_count >= self.pause_frames_limit:
                        is_speaking = False
                        
                        # Chỉ xử lý nếu độ dài giọng nói thực tế >= min_speech_frames (tránh tiếng tặc lưỡi, gõ bàn)
                        if speech_frame_count >= self.min_speech_frames:
                            full_utterance = np.concatenate(speaking_frames)
                            # Đưa vào luồng riêng chạy Whisper để không chặn luồng lắng nghe
                            threading.Thread(
                                target=self._transcribe_utterance,
                                args=(full_utterance,),
                                daemon=True
                            ).start()

                        speaking_frames.clear()
                        silence_frame_count = 0
                        speech_frame_count = 0
                        self.on_status_changed("LISTENING", "Micro đang bật - Sẵn sàng câu tiếp...")
                else:
                    # Duy trì bộ đệm đón đầu (Pre-speech buffer)
                    self.pre_speech_ring.append(filtered_chunk)
                    if len(self.pre_speech_ring) > self.pre_buffer_size:
                        self.pre_speech_ring.pop(0)

    def _transcribe_utterance(self, audio_samples: np.ndarray):
        """Xử lý mảng âm thanh bằng OpenAI Whisper."""
        try:
            self.on_status_changed("PROCESSING", f"⚡ Whisper [{self.model_name.upper()}] đang dịch câu...")
            
            # Ép kiểu dữ liệu âm thanh về float32
            audio_samples = np.asarray(audio_samples, dtype=np.float32)

            # Chuẩn hóa biên độ âm thanh về khoảng [-1.0, 1.0] dạng float32
            max_val = float(np.max(np.abs(audio_samples)))
            if max_val > 0.001:
                audio_norm = (audio_samples / max_val * 0.95).astype(np.float32)
            else:
                audio_norm = audio_samples.astype(np.float32)

            text = whisper_manager.transcribe_audio(audio_norm, model_name=self.model_name)
            
            if text and text.strip():
                # Gửi văn bản nhận diện về giao diện chính
                self.on_text_recognized(text.strip())
                self.on_status_changed("LISTENING", f"Đã nghe: \"{text.strip()}\" - Sẵn sàng...")
            else:
                self.on_status_changed("LISTENING", "Micro đang bật - Sẵn sàng...")
        except Exception as e:
            self.on_status_changed("ERROR", f"Lỗi giải mã Whisper: {str(e)[:40]}")

    def _record_raw_pyaudio(self, duration: float) -> np.ndarray:
        """Ghi âm thô qua PyAudio khi cần hiệu chuẩn."""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            frames_to_read = int(duration * self.sample_rate)
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size
            )
            raw_data = stream.read(frames_to_read, exception_on_overflow=False)
            stream.stop_stream()
            stream.close()
            p.terminate()
            return np.frombuffer(raw_data, dtype=np.float32)
        except Exception:
            return np.array([], dtype=np.float32)

    @staticmethod
    def get_microphone_list() -> List[str]:
        """Lấy danh sách các micro khả dụng."""
        mic_names = []
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if dev.get('max_input_channels', 0) > 0:
                    mic_names.append(f"[{i}] {dev.get('name', 'Mic')}")
        except Exception:
            try:
                import speech_recognition as sr
                mic_names = sr.Microphone.list_microphone_names()
            except Exception:
                pass
        return mic_names if mic_names else ["Mặc định hệ thống"]
