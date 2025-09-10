"""
Embedding provider manager for TradingAgents.
Supports multiple embedding providers including OpenAI, OpenRouter, Google, etc.
"""

import os
from typing import List, Union, Optional, Dict, Any
from abc import ABC, abstractmethod
import numpy as np


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text."""
        pass
    
    @abstractmethod
    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider."""
    
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = "", base_url: str = "https://api.openai.com/v1"):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.client = None
        
    def _get_client(self):
        """Lazy initialize OpenAI client."""
        if self.client is None:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                raise ImportError("openai package is required for OpenAI embeddings")
        
        return self.client
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text using OpenAI."""
        client = self._get_client()
        response = client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding
    
    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts using OpenAI."""
        client = self._get_client()
        response = client.embeddings.create(model=self.model, input=texts)
        return [data.embedding for data in response.data]


class GoogleEmbeddingProvider(EmbeddingProvider):
    """Google Gemini embedding provider."""
    
    def __init__(self, model: str = "models/embedding-001", api_key: str = ""):
        self.model = model
        self.api_key = api_key
        self.client = None
        
    def _get_client(self):
        """Lazy initialize Google embeddings client."""
        if self.client is None:
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                self.client = GoogleGenerativeAIEmbeddings(
                    model=self.model,
                    google_api_key=self.api_key
                )
            except ImportError:
                raise ImportError("langchain-google-genai package is required for Google embeddings")
        
        return self.client
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text using Google."""
        client = self._get_client()
        embedding = client.embed_query(text)
        return embedding
    
    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts using Google."""
        client = self._get_client()
        embeddings = client.embed_documents(texts)
        return embeddings


class OpenRouterEmbeddingProvider(OpenAIEmbeddingProvider):
    """OpenRouter embedding provider (compatible with OpenAI API)."""
    
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = ""):
        super().__init__(
            model=model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )


class MockEmbeddingProvider(EmbeddingProvider):
    """Mock embedding provider for testing and fallback."""
    
    def __init__(self, embedding_dim: int = 1536):
        self.embedding_dim = embedding_dim
        
    def get_embedding(self, text: str) -> List[float]:
        """Generate mock embedding based on text hash."""
        # Simple hash-based embedding for demonstration
        np.random.seed(hash(text) % 2**32)
        return np.random.randn(self.embedding_dim).tolist()
    
    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for multiple texts."""
        return [self.get_embedding(text) for text in texts]


class EmbeddingManager:
    """Manager for embedding providers."""
    
    def __init__(self, config: Dict[str, Any]):
        # Handle both flat config (with _full_config) and full config
        if "_full_config" in config:
            self.config = config["_full_config"]
        else:
            self.config = config
        self.provider = self._create_provider()
        
    def _create_provider(self) -> EmbeddingProvider:
        """Create embedding provider based on configuration."""
        # Check if embeddings are enabled
        embedding_settings = self.config.get("embedding_settings", {})
        if not embedding_settings.get("enabled", True):
            print("Embeddings disabled, using mock provider")
            return MockEmbeddingProvider()
        
        # Get provider name
        provider_name = self.config.get("llm_provider", "openai")
        
        # Get provider-specific configuration
        provider_config = self.config.get("llm_providers", {}).get(provider_name, {})
        api_key = provider_config.get("api_key", "")
        
        # Check if API key is available
        if not api_key or api_key.strip() in ["", "your-api-key-here"]:
            print(f"Warning: No API key for provider '{provider_name}', using mock provider")
            return MockEmbeddingProvider()
        
        # Create appropriate provider
        try:
            if provider_name in ["openai", "openrouter"]:
                model = "text-embedding-3-small"
                if provider_name == "openrouter":
                    return OpenRouterEmbeddingProvider(model=model, api_key=api_key)
                else:
                    return OpenAIEmbeddingProvider(model=model, api_key=api_key)
                    
            elif provider_name == "google":
                return GoogleEmbeddingProvider(api_key=api_key)
                
            else:
                # Fallback to mock provider for unsupported providers
                print(f"Warning: Embedding provider '{provider_name}' not supported, using mock provider")
                return MockEmbeddingProvider()
                
        except Exception as e:
            print(f"Error creating embedding provider '{provider_name}': {e}")
            if embedding_settings.get("fallback_to_mock", True):
                print("Falling back to mock provider")
                return MockEmbeddingProvider()
            else:
                raise
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text."""
        try:
            return self.provider.get_embedding(text)
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Fallback to mock embedding
            mock_provider = MockEmbeddingProvider()
            return mock_provider.get_embedding(text)
    
    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        try:
            return self.provider.get_batch_embeddings(texts)
        except Exception as e:
            print(f"Error getting batch embeddings: {e}")
            # Fallback to mock embeddings
            mock_provider = MockEmbeddingProvider()
            return mock_provider.get_batch_embeddings(texts)