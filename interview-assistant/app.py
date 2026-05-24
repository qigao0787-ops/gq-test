"""
面试辅助工具 - 主程序
实时监听面试官问题 → 语音识别 → 知识库搜索 → 悬浮窗显示答案
"""
import tkinter as tk
from tkinter import scrolledtext, font
import threading
import time
from knowledge_index import KnowledgeIndex
from speech_recognizer import SpeechRecognizer
from config import (
    WINDOW_OPACITY, WINDOW_WIDTH, WINDOW_HEIGHT,
    FONT_SIZE_QUESTION, FONT_SIZE_ANSWER, WINDOW_POSITION
)


class InterviewAssistantUI:
    """面试辅助悬浮窗"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("面试助手 (按 Esc 退出)")
        self._setup_window()
        self._create_widgets()

        # 初始化知识库
        self.status_var.set("⏳ 正在加载知识库...")
        self.root.update()
        self.knowledge = KnowledgeIndex()

        # 初始化语音识别
        self.status_var.set("⏳ 正在加载语音模型...")
        self.root.update()
        self.recognizer = SpeechRecognizer(on_text_callback=self._on_speech_text)

        self.status_var.set("✅ 就绪! 正在监听...")
        self.recognizer.start()

    def _setup_window(self):
        """设置窗口属性"""
        # 窗口大小
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # 窗口位置
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        if WINDOW_POSITION == "right_bottom":
            x = screen_w - WINDOW_WIDTH - 20
            y = screen_h - WINDOW_HEIGHT - 80
        elif WINDOW_POSITION == "right_top":
            x = screen_w - WINDOW_WIDTH - 20
            y = 50
        elif WINDOW_POSITION == "left_bottom":
            x = 20
            y = screen_h - WINDOW_HEIGHT - 80
        else:  # left_top
            x = 20
            y = 50

        self.root.geometry(f"+{x}+{y}")

        # 透明度
        self.root.attributes('-alpha', WINDOW_OPACITY)

        # 置顶
        self.root.attributes('-topmost', True)

        # 配色
        self.root.configure(bg='#1e1e2e')

        # 快捷键
        self.root.bind('<Escape>', lambda e: self._quit())
        self.root.bind('<Control-q>', lambda e: self._quit())

    def _create_widgets(self):
        """创建UI组件"""
        # 状态栏
        self.status_var = tk.StringVar(value="初始化中...")
        status_frame = tk.Frame(self.root, bg='#313244')
        status_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            fg='#a6e3a1',
            bg='#313244',
            font=('Microsoft YaHei', 10)
        )
        status_label.pack(side=tk.LEFT, padx=10, pady=5)

        # 识别到的问题
        question_frame = tk.Frame(self.root, bg='#1e1e2e')
        question_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(
            question_frame,
            text="🎙️ 面试官问题:",
            fg='#f9e2af',
            bg='#1e1e2e',
            font=('Microsoft YaHei', 11, 'bold')
        ).pack(anchor=tk.W, padx=10)

        self.question_var = tk.StringVar(value="等待面试官提问...")
        self.question_label = tk.Label(
            question_frame,
            textvariable=self.question_var,
            fg='#cdd6f4',
            bg='#313244',
            font=('Microsoft YaHei', FONT_SIZE_QUESTION),
            wraplength=WINDOW_WIDTH - 40,
            justify=tk.LEFT,
            padx=10,
            pady=8
        )
        self.question_label.pack(fill=tk.X, padx=10, pady=(2, 0))

        # 答案区域
        answer_frame = tk.Frame(self.root, bg='#1e1e2e')
        answer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(
            answer_frame,
            text="📖 参考答案:",
            fg='#89b4fa',
            bg='#1e1e2e',
            font=('Microsoft YaHei', 11, 'bold')
        ).pack(anchor=tk.W, padx=10)

        self.answer_text = scrolledtext.ScrolledText(
            answer_frame,
            wrap=tk.WORD,
            bg='#313244',
            fg='#cdd6f4',
            font=('Microsoft YaHei', FONT_SIZE_ANSWER),
            insertbackground='#cdd6f4',
            relief=tk.FLAT,
            padx=10,
            pady=8
        )
        self.answer_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 5))
        self.answer_text.insert(tk.END, "等待问题...\n\n提示:\n- 程序会自动监听麦克风\n- 识别到问题后自动搜索答案\n- 按 Esc 或 Ctrl+Q 退出")
        self.answer_text.config(state=tk.DISABLED)

        # 底部提示
        tk.Label(
            self.root,
            text="Esc退出 | 自动监听中 | 保持窗口置顶",
            fg='#6c7086',
            bg='#1e1e2e',
            font=('Microsoft YaHei', 9)
        ).pack(side=tk.BOTTOM, pady=3)

    def _on_speech_text(self, text):
        """语音识别回调 - 在主线程更新UI"""
        self.root.after(0, self._process_question, text)

    def _process_question(self, question):
        """处理识别到的问题"""
        # 更新问题显示
        self.question_var.set(question)
        self.status_var.set(f"🔍 正在搜索: {question[:30]}...")

        # 搜索知识库
        results = self.knowledge.search(question)

        # 更新答案显示
        self.answer_text.config(state=tk.NORMAL)
        self.answer_text.delete('1.0', tk.END)

        if results:
            for i, r in enumerate(results):
                # 标题和来源
                self.answer_text.insert(tk.END, f"{'─'*40}\n")
                self.answer_text.insert(tk.END, f"📌 [{r['file']}] {r['title']}")
                self.answer_text.insert(tk.END, f"  (匹配度: {r['score']:.1%})\n")
                self.answer_text.insert(tk.END, f"{'─'*40}\n\n")

                # 内容 (截取关键部分)
                content = r['content']
                # 限制每段显示长度
                if len(content) > 800:
                    content = content[:800] + "\n\n... (内容已截断)"
                self.answer_text.insert(tk.END, content + "\n\n")

            self.status_var.set(f"✅ 找到 {len(results)} 条相关结果")
        else:
            self.answer_text.insert(tk.END, "❌ 未找到相关内容\n\n")
            self.answer_text.insert(tk.END, f"搜索词: {question}\n")
            self.answer_text.insert(tk.END, "建议: 等面试官说完整一点再搜索")
            self.status_var.set("⚠️ 未找到匹配结果")

        self.answer_text.config(state=tk.DISABLED)
        # 滚动到顶部
        self.answer_text.yview_moveto(0)

    def _quit(self):
        """退出程序"""
        self.recognizer.stop()
        self.root.destroy()

    def run(self):
        """运行主循环"""
        self.root.mainloop()


class InterviewAssistantCLI:
    """命令行版本 (无GUI依赖，用于测试)"""

    def __init__(self):
        print("="*50)
        print("  面试辅助工具 - 命令行版")
        print("="*50)

        self.knowledge = KnowledgeIndex()
        self.recognizer = SpeechRecognizer(on_text_callback=self._on_speech_text)
        self.recognizer.start()

    def _on_speech_text(self, text):
        """处理识别到的文字"""
        print(f"\n{'='*50}")
        print(f"🎙️ 面试官: {text}")
        print(f"{'='*50}")

        results = self.knowledge.search(text)
        if results:
            for i, r in enumerate(results):
                print(f"\n📌 [{i+1}] [{r['file']}] {r['title']} (匹配: {r['score']:.1%})")
                print("-"*40)
                # 只显示前300字
                content = r['content'][:300]
                print(content)
                if len(r['content']) > 300:
                    print("... (更多内容略)")
        else:
            print("❌ 未找到相关内容")

        print(f"\n{'─'*50}")
        print("继续监听中... (Ctrl+C 退出)")

    def run(self):
        """运行"""
        print("\n🎙️ 正在监听麦克风... (Ctrl+C 退出)\n")
        try:
            import sounddevice as sd
            while True:
                sd.sleep(1000)
        except KeyboardInterrupt:
            self.recognizer.stop()
            print("\n已退出")


def main():
    """主入口"""
    import sys

    if "--cli" in sys.argv:
        # 命令行模式
        app = InterviewAssistantCLI()
    else:
        # GUI 模式
        app = InterviewAssistantUI()

    app.run()


if __name__ == "__main__":
    main()
