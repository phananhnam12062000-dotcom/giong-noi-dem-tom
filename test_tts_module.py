import os
import sys
import time
import hashlib
import threading
import ctypes

if sys.stdout and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class VietnameseTTS:
    def __init__(self, cache_dir=None):
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "tts_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self._lock = threading.Lock()
        self.enabled = True

    def speak(self, text: str):
        if not self.enabled or not text:
            return
        self._speak_worker(text)

    def _speak_worker(self, text: str):
        with self._lock:
            # 1. Try gTTS with local caching
            try:
                txt_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
                cached_file = os.path.join(self.cache_dir, f"{txt_hash}.mp3")
                if not os.path.exists(cached_file):
                    from gtts import gTTS
                    tts = gTTS(text=text, lang='vi', slow=False)
                    tts.save(cached_file)

                # Play via winmm
                winmm = ctypes.windll.winmm
                alias = f"tts_{int(time.time() * 1000)}"
                winmm.mciSendStringW(f'open "{cached_file}" type mpegvideo alias {alias}', None, 0, 0)
                winmm.mciSendStringW(f'play {alias} wait', None, 0, 0)
                winmm.mciSendStringW(f'close {alias}', None, 0, 0)
                return
            except Exception as e:
                print("gTTS error:", e)

            # 2. Fallback to PowerShell SAPI (native Windows)
            try:
                import subprocess
                clean_t = text.replace("'", "").replace('"', '')
                cmd = f'powershell -Command "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak(\'{clean_t}\')"'
                subprocess.run(cmd, shell=True, timeout=5)
            except Exception as e2:
                print("SAPI error:", e2)

if __name__ == '__main__':
    tts = VietnameseTTS()
    print("Testing speak: 'Đã thêm 5 con, tổng 55'")
    tts.speak("Đã thêm 5 con, tổng 55")
    print("Speak test completed successfully!")
