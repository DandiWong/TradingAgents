"""
Embedding package for TradingAgents.
Provides multi-provider embedding support.
"""

from .embedding_manager import (
    EmbeddingProvider,
    OpenAIEmbeddingProvider,
    GoogleEmbeddingProvider,
    OpenRouterEmbeddingProvider,
    MockEmbeddingProvider,
    EmbeddingManager
)

__all__ = [
    "EmbeddingProvider",
    "OpenAIEmbeddingProvider", 
    "GoogleEmbeddingProvider",
    "OpenRouterEmbeddingProvider",
    "MockEmbeddingProvider",
    "EmbeddingManager"
]