"""
纯搜索模式 - 不需要语音识别/麦克风
依赖极少: 只需要 jieba + scikit-learn

两种用法:
  1. 交互模式: python search_only.py
  2. Web模式:  python search_only.py --web
     (同样是手机浏览器访问,但不需要麦克风)
"""
import sys
from knowledge_index import KnowledgeIndex


def interactive_mode():
    """交互式搜索(终端输入)"""
    print("=" * 50)
    print("  面试知识库搜索 (输入 q 退出)")
    print("=" * 50)

    index = KnowledgeIndex()

    while True:
        print()
        query = input("🔍 搜索: ").strip()
        if query.lower() in ('q', 'quit', 'exit'):
            break
        if not query:
            continue

        results = index.search(query)
        if results:
            for i, r in enumerate(results):
                print(f"\n{'━'*50}")
                print(f"📌 [{r['file']}] {r['title']} ({r['score']:.0%})")
                print(f"{'━'*50}")
                content = r['content'][:500]
                print(content)
                if len(r['content']) > 500:
                    print("... (截断)")
        else:
            print("❌ 未找到,换个关键词试试")


def web_mode():
    """Web模式: 只有手动搜索,没有语音"""
    from flask import Flask, render_template_string, jsonify, request
    from config import WEB_PORT, WEB_HOST
    import socket

    app = Flask(__name__)
    index = KnowledgeIndex()

    HTML = """
    <!DOCTYPE html><html><head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>备忘录</title>
    <style>
    *{margin:0;padding:0;box-sizing:border-box}
    body{background:#1a1a2e;color:#e0e0e0;font-family:-apple-system,sans-serif;font-size:14px;padding:12px;min-height:100vh}
    .search{display:flex;gap:8px;margin-bottom:12px}
    .search input{flex:1;background:#16213e;border:1px solid #333;border-radius:6px;padding:10px;color:#fff;font-size:15px;outline:none}
    .search input:focus{border-color:#4ecca3}
    .search button{background:#4ecca3;color:#1a1a2e;border:none;border-radius:6px;padding:10px 20px;font-weight:bold;font-size:15px}
    .result{background:#16213e;border-radius:8px;padding:10px 12px;margin-bottom:8px;border-left:3px solid #4ecca3}
    .result-header{font-size:12px;color:#4ecca3;margin-bottom:6px}
    .result-content{font-size:13px;line-height:1.6;color:#ccc;white-space:pre-wrap;max-height:400px;overflow-y:auto}
    .empty{text-align:center;color:#555;padding:40px;font-size:13px}
    </style></head><body>
    <div class="search">
        <input id="q" placeholder="输入面试关键词..." onkeypress="if(event.key==='Enter')search()">
        <button onclick="search()">搜</button>
    </div>
    <div id="results"><div class="empty">输入关键词搜索面试知识库</div></div>
    <script>
    function search(){
        const q=document.getElementById('q').value.trim();
        if(!q)return;
        fetch('/api/search?q='+encodeURIComponent(q))
        .then(r=>r.json())
        .then(d=>{
            const el=document.getElementById('results');
            if(!d.results.length){el.innerHTML='<div class="empty">未找到</div>';return;}
            el.innerHTML=d.results.map(r=>`
                <div class="result">
                    <div class="result-header">📌 ${r.file} · ${r.title} (${(r.score*100).toFixed(0)}%)</div>
                    <div class="result-content">${r.content.substring(0,800).replace(/</g,'&lt;')}</div>
                </div>`).join('');
        });
        document.getElementById('q').value='';
    }
    </script></body></html>
    """

    @app.route('/')
    def home():
        return render_template_string(HTML)

    @app.route('/api/search')
    def api_search():
        q = request.args.get('q', '')
        return jsonify({"results": index.search(q) if q else []})

    # 获取IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "127.0.0.1"

    print(f"\n手机浏览器打开: http://{ip}:{WEB_PORT}")
    print("Ctrl+C 退出\n")

    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(host=WEB_HOST, port=WEB_PORT)


if __name__ == "__main__":
    if "--web" in sys.argv:
        web_mode()
    else:
        interactive_mode()
