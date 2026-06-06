"""Free LLM Fallback - Integration with free LLM API resources

Reference: https://github.com/cheahjs/free-llm-api-resources
"""

import logging
from typing import Optional, Dict, Any
import aiohttp
import asyncio

logger = logging.getLogger(__name__)


class FreeLLMFallback:
    """
    Integration with free LLM API resources.
    
    Supported services (Phase 2):
    - GPT4Free (various providers)
    - Replicate API (free tier)
    - Hugging Face Inference API (free)
    - Together AI (free credits)
    """

    def __init__(self):
        self.current_provider = None
        self.session = None
        self.fallback_order = [
            "huggingface",
            "replicate",
            "together_ai"
        ]
        logger.info("FreeLLMFallback initialized")

    async def initialize(self):
        """Initialize async session"""
        self.session = aiohttp.ClientSession()

    async def cleanup(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate text using free LLM service.
        Tries multiple providers as fallback.
        """
        logger.info(f"Attempting free LLM generation")
        
        for provider in self.fallback_order:
            try:
                if provider == "huggingface":
                    result = await self._generate_huggingface(prompt, max_tokens, temperature)
                elif provider == "replicate":
                    result = await self._generate_replicate(prompt, max_tokens, temperature)
                elif provider == "together_ai":
                    result = await self._generate_together(prompt, max_tokens, temperature)
                else:
                    continue
                
                if result:
                    self.current_provider = provider
                    logger.info(f"Generated using {provider}")
                    return result
            
            except Exception as e:
                logger.warning(f"{provider} failed: {str(e)}. Trying next provider...")
                continue
        
        logger.error("All free LLM providers failed")
        return None

    async def _generate_huggingface(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Optional[str]:
        """
        Generate using Hugging Face Inference API (free tier).
        Requires HF_API_KEY environment variable.
        
        Model: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1
        """
        import os
        api_key = os.getenv("HF_API_KEY")
        
        if not api_key:
            logger.warning("HF_API_KEY not set")
            return None
        
        try:
            url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature
                }
            }
            
            async with self.session.post(url, json=payload, headers=headers, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and len(data) > 0:
                        return data[0].get("generated_text", "")
        
        except Exception as e:
            logger.error(f"HuggingFace error: {str(e)}")
        
        return None

    async def _generate_replicate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Optional[str]:
        """
        Generate using Replicate API (free credits).
        Requires REPLICATE_API_TOKEN environment variable.
        """
        import os
        api_token = os.getenv("REPLICATE_API_TOKEN")
        
        if not api_token:
            logger.warning("REPLICATE_API_TOKEN not set")
            return None
        
        try:
            url = "https://api.replicate.com/v1/predictions"
            headers = {
                "Authorization": f"Token {api_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "version": "8abccf52e7c14ce6eb5c2b2debb9ba20ea4b503f",  # Llama-7b
                "input": {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            }
            
            async with self.session.post(url, json=payload, headers=headers, timeout=30) as resp:
                if resp.status in [201, 200]:
                    data = await resp.json()
                    # Poll for completion
                    prediction_id = data["id"]
                    return await self._poll_replicate(prediction_id, api_token)
        
        except Exception as e:
            logger.error(f"Replicate error: {str(e)}")
        
        return None

    async def _poll_replicate(self, prediction_id: str, api_token: str) -> Optional[str]:
        """Poll Replicate for prediction status"""
        url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
        headers = {"Authorization": f"Token {api_token}"}
        
        for _ in range(30):  # Poll up to 30 times
            try:
                async with self.session.get(url, headers=headers, timeout=10) as resp:
                    data = await resp.json()
                    if data["status"] == "succeeded":
                        return "".join(data["output"])
                    elif data["status"] == "failed":
                        return None
                
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Poll error: {str(e)}")
                return None
        
        return None

    async def _generate_together(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Optional[str]:
        """
        Generate using Together AI (free credits).
        Requires TOGETHER_API_KEY environment variable.
        """
        import os
        api_key = os.getenv("TOGETHER_API_KEY")
        
        if not api_key:
            logger.warning("TOGETHER_API_KEY not set")
            return None
        
        try:
            url = "https://api.together.xyz/inference"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "togethercomputer/llama-7b-chat",
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 50,
                "repetition_penalty": 1.0
            }
            
            async with self.session.post(url, json=payload, headers=headers, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data[0].get("generated_text", "")
        
        except Exception as e:
            logger.error(f"Together AI error: {str(e)}")
        
        return None
