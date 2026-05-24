"""
面试辅助工具配置文件
架构: 电脑后台运行(无任何可见UI) → 手机浏览器查看答案
"""
import os

# ============ 路径配置 ============
# 知识库目录 (你的面试md文件所在目录)
# 自动找到 interview-assistant 同级的 document 目录
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))), "document")

# 如果上面的路径找不到，尝试当前工作目录的上级
if not os.path.exists(KNOWLEDGE_BASE_DIR):
    KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.getcwd()), "document")
if not os.path.exists(KNOWLEDGE_BASE_DIR):
    KNOWLEDGE_BASE_DIR = os.path.join(os.getcwd(), "..", "document")

# ============ Web 服务配置 ============
# 本地 Web 服务端口 (手机浏览器访问 http://电脑IP:端口)
WEB_PORT = 9900

# 绑定地址 (0.0.0.0 允许局域网访问)
WEB_HOST = "0.0.0.0"

# ============ 语音识别配置 ============
# Whisper 模型大小: tiny/base/small/medium/large-v3
# tiny: 最快(~1s), 准确率一般, 适合实时
# base: 较快(~2s), 准确率较好, ★推荐
# small: 中等(~4s), 准确率好
WHISPER_MODEL = "base"

# 语音识别语言
WHISPER_LANGUAGE = "zh"

# 录音参数
SAMPLE_RATE = 16000          # 采样率
CHANNELS = 1                 # 单声道

# ============ 搜索配置 ============
# 返回最相关的 N 个结果
TOP_K_RESULTS = 3

# 最低相关度阈值 (0~1, 低于此值不显示)
MIN_RELEVANCE_SCORE = 0.05

# ============ 高级配置 ============
# 是否使用GPU加速 (需要CUDA)
USE_GPU = False

# 静音检测: 音量低于此值认为是静音
SILENCE_THRESHOLD = 0.01

# 连续静音多少秒后认为一句话说完
SILENCE_DURATION = 1.5
