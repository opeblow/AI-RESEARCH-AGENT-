"""Answer quality assessment model using PyTorch."""

import logging
import torch
import torch.nn as nn
from typing import Dict, List, Optional
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


class AnswerQualityAssessor(nn.Module):
    """
    Neural network model to assess answer quality based on:
    - Semantic similarity between question and answer
    - Answer length appropriateness
    - Information density
    - Source utilization
    """

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None
    ):
        super().__init__()
        
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = torch.device(device)
        
        self.encoder = SentenceTransformer(embedding_model, device=self.device)
        hidden_size = self.encoder.get_sentence_embedding_dimension()
        
        self.quality_head = nn.Sequential(
            nn.Linear(hidden_size + 4, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        ).to(self.device)
        
        self.to(self.device)
        logger.info("AnswerQualityAssessor initialized")

    def extract_features(
        self,
        question: str,
        answer: str,
        context_length: int,
        num_sources: int
    ) -> torch.Tensor:
        """Extract hand-crafted features for quality assessment."""
        answer_len = len(answer.split())
        question_len = len(question.split())
        
        length_ratio = answer_len / max(question_len, 1)
        length_score = min(1.0, answer_len / 50)
        
        info_density = context_length / max(answer_len, 1)
        source_util = min(1.0, num_sources / 5)
        
        features = torch.tensor([
            length_ratio,
            length_score,
            info_density,
            source_util
        ], dtype=torch.float32).to(self.device)
        
        return features

    def forward(
        self,
        question: str,
        answer: str,
        context_length: int,
        num_sources: int
    ) -> Dict[str, float]:
        """
        Assess answer quality.
        
        Returns:
            Dictionary with quality score and components
        """
        q_emb = self.encoder.encode([question])
        a_emb = self.encoder.encode([answer])
        
        semantic_sim = util.cos_sim(q_emb, a_emb).item()
        
        features = self.extract_features(
            question, answer, context_length, num_sources
        )
        
        combined = torch.cat([
            q_emb,
            a_emb,
            features.unsqueeze(0)
        ], dim=-1)
        
        quality_score = self.quality_head(combined).item()
        
        return {
            "overall_quality": quality_score,
            "semantic_similarity": semantic_sim,
            "length_score": features[1].item(),
            "info_density": features[2].item(),
            "source_utilization": features[3].item()
        }

    @torch.no_grad()
    def assess(
        self,
        question: str,
        answer: str,
        context_length: int = 0,
        num_sources: int = 0
    ) -> Dict:
        """Assess answer quality (no grad context)."""
        return self.forward(question, answer, context_length, num_sources)


class ConfidenceCalibrator:
    """Calibrates confidence scores using temperature scaling."""

    def __init__(self, temperature: float = 1.0):
        self.temperature = temperature

    def calibrate(self, raw_score: float) -> float:
        """Apply temperature scaling to raw confidence."""
        import math
        logits = math.log(raw_score / (1 - raw_score + 1e-10))
        scaled = 1 / (1 + math.exp(-logits / self.temperature))
        return scaled

    def set_temperature(self, temperature: float):
        """Update temperature parameter."""
        self.temperature = temperature
