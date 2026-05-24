"""
知识库索引模块
加载所有 Markdown 文件，分段建立 TF-IDF 索引，支持快速搜索
"""
import os
import re
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import KNOWLEDGE_BASE_DIR, TOP_K_RESULTS, MIN_RELEVANCE_SCORE


class KnowledgeIndex:
    """知识库索引：加载md文件 → 分段 → TF-IDF向量化 → 余弦相似度搜索"""

    def __init__(self, knowledge_dir=None):
        self.knowledge_dir = knowledge_dir or KNOWLEDGE_BASE_DIR
        self.sections = []       # [{"title": "...", "content": "...", "file": "..."}]
        self.vectorizer = None
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        """构建索引"""
        print(f"[知识库] 正在加载目录: {self.knowledge_dir}")
        self._load_all_files()
        self._build_tfidf()
        print(f"[知识库] 索引构建完成! 共 {len(self.sections)} 个知识段落")

    def _load_all_files(self):
        """递归加载所有 .md 文件"""
        for root, dirs, files in os.walk(self.knowledge_dir):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    self._parse_markdown(filepath)

    def _parse_markdown(self, filepath):
        """解析单个 Markdown 文件，按标题分段"""
        filename = os.path.basename(filepath).replace('.md', '')

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"[警告] 无法读取文件 {filepath}: {e}")
            return

        # 按二级/三级标题分段
        sections = re.split(r'\n(?=#{2,3}\s)', content)

        for section in sections:
            section = section.strip()
            if not section or len(section) < 20:
                continue

            # 提取标题
            title_match = re.match(r'^(#{2,3})\s+(.+)', section)
            title = title_match.group(2) if title_match else filename

            # 清理 Markdown 语法（保留文字内容）
            clean_text = self._clean_markdown(section)

            if len(clean_text) > 10:
                self.sections.append({
                    "title": title,
                    "content": section,          # 保留原始 Markdown (显示用)
                    "clean_text": clean_text,    # 清理后文本 (搜索用)
                    "file": filename
                })

    def _clean_markdown(self, text):
        """清理 Markdown 语法,只保留纯文本用于搜索"""
        # 移除代码块
        text = re.sub(r'```[\s\S]*?```', '', text)
        # 移除 mermaid 图
        text = re.sub(r'```mermaid[\s\S]*?```', '', text)
        # 移除行内代码
        text = re.sub(r'`[^`]*`', '', text)
        # 移除链接
        text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
        # 移除图片
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        # 移除标题标记
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        # 移除强调
        text = re.sub(r'\*{1,2}([^*]*)\*{1,2}', r'\1', text)
        text = re.sub(r'_{1,2}([^_]*)_{1,2}', r'\1', text)
        # 移除表格分隔线
        text = re.sub(r'\|[-:]+\|', '', text)
        # 移除 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _tokenize(self, text):
        """中文分词"""
        words = jieba.cut(text)
        # 过滤停用词和短词
        stop_words = {'的', '了', '是', '在', '和', '有', '就', '不', '也', '都',
                      '到', '说', '要', '会', '对', '这', '那', '个', '为', '什么',
                      '怎么', '如何', '可以', '能', '吗', '呢', '啊', '吧', '么'}
        return ' '.join(w for w in words if len(w) > 1 and w not in stop_words)

    def _build_tfidf(self):
        """构建 TF-IDF 矩阵"""
        # 对每个段落进行分词
        corpus = [self._tokenize(s["clean_text"]) for s in self.sections]

        # 构建 TF-IDF 向量
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),    # 支持双字词
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query, top_k=None):
        """
        搜索最相关的知识段落

        Args:
            query: 搜索关键词/问题
            top_k: 返回前N个结果

        Returns:
            [{"title", "content", "file", "score"}, ...]
        """
        if not query or not self.sections:
            return []

        top_k = top_k or TOP_K_RESULTS

        # 对查询进行分词和向量化
        query_tokenized = self._tokenize(query)
        query_vec = self.vectorizer.transform([query_tokenized])

        # 计算余弦相似度
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # 获取 top-k 结果
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = scores[idx]
            if score < MIN_RELEVANCE_SCORE:
                continue
            results.append({
                "title": self.sections[idx]["title"],
                "content": self.sections[idx]["content"],
                "file": self.sections[idx]["file"],
                "score": float(score)
            })

        return results


# 测试
if __name__ == "__main__":
    index = KnowledgeIndex()
    print("\n" + "="*50)
    print("知识库搜索测试")
    print("="*50)

    test_queries = [
        "HashMap底层原理",
        "TCP三次握手",
        "Redis分布式锁",
        "G1垃圾收集器",
        "Spring AOP",
    ]

    for q in test_queries:
        print(f"\n🔍 搜索: {q}")
        results = index.search(q)
        for i, r in enumerate(results):
            print(f"  [{i+1}] [{r['file']}] {r['title']} (相关度: {r['score']:.3f})")
