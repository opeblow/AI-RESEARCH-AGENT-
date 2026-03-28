"""Semantic similarity module."""

import logging
import numpy as np
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


class SemanticSimilarity:
    """Semantic similarity computation using sentence transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading similarity model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings."""
        return self.model.encode(texts, show_progress_bar=False)

    def cosine_similarity(self, text1: str, text2: str) -> float:
        """Compute cosine similarity between two texts."""
        emb1 = self.encode([text1])
        emb2 = self.encode([text2])
        sim = util.cos_sim(emb1, emb2)[0][0].item()
        return sim

    def batch_similarity(
        self,
        query: str,
        documents: List[str]
    ) -> List[float]:
        """Compute similarity between query and list of documents."""
        query_emb = self.encode([query])
        doc_embs = self.encode(documents)
        similarities = util.cos_sim(query_emb, doc_embs)[0]
        return similarities.tolist()

    def find_most_similar(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[Tuple[int, float, str]]:
        """
        Find most similar documents to query.
        
        Returns:
            List of (index, score, document) tuples
        """
        similarities = self.batch_similarity(query, documents)
        
        results = []
        for idx, score in enumerate(similarities):
            if score >= threshold:
                results.append((idx, score, documents[idx]))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def compute_embedding_stats(self, texts: List[str]) -> dict:
        """Compute statistics about embeddings."""
        embeddings = self.encode(texts)
        
        norms = np.linalg.norm(embeddings, axis=1)
        
        pairwise_sim = util.cos_sim(embeddings, embeddings)
        upper_tri = pairwise_sim[np.triu_indices(len(texts), k=1)]
        
        return {
            "num_documents": len(texts),
            "embedding_dim": self.embedding_dim,
            "mean_norm": float(np.mean(norms)),
            "std_norm": float(np.std(norms)),
            "mean_similarity": float(np.mean(upper_tri)),
            "std_similarity": float(np.std(upper_tri))
        }


class DiversityScorer:
    """Scores document diversity for better coverage."""

    def __init__(self, similarity_model: SemanticSimilarity):
        self.similarity = similarity_model

    def compute_diversity_score(
        self,
        documents: List[str],
        threshold: float = 0.7
    ) -> float:
        """
        Compute diversity score (1 = all different, 0 = all same).
        
        Higher score means more diverse documents.
        """
        if len(documents) <= 1:
            return 1.0
        
        embeddings = self.similarity.encode(documents)
        pairwise_sim = util.cos_sim(embeddings, embeddings)
        
        upper_tri = pairwise_sim[np.triu_indices(len(documents), k=1)]
        avg_sim = float(np.mean(upper_tri))
        
        diversity = 1 - avg_sim
        return max(0.0, diversity)

    def select_diverse_subset(
        self,
        documents: List[str],
        k: int = 5,
        threshold: float = 0.7
    ) -> List[int]:
        """
        Select k most diverse documents.
        
        Returns indices of selected documents.
        """
        if len(documents) <= k:
            return list(range(len(documents)))
        
        selected = [0]
        remaining = set(range(1, len(documents)))
        
        embeddings = self.similarity.encode(documents)
        
        while len(selected) < k and remaining:
            best_idx = None
            best_min_sim = float('inf')
            
            for idx in remaining:
                min_sim_to_selected = min(
                    util.cos_sim(embeddings[idx], embeddings[s])[0][0].item()
                    for s in selected
                )
                
                if min_sim_to_selected < best_min_sim:
                    best_min_sim = min_sim_to_selected
                    best_idx = idx
            
            if best_idx is not None and best_min_sim < threshold:
                selected.append(best_idx)
                remaining.remove(best_idx)
            else:
                break
        
        return selected
