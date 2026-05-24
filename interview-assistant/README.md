# 面试语音辅助工具

> 实时监听面试官问题 → 语音识别 → 知识库搜索 → 悬浮窗显示答案

---

## 功能特点

- 🎙️ **实时语音识别**：本地 Whisper 模型，无需网络/API费用
- 🔍 **极速搜索**：TF-IDF + 余弦相似度，毫秒级返回结果
- 📖 **知识库索引**：自动加载所有 Markdown 面试文档
- 🖥️ **悬浮窗显示**：置顶半透明窗口，不影响视频面试
- 🔒 **完全离线**：所有处理在本地完成，隐私安全

---

## 快速开始

### 1. 安装依赖

```bash
cd interview-assistant

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 三种使用方式

#### 方式一：纯搜索模式（最简单，不需要麦克风和 Whisper）

```bash
python search_only.py
```

手动输入关键词搜索知识库，适合：
- 快速验证搜索效果
- 没有麦克风的环境
- Whisper 安装有困难时

#### 方式二：GUI 悬浮窗模式（推荐面试使用）

```bash
python app.py
```

特点：
- 置顶透明悬浮窗
- 自动监听麦克风
- 实时显示答案
- 按 `Esc` 退出

#### 方式三：命令行模式

```bash
python app.py --cli
```

终端显示，适合调试。

---

## 配置说明

编辑 `config.py` 修改配置：

| 配置项 | 说明 | 建议值 |
|--------|------|--------|
| `WHISPER_MODEL` | 模型大小 | `base`（速度和准确率平衡）|
| `RECORD_SECONDS` | 录音时长 | `5`（越短响应越快）|
| `TOP_K_RESULTS` | 返回结果数 | `3` |
| `WINDOW_OPACITY` | 窗口透明度 | `0.92` |
| `WINDOW_POSITION` | 窗口位置 | `right_bottom` |

---

## 系统要求

| 项目 | 最低要求 | 推荐 |
|------|---------|------|
| Python | 3.8+ | 3.10+ |
| 内存 | 4GB | 8GB+ |
| CPU | 任意 | 多核（Whisper加速）|
| 麦克风 | 需要（语音模式）| 降噪麦克风 |
| 网络 | ❌ 不需要 | - |

---

## 面试使用技巧

### 布局建议

```
┌─────────────────────────────────────────────┐
│  视频面试窗口 (Teams/Zoom/飞书)              │
│                                             │
│                                             │
│                                             │
│                          ┌────────────────┐ │
│                          │ 面试助手悬浮窗  │ │
│                          │ (右下角,半透明) │ │
│                          └────────────────┘ │
└─────────────────────────────────────────────┘
```

### 注意事项

1. **面试前测试**：提前运行确认麦克风正常、搜索准确
2. **调整透明度**：根据背景调整 `WINDOW_OPACITY`
3. **眼神管理**：不要频繁看辅助窗口，自然地看摄像头
4. **作为辅助**：工具只是提示关键词，回答还是要自己组织语言
5. **静音问题**：如果戴耳机，确保系统麦克风能录到面试官的声音

### 如果 Whisper 安装困难

Whisper 需要下载模型文件，首次运行会自动下载。如果网络问题：

```bash
# 方案1: 使用镜像
pip install faster-whisper -i https://pypi.tuna.tsinghua.edu.cn/simple

# 方案2: 直接用纯搜索模式
python search_only.py

# 方案3: 用 OpenAI Whisper API (需要网络+付费)
# 修改 speech_recognizer.py 使用 openai.audio.transcriptions
```

---

## 项目结构

```
interview-assistant/
├── app.py                 # 主程序入口 (GUI/CLI)
├── speech_recognizer.py   # 语音识别模块
├── knowledge_index.py     # 知识库索引和搜索
├── search_only.py         # 纯搜索模式 (无需语音)
├── config.py              # 配置文件
├── requirements.txt       # Python 依赖
└── README.md              # 本文件
```

---

## 常见问题

**Q: 识别不准确怎么办？**
A: 把 `WHISPER_MODEL` 改为 `small` 或 `medium`，牺牲速度换精度。

**Q: 响应太慢？**
A: 减小 `SILENCE_DURATION`（更快结束录音段）；用 `tiny` 模型。

**Q: 搜索结果不相关？**
A: 知识库内容越丰富越准。也可以在知识库md里多加同义词/关键词。

**Q: Mac 上无法录音？**
A: 系统设置 → 安全性与隐私 → 麦克风 → 允许终端/Python。

**Q: Windows 上 Tkinter 报错？**
A: 重装 Python 时勾选 "tcl/tk and IDLE"。

---

## 进阶优化方向

1. **嵌入向量搜索**：用 sentence-transformers 替代 TF-IDF，语义理解更好
2. **LLM 总结**：搜索到内容后用 GPT/Claude 生成精简回答
3. **快捷键触发**：按快捷键才搜索，避免噪音干扰
4. **历史记录**：记录面试问题，面试后复盘
5. **多语言**：支持英文面试

---

*祝面试顺利！*
