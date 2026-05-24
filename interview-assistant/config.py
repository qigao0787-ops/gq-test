"""
面试辅助工具配置文件
架构: 电脑后台运行(无任何可见UI) → 手机浏览器查看答案
"""
import os

# ============ 路径配置 ============
# 知识库目录 (自动找到 interview-assistant 同级的 document 目录)
_this_dir = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(_this_dir), "document")

# 兜底: 如果路径不存在,尝试其他位置
if not os.path.exists(KNOWLEDGE_BASE_DIR):
    KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.getcwd()), "document")
if not os.path.exists(KNOWLEDGE_BASE_DIR):
    KNOWLEDGE_BASE_DIR = os.path.join(os.getcwd(), "..", "document")

# ============ Web 服务配置 ============
WEB_PORT = 9900
WEB_HOST = "0.0.0.0"

# ============ 语音识别配置 ============
WHISPER_MODEL = "base"
WHISPER_LANGUAGE = "zh"
SAMPLE_RATE = 16000
CHANNELS = 1

# ============ 搜索配置 ============
TOP_K_RESULTS = 3
MIN_RELEVANCE_SCORE = 0.05

# ============ 高级配置 ============
USE_GPU = False
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.5
