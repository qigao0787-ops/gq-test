"""
面试辅助工具配置文件
"""
import os

# ============ 路径配置 ============
# 知识库目录 (你的面试md文件所在目录)
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "document")

# ============ 语音识别配置 ============
# Whisper 模型大小: tiny/base/small/medium/large-v3
# tiny: 最快(~1s), 准确率一般, 适合实时
# base: 较快(~2s), 准确率较好, 推荐
# small: 中等(~4s), 准确率好
# medium: 较慢(~8s), 准确率很好
# large-v3: 最慢(~15s), 最准确
WHISPER_MODEL = "base"

# 语音识别语言
WHISPER_LANGUAGE = "zh"

# 录音参数
SAMPLE_RATE = 16000          # 采样率
CHANNELS = 1                 # 单声道
RECORD_SECONDS = 5           # 每次录音时长(秒), 越短响应越快

# ============ 搜索配置 ============
# 返回最相关的 N 个结果
TOP_K_RESULTS = 3

# 最低相关度阈值 (0~1, 低于此值不显示)
MIN_RELEVANCE_SCORE = 0.05

# ============ UI 配置 ============
# 窗口透明度 (0.0 完全透明 ~ 1.0 完全不透明)
WINDOW_OPACITY = 0.92

# 窗口大小
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500

# 窗口位置 (右下角)
WINDOW_POSITION = "right_bottom"  # right_bottom / right_top / left_bottom / left_top

# 字体大小
FONT_SIZE_QUESTION = 14
FONT_SIZE_ANSWER = 12

# ============ 高级配置 ============
# 是否使用GPU加速 (需要CUDA)
USE_GPU = False

# 静音检测阈值 (低于此值认为是静音,不处理)
SILENCE_THRESHOLD = 0.01

# 连续静音多少秒后停止当前录音段
SILENCE_DURATION = 1.5
