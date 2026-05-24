"""
语音识别模块
实时录音 → 静音检测 → Whisper 转文字
"""
import numpy as np
import sounddevice as sd
import threading
import queue
import tempfile
import wave
import os
from config import (
    SAMPLE_RATE, CHANNELS, RECORD_SECONDS,
    WHISPER_MODEL, WHISPER_LANGUAGE, USE_GPU,
    SILENCE_THRESHOLD, SILENCE_DURATION
)


class SpeechRecognizer:
    """实时语音识别器"""

    def __init__(self, on_text_callback=None):
        """
        Args:
            on_text_callback: 识别到文字时的回调函数 callback(text: str)
        """
        self.on_text_callback = on_text_callback
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.model = None
        self._load_model()

    def _load_model(self):
        """加载 Whisper 模型"""
        print(f"[语音] 正在加载 Whisper 模型 ({WHISPER_MODEL})...")
        try:
            from faster_whisper import WhisperModel
            compute_type = "float16" if USE_GPU else "int8"
            device = "cuda" if USE_GPU else "cpu"
            self.model = WhisperModel(
                WHISPER_MODEL,
                device=device,
                compute_type=compute_type
            )
            print(f"[语音] 模型加载完成! (设备: {device})")
        except ImportError:
            print("[语音] ⚠️ faster-whisper 未安装，将使用模拟模式")
            print("[语音]    安装命令: pip install faster-whisper")
            self.model = None
        except Exception as e:
            print(f"[语音] ⚠️ 模型加载失败: {e}")
            self.model = None

    def start(self):
        """开始监听麦克风"""
        if self.is_running:
            return

        self.is_running = True
        print("[语音] 🎙️ 开始监听麦克风...")

        # 录音线程
        self.record_thread = threading.Thread(target=self._record_loop, daemon=True)
        self.record_thread.start()

        # 识别线程
        self.recognize_thread = threading.Thread(target=self._recognize_loop, daemon=True)
        self.recognize_thread.start()

    def stop(self):
        """停止监听"""
        self.is_running = False
        print("[语音] 🛑 停止监听")

    def _record_loop(self):
        """持续录音，检测到语音后放入队列"""
        buffer = []
        silence_count = 0
        has_voice = False

        def audio_callback(indata, frames, time_info, status):
            nonlocal buffer, silence_count, has_voice

            # 计算音量
            volume = np.abs(indata).mean()

            if volume > SILENCE_THRESHOLD:
                # 检测到声音
                buffer.append(indata.copy())
                silence_count = 0
                has_voice = True
            elif has_voice:
                # 声音结束后的静音
                buffer.append(indata.copy())
                silence_count += frames / SAMPLE_RATE

                if silence_count >= SILENCE_DURATION:
                    # 静音超过阈值，认为一句话结束
                    if len(buffer) > 0:
                        audio_data = np.concatenate(buffer)
                        self.audio_queue.put(audio_data)
                    buffer = []
                    silence_count = 0
                    has_voice = False

        try:
            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype='float32',
                blocksize=int(SAMPLE_RATE * 0.1),  # 100ms blocks
                callback=audio_callback
            ):
                while self.is_running:
                    sd.sleep(100)
        except Exception as e:
            print(f"[语音] ❌ 录音错误: {e}")
            print("[语音]    请检查麦克风是否可用")

    def _recognize_loop(self):
        """从队列取音频，进行识别"""
        while self.is_running:
            try:
                audio_data = self.audio_queue.get(timeout=1.0)
            except queue.Empty:
                continue

            # 识别
            text = self._transcribe(audio_data)
            if text and len(text.strip()) > 1:
                print(f"[语音] 📝 识别结果: {text}")
                if self.on_text_callback:
                    self.on_text_callback(text)

    def _transcribe(self, audio_data):
        """将音频数据转为文字"""
        if self.model is None:
            return None

        try:
            # faster-whisper 需要 numpy array
            audio_float = audio_data.flatten().astype(np.float32)

            segments, info = self.model.transcribe(
                audio_float,
                language=WHISPER_LANGUAGE,
                beam_size=3,
                vad_filter=True,       # 启用 VAD 过滤静音
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                ),
            )

            text = ' '.join(segment.text for segment in segments)
            return text.strip()

        except Exception as e:
            print(f"[语音] ⚠️ 识别错误: {e}")
            return None


# 测试
if __name__ == "__main__":
    def on_text(text):
        print(f"\n{'='*40}")
        print(f"识别到: {text}")
        print(f"{'='*40}\n")

    recognizer = SpeechRecognizer(on_text_callback=on_text)
    recognizer.start()

    print("\n请对着麦克风说话 (按 Ctrl+C 退出)...\n")
    try:
        while True:
            sd.sleep(1000)
    except KeyboardInterrupt:
        recognizer.stop()
        print("\n已退出")
