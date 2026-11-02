"""
Central configuration and environment variables for Mirror Future.
Staff AI grade architecture: typed validation via Pydantic Settings,
support for multiple Meta Llama API gateways (Together AI, Groq, Meta Direct, vLLM),
and secure connections to Supabase pgvector and Meta WhatsApp Cloud API.
"""

import os
from functools import lru_cache
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

_backend_dir = Path(__file__).resolve().parent.parent
_root_dir = _backend_dir.parent
load_dotenv(_backend_dir / ".env")
load_dotenv(_root_dir / ".env")
load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[str(_backend_dir / ".env"), str(_root_dir / ".env"), ".env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # --- Meta Llama API Config ---
    # Supports official Meta endpoint or high-throughput gateways (Together AI, Groq, Nebius, vLLM)
    meta_llama_api_key: str = Field(
        default_factory=lambda: (
            os.getenv("META_LLAMA_API_KEY")
            or os.getenv("TOGETHER_API_KEY")
            or os.getenv("GROQ_API_KEY")
            or os.getenv("LLAMA_API_KEY")
            or ""
        ),
        description="API key for Meta Llama inference engine"
    )
    meta_llama_base_url: str = Field(
        default_factory=lambda: (
            os.getenv("META_LLAMA_BASE_URL")
            or (
                "https://api.groq.com/openai/v1"
                if os.getenv("GROQ_API_KEY")
                else (
                    "https://api.meta.ai/v1"
                    if os.getenv("META_LLAMA_API_KEY")
                    else "https://api.together.xyz/v1"
                )
            )
        ),
        description="Base URL compatible with Meta / OpenAI API specification"
    )

    # Official Meta Models (Muse Series & Llama)
    together_api_key: str = Field(
        default_factory=lambda: os.getenv("TOGETHER_API_KEY", ""),
        description="Optional Together AI API key for Flux / Muse image generation"
    )
    llama_vision_model: str = Field(
        default="muse-spark-1.3",
        description="Multimodal vision model for biometric and forensic feature inspection (Muse Spark 1.3 / Llama 3.2 Vision)"
    )
    llama_fast_model: str = Field(
        default="muse-spark-1.3-contributor",
        description="Low-latency agile model for rapid predictions and classification"
    )
    llama_reasoning_model: str = Field(
        default="muse-spark-1.3",
        description="Flagship model for causal reasoning, stochastic simulation, and discovery synthesis (Muse Spark 1.3 / Llama 3.3 70B)"
    )
    llama_image_model: str = Field(
        default="muse-image-1.0",
        description="Official image generation and editing model (Muse Image 1.0)"
    )
    llama_embedding_model: str = Field(
        default="togethercomputer/m2-bert-80M-8k-retrieval",
        description="Dense embedding model for episodic retrieval in Supabase pgvector"
    )

    # --- Supabase Database & pgvector ---
    supabase_url: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_URL", "https://your-project.supabase.co"),
        description="Supabase project base URL"
    )
    supabase_key: str = Field(
        default_factory=lambda: (
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or ""
        ),
        description="Supabase Service Role Key or API Key for RPC and vector retrieval"
    )

    # --- Meta WhatsApp Cloud API ---
    whatsapp_api_token: str = Field(
        default_factory=lambda: os.getenv("WHATSAPP_API_TOKEN", ""),
        description="Meta Graph API permanent bearer token"
    )
    whatsapp_phone_number_id: str = Field(
        default_factory=lambda: os.getenv("WHATSAPP_PHONE_NUMBER_ID", ""),
        description="Phone number ID registered in Meta Business Manager"
    )
    whatsapp_business_account_id: str = Field(
        default_factory=lambda: os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", ""),
        description="WABA ID (WhatsApp Business Account ID)"
    )
    whatsapp_api_version: str = Field(
        default="v21.0",
        description="Meta Graph API version"
    )
    whatsapp_base_url: str = Field(
        default="https://graph.facebook.com",
        description="Meta Graph API base URL"
    )

    # --- Environment & Operations ---
    app_env: str = Field(default="production", description="development / staging / production")
    debug: bool = Field(default=False)
    timeout_seconds: float = Field(default=60.0, description="HTTP timeout for LLM and vision calls")


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton instance of system configuration settings."""
    return Settings()
