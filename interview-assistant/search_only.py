"""
纯搜索模式 - 不需要语音识别，手动输入关键词搜索
适合没有麦克风或 whisper 安装困难的情况
依赖极少: 只需要 jieba + scikit-learn
"""
from knowledge_index import KnowledgeIndex


def main():
    print("="*50)
    print("  面试知识库快速搜索")
    print("  输入关键词即可搜索，输入 q 退出")
    print("="*50)

    index = KnowledgeIndex()

    while True:
        print()
        query = input("🔍 搜索: ").strip()

        if query.lower() in ('q', 'quit', 'exit'):
            print("再见!")
            break

        if not query:
            continue

        results = index.search(query)

        if results:
            for i, r in enumerate(results):
                print(f"\n{'━'*50}")
                print(f"📌 [{i+1}] [{r['file']}] {r['title']}")
                print(f"   匹配度: {r['score']:.1%}")
                print(f"{'━'*50}")

                # 显示内容(限制长度)
                content = r['content']
                if len(content) > 600:
                    content = content[:600] + "\n... (内容已截断，完整版请看原文件)"
                print(content)
        else:
            print("❌ 未找到相关内容，试试换个关键词")


if __name__ == "__main__":
    main()
