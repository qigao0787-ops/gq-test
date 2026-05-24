"""
面试辅助工具 - 隐蔽模式 (安全版)

★ 核心设计: 电脑上没有任何可见窗口！
  - 电脑端: 后台进程 + 本地Web服务
  - 手机端: 浏览器访问 http://电脑IP:9900 查看答案
  - 共享屏幕时: 面试官看不到任何东西

使用:
  1. 电脑运行: python app.py
  2. 手机连同一WiFi,浏览器打开提示的地址
  3. 面试开始,手机自动显示识别到的问题和答案
"""
import json
import time
import socket
import threading
from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO

from knowledge_index import KnowledgeIndex
from speech_recognizer import SpeechRecognizer
from config import WEB_PORT, WEB_HOST

# ============ Flask 应用 ============
app = Flask(__name__)
app.config['SECRET_KEY'] = 'interview-helper-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 全局状态
knowledge = None
recognizer = None
latest_data = {"question": "", "results": [], "timestamp": 0}


# ============ 手机端页面 (暗黑主题,适合低头瞟一眼) ============
MOBILE_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>备忘录</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
    background: #1a1a2e;
    color: #e0e0e0;
    font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
    font-size: 14px;
    padding: 12px;
    min-height: 100vh;
}
.status {
    background: #16213e;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 10px;
    font-size: 12px;
    color: #4ecca3;
    display: flex;
    align-items: center;
    gap: 8px;
}
.status .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #4ecca3;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.question {
    background: #0f3460;
    border-left: 3px solid #e94560;
    border-radius: 6px;
    padding: 10px 12px;
    margin-bottom: 10px;
    font-size: 15px;
    font-weight: 500;
    color: #fff;
    word-break: break-all;
}
.result {
    background: #16213e;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 8px;
    border-left: 3px solid #4ecca3;
}
.result-header {
    font-size: 12px;
    color: #4ecca3;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
}
.result-content {
    font-size: 13px;
    line-height: 1.6;
    color: #ccc;
    white-space: pre-wrap;
    word-break: break-all;
    max-height: 300px;
    overflow-y: auto;
}
.empty {
    text-align: center;
    color: #555;
    padding: 40px 20px;
    font-size: 13px;
}
.manual-search {
    display: flex;
    gap: 8px;
    margin-bottom: 10px;
}
.manual-search input {
    flex: 1;
    background: #16213e;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 8px 12px;
    color: #fff;
    font-size: 14px;
    outline: none;
}
.manual-search input:focus { border-color: #4ecca3; }
.manual-search button {
    background: #4ecca3;
    color: #1a1a2e;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    cursor: pointer;
}
</style>
</head>
<body>

<div class="status">
    <div class="dot" id="statusDot"></div>
    <span id="statusText">连接中...</span>
</div>

<!-- 手动搜索框(语音识别不准时可手动输入) -->
<div class="manual-search">
    <input type="text" id="manualInput" placeholder="手动输入关键词搜索..." 
           onkeypress="if(event.key==='Enter')manualSearch()">
    <button onclick="manualSearch()">搜</button>
</div>

<div id="question" class="question" style="display:none;"></div>
<div id="results"></div>
<div id="empty" class="empty">
    🎙️ 等待面试官提问...<br><br>
    语音自动识别中<br>
    也可以手动输入关键词搜索
</div>

<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<script>
const socket = io();

socket.on('connect', () => {
    document.getElementById('statusText').textContent = '已连接 · 监听中';
    document.getElementById('statusDot').style.background = '#4ecca3';
});

socket.on('disconnect', () => {
    document.getElementById('statusText').textContent = '连接断开';
    document.getElementById('statusDot').style.background = '#e94560';
});

socket.on('new_result', (data) => {
    showResults(data.question, data.results);
});

function showResults(question, results) {
    document.getElementById('empty').style.display = 'none';
    
    const qEl = document.getElementById('question');
    qEl.style.display = 'block';
    qEl.textContent = '🎙️ ' + question;
    
    const rEl = document.getElementById('results');
    if (!results || results.length === 0) {
        rEl.innerHTML = '<div class="empty">未找到相关内容</div>';
        return;
    }
    
    rEl.innerHTML = results.map((r, i) => `
        <div class="result">
            <div class="result-header">
                <span>📌 ${r.file} · ${r.title}</span>
                <span>${(r.score * 100).toFixed(0)}%</span>
            </div>
            <div class="result-content">${escapeHtml(r.content.substring(0, 800))}</div>
        </div>
    `).join('');
    
    window.scrollTo(0, 0);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function manualSearch() {
    const input = document.getElementById('manualInput');
    const query = input.value.trim();
    if (!query) return;
    
    fetch('/api/search?q=' + encodeURIComponent(query))
        .then(r => r.json())
        .then(data => {
            showResults(query, data.results);
        });
    input.value = '';
}
</script>
</body>
</html>
"""


# ============ 路由 ============
@app.route('/')
def index():
    return render_template_string(MOBILE_HTML)


@app.route('/api/search')
def api_search():
    """手动搜索接口"""
    from flask import request
    query = request.args.get('q', '')
    if not query:
        return jsonify({"results": []})
    results = knowledge.search(query)
    return jsonify({"results": results})


@app.route('/api/status')
def api_status():
    """状态接口"""
    return jsonify({
        "status": "running",
        "knowledge_sections": len(knowledge.sections) if knowledge else 0,
        "latest": latest_data
    })


# ============ 语音识别回调 ============
def on_speech_text(text):
    """识别到文字后: 搜索知识库 → WebSocket推送到手机"""
    global latest_data
    results = knowledge.search(text)
    latest_data = {
        "question": text,
        "results": results,
        "timestamp": time.time()
    }
    # 推送到所有连接的手机
    socketio.emit('new_result', latest_data)
    print(f"[推送] {text} → {len(results)} 条结果")


# ============ 获取本机IP ============
def get_local_ip():
    """获取局域网IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


# ============ 主入口 ============
def main():
    global knowledge, recognizer

    print("=" * 55)
    print("  面试辅助工具 · 隐蔽模式 (共享屏幕安全)")
    print("=" * 55)
    print()
    print("  ★ 电脑上无任何可见窗口")
    print("  ★ 答案只显示在手机浏览器上")
    print("  ★ 面试官共享屏幕看不到任何东西")
    print()

    # 1. 加载知识库
    print("[1/3] 加载知识库...")
    knowledge = KnowledgeIndex()

    # 2. 加载语音识别
    print("[2/3] 加载语音识别...")
    recognizer = SpeechRecognizer(on_text_callback=on_speech_text)
    recognizer.start()

    # 3. 启动 Web 服务
    local_ip = get_local_ip()
    print(f"[3/3] 启动 Web 服务...")
    print()
    print("━" * 55)
    print(f"  ✅ 手机浏览器打开: http://{local_ip}:{WEB_PORT}")
    print(f"  ✅ 备用地址:       http://127.0.0.1:{WEB_PORT}")
    print("━" * 55)
    print()
    print("  📱 确保手机和电脑连同一个 WiFi")
    print("  🎙️ 语音自动监听中,也支持手机端手动搜索")
    print("  🛑 按 Ctrl+C 退出")
    print()

    # 启动 Flask (静默模式,不输出HTTP日志)
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    socketio.run(app, host=WEB_HOST, port=WEB_PORT, allow_unsafe_werkzeug=True)


if __name__ == "__main__":
    main()
