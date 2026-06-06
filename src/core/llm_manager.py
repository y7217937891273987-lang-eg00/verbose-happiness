"""LLM Manager - Routes requests to Ollama (local) or OpenAI"""

import asyncio
import os
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
import json

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Available LLM providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    FREE_API = "free_api"  # Free LLM API (Phase 2)


class LLMManager:
    """
    Manages LLM interactions.
    Supports:
    - Ollama (local, free, ~4GB)
    - OpenAI API (requires API key, paid)
    - Free LLM APIs (fallback)
    """

    def __init__(
        self,
        primary_provider: LLMProvider = LLMProvider.OLLAMA,
        ollama_host: str = "http://localhost:11434",
        ollama_model: str = "mistral",  # or "neural-chat", "orca"
        openai_api_key: Optional[str] = None,
        openai_model: str = "gpt-3.5-turbo"
    ):
        self.primary_provider = primary_provider
        self.ollama_host = ollama_host
        self.ollama_model = ollama_model
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.conversation_history: List[Dict[str, str]] = []
        
        logger.info(f"LLMManager initialized with primary provider: {primary_provider.value}")

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        provider: Optional[LLMProvider] = None
    ) -> str:
        """
        Generate text using the configured LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: System context (optional)
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            provider: Override default provider
        
        Returns:
            Generated text response
        """
        provider = provider or self.primary_provider
        
        try:
            if provider == LLMProvider.OLLAMA:
                return await self._generate_ollama(prompt, system_prompt, temperature, max_tokens)
            elif provider == LLMProvider.OPENAI:
                return await self._generate_openai(prompt, system_prompt, temperature, max_tokens)
            elif provider == LLMProvider.FREE_API:
                return await self._generate_free_api(prompt, system_prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"Error generating with {provider.value}: {str(e)}")
            # Fallback to alternative provider
            if provider != LLMProvider.OLLAMA:
                logger.info("Falling back to Ollama")
                return await self._generate_ollama(prompt, system_prompt, temperature, max_tokens)
            raise

    async def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """
        Generate using Ollama (local LLM).
        Requires Ollama to be running: https://ollama.ai
        """
        try:
            import requests
        except ImportError:
            logger.error("requests library not installed")
            raise
        
        logger.info(f"Generating with Ollama ({self.ollama_model})")
        
        # Check if Ollama is running
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=2)
            if response.status_code != 200:
                raise Exception("Ollama server not responding correctly")
        except Exception as e:
            logger.error(f"Ollama not available: {str(e)}. Is it running?")
            raise
        
        # Prepare the full prompt
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        # Call Ollama API
        payload = {
            "model": self.ollama_model,
            "prompt": full_prompt,
            "temperature": temperature,
            "stream": False
        }
        
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=300  # Long timeout for response
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API error: {str(e)}")
            raise

    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """
        Generate using OpenAI API.
        Requires OPENAI_API_KEY environment variable or initialization parameter.
        """
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            if not self.openai_api_key:
                raise Exception(
                    "OpenAI API key not configured. "
                    "Set OPENAI_API_KEY environment variable or pass during initialization."
                )
        
        logger.info(f"Generating with OpenAI ({self.openai_model})")
        
        try:
            from openai import AsyncOpenAI
        except ImportError:
            logger.error("openai library not installed")
            raise
        
        client = AsyncOpenAI(api_key=self.openai_api_key)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    async def _generate_free_api(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """
        Generate using free LLM APIs.
        Check: https://github.com/cheahjs/free-llm-api-resources
        Phase 2 implementation.
        """
        logger.info("Free API support coming in Phase 2")
        raise NotImplementedError("Free API support will be added in Phase 2")

    async def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        clear_history: bool = False
    ) -> str:
        """
        Chat with conversation history.
        """
        if clear_history:
            self.conversation_history = []
        
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Generate response
        response = await self.generate(user_message, system_prompt)
        
        # Add assistant response to history
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current LLM provider"""
        info = {
            "primary_provider": self.primary_provider.value,
            "conversation_history_length": len(self.conversation_history)
        }
        
        if self.primary_provider == LLMProvider.OLLAMA:
            info["ollama_host"] = self.ollama_host
            info["ollama_model"] = self.ollama_model
        elif self.primary_provider == LLMProvider.OPENAI:
            info["openai_model"] = self.openai_model
            info["api_key_configured"] = bool(self.openai_api_key)
        
        return info
