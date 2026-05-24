"""
知识库索引模块
加载所有 Markdown 文件 → 分段 → TF-IDF 索引 → 余弦相似度搜索
"""
import os
import re
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import KNOWLEDGE_BASE_DIR, TOP_K_RESULTS, MIN_RELEVANCE_SCORE


class KnowledgeIndex:
    """知识库索引"""

    def __init__(self, knowledge_dir=None):
        self.knowledge_dir = knowledge_dir or KNOWLEDGE_BASE_DIR
        self.sections = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self._build_index()

    def _build_index(self):
        print(f"[知识库] 加载目录: {self.knowledge_dir}")
        self._load_all_files()
        if self.sections:
            self._build_tfidf()
        print(f"[知识库] 完成! 共 {len(self.sections)} 个段落")

    def _load_all_files(self):
        for root, dirs, files in os.walk(self.knowledge_dir):
            for file in files:
                if file.endswith('.md'):
                    self._parse_markdown(os.path.join(root, file))

    def _parse_markdown(self, filepath):
        filename = os.path.basename(filepath).replace('.md', '')
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"[警告] 无法读取 {filepath}: {e}")
            return

        sections = re.split(r'\n(?=#{2,3}\s)', content)
        for section in sections:
            section = section.strip()
            if not section or len(section) < 20:
                continue
            title_match = re.match(r'^(#{2,3})\s+(.+)', section)
            title = title_match.group(2) if title_match else filename
            clean_text = self._clean_markdown(section)
            if len(clean_text) > 10:
                self.sections.append({
                    "title": title,
                    "content": section,
                    "clean_text": clean_text,
                    "file": filename
                })

    def _clean_markdown(self, text):
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`[^`]*`', '', text)
        text = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', text)
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\*{1,2}([^*]*)\*{1,2}', r'\1', text)
        text = re.sub(r'\|[-:]+\|', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def _tokenize(self, text):
        # 先提取英文单词/技术术语(保持原样,不被jieba切碎)
        import re
        english_words = re.findall(r'[A-Za-z][A-Za-z0-9_\-\.]+', text)
        # 把英文术语的各种大小写形式都加进去
        english_tokens = []
        for w in english_words:
            english_tokens.append(w.lower())
            # CamelCase 拆分: ThreadLocal → thread, local
            parts = re.findall(r'[A-Z][a-z]+|[a-z]+|[A-Z]+', w)
            english_tokens.extend(p.lower() for p in parts if len(p) > 1)

        # 中文部分用jieba分词
        words = jieba.cut(text)
        stop_words = {'的', '了', '是', '在', '和', '有', '就', '不', '也', '都',
                      '到', '说', '要', '会', '对', '这', '那', '个', '为', '什么',
                      '怎么', '如何', '可以', '能', '吗', '呢', '啊', '吧', '么',
                      '一个', '使用', '通过', '进行', '以及', '或者', '但是'}
        chinese_tokens = [w for w in words if len(w) > 1 and w not in stop_words]

        all_tokens = chinese_tokens + english_tokens
        return ' '.join(all_tokens)

    def _build_tfidf(self):
        corpus = [self._tokenize(s["clean_text"]) for s in self.sections]
        self.vectorizer = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query, top_k=None):
        if not query or not self.sections:
            return []
        top_k = top_k or TOP_K_RESULTS

        # TF-IDF 相似度搜索
        query_tokenized = self._tokenize(query)
        query_vec = self.vectorizer.transform([query_tokenized])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # 标题/关键词精确匹配加权(大幅提升准确率)
        query_lower = query.lower()
        for i, section in enumerate(self.sections):
            title_lower = section['title'].lower()
            content_lower = section['clean_text'].lower()
            # 标题包含查询词 → 加大权重
            if query_lower in title_lower:
                scores[i] += 0.5
            # 内容中出现完整查询词 → 加权
            elif query_lower in content_lower:
                scores[i] += 0.3
            # 英文术语精确匹配(不区分大小写)
            import re
            query_words = re.findall(r'[A-Za-z][A-Za-z0-9_]+', query)
            for qw in query_words:
                if qw.lower() in title_lower or qw.lower() in content_lower:
                    scores[i] += 0.4

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
                "score": float(min(score, 1.0))
            })
        return results


if __name__ == "__main__":
    index = KnowledgeIndex()
    test_queries = ["HashMap底层原理", "TCP三次握手", "Redis分布式锁", "G1垃圾收集器"]
    for q in test_queries:
        print(f"\n🔍 {q}")
        for r in index.search(q):
            print(f"  [{r['file']}] {r['title']} ({r['score']:.2%})")
