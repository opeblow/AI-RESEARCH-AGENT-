"""Document relevance classifier using PyTorch and sentence-transformers."""

import logging
import torch
import torch.nn as nn
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


class RelevanceClassifier(nn.Module):
    """Neural network classifier for document relevance scoring."""

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None
    ):
        super().__init__()
        
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        
        logger.info(f"Loading embedding model: {embedding_model}")
        self.encoder = SentenceTransformer(embedding_model, device=self.device)
        
        hidden_size = self.encoder.get_sentence_embedding_dimension()
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 3, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, 1),
            nn.Sigmoid()
        ).to(self.device)
        
        self.to(self.device)
        logger.info(f"RelevanceClassifier initialized on {self.device}")

    def encode(self, texts: List[str]) -> torch.Tensor:
        """Encode texts to embeddings."""
        embeddings = self.encoder.encode(
            texts,
            convert_to_tensor=True,
            show_progress_bar=False
        )
        return embeddings

    def forward(
        self,
        query: str,
        documents: List[str]
    ) -> torch.Tensor:
        """
        Compute relevance scores for documents given a query.
        
        Args:
            query: The search/query text
            documents: List of document texts to score
            
        Returns:
            Tensor of relevance scores [0, 1] for each document
        """
        query_emb = self.encode([query])
        doc_embs = self.encode(documents)
        
        similarities = util.cos_sim(query_emb, doc_embs)
        
        concatenated = torch.cat([
            query_emb.unsqueeze(1).expand(-1, len(documents), -1),
            doc_embs.unsqueeze(0).expand(len(documents), -1, -1),
            similarities.unsqueeze(-1)
        ], dim=-1)
        
        scores = self.classifier(concatenated.squeeze(0))
        return scores.squeeze()

    def score_documents(
        self,
        query: str,
        documents: List[str]
    ) -> List[Tuple[int, float]]:
        """
        Score and rank documents by relevance.
        
        Returns:
            List of (index, score) tuples sorted by score descending
        """
        if not documents:
            return []
            
        scores = self.forward(query, documents)
        ranked = sorted(
            enumerate(scores.tolist()),
            key=lambda x: x[1],
            reverse=True
        )
        return ranked

    @torch.no_grad()
    def predict_relevant(
        self,
        query: str,
        documents: List[str],
        threshold: float = 0.5
    ) -> List[Tuple[int, float, bool]]:
        """
        Predict which documents are relevant with threshold.
        
        Returns:
            List of (index, score, is_relevant) tuples
        """
        scored = self.score_documents(query, documents)
        return [(idx, score, score >= threshold) for idx, score in scored]


class SimpleRelevanceScorer:
    """Lightweight relevance scorer using cosine similarity only."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        logger.info(f"SimpleRelevanceScorer initialized with {model_name}")

    def score(self, query: str, documents: List[str]) -> List[float]:
        """Compute cosine similarity scores."""
        query_emb = self.model.encode([query])
        doc_embs = self.model.encode(documents)
        similarities = util.cos_sim(query_emb, doc_embs)[0]
        return similarities.tolist()

    def get_top_k(
        self,
        query: str,
        documents: List[str],
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """Get top-k most relevant documents."""
        scores = self.score(query, documents)
        indexed = list(enumerate(scores))
        return sorted(indexed, key=lambda x: x[1], reverse=True)[:k]
