"""
Causal Engine: Production Asynchronous Client for Meta Llama API.
Supports official Meta models and gateways:
- Llama-3.2-11B-Vision-Instruct / Muse Spark (Multimodal Forensic Vision)
- Llama-3.2-3B-Instruct / Muse Spark Contributor (Fast Inference / Lexical Classification)
- Llama-3.3-70B-Instruct / Muse Spark 1.3 (Deep Causal Reasoning, Social Twins, and MCTS)
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Union
import httpx
from app.config import get_settings

logger = logging.getLogger("MirrorFuture.MetaLlamaAPI")
logging.basicConfig(level=logging.INFO)


class MetaLlamaAPIError(Exception):
    """Base exception for Meta Llama API communication failures."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class MetaLlamaClient:
    """
    Robust asynchronous client for interacting with official Meta Llama 3.2 and 3.3 models.
    Compatible with Meta Direct Endpoint (api.meta.ai), Together AI, Groq, Nebius, and vLLM.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        settings = get_settings()
        self.api_key = api_key or settings.meta_llama_api_key
        raw_base = (base_url or settings.meta_llama_base_url or "").rstrip("/")
        # Official Meta migration: automatically redirect retired domains
        if "api.llama.com" in raw_base.lower():
            raw_base = "https://api.meta.ai/v1"
        self.base_url = raw_base
        self.timeout = timeout or settings.timeout_seconds

        # Configured model references
        self.vision_model_raw = settings.llama_vision_model
        self.fast_model_raw = settings.llama_fast_model
        self.reasoning_model_raw = settings.llama_reasoning_model
        self.image_model_raw = getattr(settings, "llama_image_model", "muse-image-1.0")
        self.embedding_model = settings.llama_embedding_model

    def _resolve_model_name(self, requested_model: str) -> str:
        """
        Normalizes model identifiers according to active gateway provider:
        - Meta Model API (api.meta.ai): Muse Series (muse-spark-1.3, muse-image-1.0, muse-wonder-1.0, sam-3.1)
        - Groq: llama-3.3-70b-versatile, llama-3.2-11b-vision-preview
        - Together AI: meta-llama/Llama-3.3-70B-Instruct
        """
        base_lower = self.base_url.lower()
        is_meta_ai = "api.meta.ai" in base_lower or "llama.com" in base_lower
        is_groq = "groq.com" in base_lower

        req_clean = (requested_model or "").strip()
        req_lower = req_clean.lower()

        if is_meta_ai:
            if "image" in req_lower:
                return "muse-image-1.0"
            if "wonder" in req_lower:
                return "muse-wonder-1.0"
            if "contributor" in req_lower or "fast" in req_lower or "3b" in req_lower:
                return "muse-spark-1.3-contributor"
            if "transcribe" in req_lower or "voice" in req_lower or "audio" in req_lower:
                return "muse-voice-transcribe-1.0"
            if "sam" in req_lower or "segment" in req_lower:
                return "sam-3.1"
            if req_lower.startswith("muse-"):
                return req_clean
            # Default flagship for multimodal vision and causal reasoning
            return "muse-spark-1.3"

        if "vision" in req_lower:
            if is_groq:
                return "llama-3.2-11b-vision-preview"
            return "meta-llama/Llama-3.2-11B-Vision-Instruct"

        if "3b" in req_lower or "fast" in req_lower or "contributor" in req_lower:
            if is_groq:
                return "llama-3.2-3b-preview"
            return "meta-llama/Llama-3.2-3B-Instruct"

        if "70b" in req_lower or "reasoning" in req_lower or "3.3" in req_lower or "spark" in req_lower:
            if is_groq:
                return "llama-3.3-70b-versatile"
            return "meta-llama/Llama-3.3-70B-Instruct"

        return req_clean or "muse-spark-1.3"

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Executes an asynchronous chat completion request conforming to OpenAI / Meta format.
        """
        target_model = self._resolve_model_name(model or self.reasoning_model_raw)
        endpoint = f"{self.base_url}/chat/completions"

        payload: Dict[str, Any] = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(endpoint, headers=self._get_headers(), json=payload)
                if response.status_code == 200:
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices and len(choices) > 0:
                        content = choices[0].get("message", {}).get("content", "")
                        return content
                    raise MetaLlamaAPIError("Empty response returned from Meta Llama endpoint")
                else:
                    logger.error(f"Meta Llama API error {response.status_code}: {response.text}")
                    raise MetaLlamaAPIError(
                        f"HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                        response_body=response.text
                    )
            except httpx.RequestError as exc:
                logger.error(f"Network error communicating with Meta Llama API: {exc}")
                raise MetaLlamaAPIError(f"Network error: {str(exc)}")

    async def structured_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """
        Guarantees extraction and deserialization of a valid JSON object.
        Applies cleaning passes to remove Markdown code fences if returned by the LLM.
        """
        raw_content = await self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )

        cleaned = raw_content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Isolate outermost curly braces
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1:
            cleaned = cleaned[first_brace:last_brace + 1]

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to decode JSON from Meta Llama: {exc}\nRaw content:\n{raw_content}")
            raise MetaLlamaAPIError(f"Malformed JSON from LLM: {exc}", response_body=raw_content)


# Default singleton instance
llama_client = MetaLlamaClient()
