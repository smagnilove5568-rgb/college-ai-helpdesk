from rank_bm25 import BM25Okapi


class HybridSearch:
    def __init__(self, documents):

        self.documents = documents

        corpus = [doc.page_content.split() for doc in documents]

        self.bm25 = BM25Okapi(corpus)

    def keyword_search(self, query, k=3):

        tokens = query.split()

        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return [doc for doc, score in ranked[:k]]