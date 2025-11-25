from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text using the LLM.
        
        Args:
            prompt: The input prompt for the LLM
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    async def generate_chat_completion(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate chat completion using the LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
        """
        pass

# Factory function to get the configured LLM provider
def get_llm_provider() -> LLMProvider:
    """
    Factory function to get the configured LLM provider.
    
    Returns:
        An instance of the configured LLM provider
    """
    from ..config import settings
    
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "gemini":
        from .gemini_adapter import GeminiAdapter
        return GeminiAdapter()
    elif provider == "openai":
        from .openai_adapter import OpenAIModelAdapter
        return OpenAIModelAdapter()
    elif provider == "ollama":
        from .ollama_adapter import OllamaAdapter
        return OllamaAdapter()
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
