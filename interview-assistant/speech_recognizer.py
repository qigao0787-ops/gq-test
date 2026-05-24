"""
语音识别模块
实时录音 → 静音检测(一句话结束) → Whisper 转文字 → 回调
"""
import numpy as np
import threading
import queue
from config import (
    SAMPLE_RATE, CHANNELS, WHISPER_MODEL, WHISPER_LANGUAGE,
    USE_GPU, SILENCE_THRESHOLD, SILENCE_DURATION
)


class SpeechRecognizer:
    """实时语音识别器(后台运行,无UI)"""

    def __init__(self, on_text_callback=None):
        self.on_text_callback = on_text_callback
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.model = None
        self._load_model()

    def _load_model(self):
        print(f"[语音] 加载 Whisper 模型 ({WHISPER_MODEL})...")
        try:
            from faster_whisper import WhisperModel
            compute_type = "float16" if USE_GPU else "int8"
            device = "cuda" if USE_GPU else "cpu"
            self.model = WhisperModel(WHISPER_MODEL, device=device, compute_type=compute_type)
            print(f"[语音] 模型就绪 (设备: {device})")
        except ImportError:
            print("[语音] ⚠️ faster-whisper 未安装")
            print("[语音]    pip install faster-whisper")
            self.model = None
        except Exception as e:
            print(f"[语音] ⚠️ 加载失败: {e}")
            self.model = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        print("[语音] 🎙️ 开始监听...")
        threading.Thread(target=self._record_loop, daemon=True).start()
        threading.Thread(target=self._recognize_loop, daemon=True).start()

    def stop(self):
        self.is_running = False
        print("[语音] 停止")

    def _record_loop(self):
        import sounddevice as sd
        buffer = []
        silence_count = 0
        has_voice = False

        def callback(indata, frames, time_info, status):
            nonlocal buffer, silence_count, has_voice
            volume = np.abs(indata).mean()
            if volume > SILENCE_THRESHOLD:
                buffer.append(indata.copy())
                silence_count = 0
                has_voice = True
            elif has_voice:
                buffer.append(indata.copy())
                silence_count += frames / SAMPLE_RATE
                if silence_count >= SILENCE_DURATION:
                    if buffer:
                        self.audio_queue.put(np.concatenate(buffer))
                    buffer = []
                    silence_count = 0
                    has_voice = False

        try:
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                                dtype='float32', blocksize=int(SAMPLE_RATE * 0.1),
                                callback=callback):
                while self.is_running:
                    sd.sleep(100)
        except Exception as e:
            print(f"[语音] ❌ 录音错误: {e}")

    def _recognize_loop(self):
        while self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=1.0)
            except queue.Empty:
                continue
            text = self._transcribe(audio_data)
            if text and len(text.strip()) > 1:
                print(f"[语音] 识别: {text}")
                if self.on_text_callback:
                    self.on_text_callback(text)

    def _transcribe(self, audio_data):
        if self.model is None:
            return None
        try:
            audio_float = audio_data.flatten().astype(np.float32)
            segments, _ = self.model.transcribe(
                audio_float, language=WHISPER_LANGUAGE,
                beam_size=3, vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            return ' '.join(seg.text for seg in segments).strip()
        except Exception as e:
            print(f"[语音] ⚠️ 识别错误: {e}")
            return None
