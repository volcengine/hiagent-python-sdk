"""aigw built-in base models (mirrors go/hibot/v1/base_models.go).

Generated from a real ListModelProvider call against the cluster.
"""

from __future__ import annotations

from dataclasses import dataclass

# Base model types
BASE_MODEL_TYPE_TEXT_GENERATION = "text-generation"
BASE_MODEL_TYPE_EMBEDDINGS = "embeddings"
BASE_MODEL_TYPE_VISION = "vision"
BASE_MODEL_TYPE_AUDIO = "audio"
BASE_MODEL_TYPE_RERANKING = "reranking"

# Base model providers
BASE_MODEL_PROVIDER_VOLCENGINE = "volcengine"
BASE_MODEL_PROVIDER_BYTEPLUS = "byteplus"
BASE_MODEL_PROVIDER_VOLCENGINE_AICC = "volcengine_aicc"
BASE_MODEL_PROVIDER_ZHIPU = "zhipu"
BASE_MODEL_PROVIDER_KIMI = "kimi"
BASE_MODEL_PROVIDER_MINIMAX = "minimax"
BASE_MODEL_PROVIDER_DEEPSEEK = "deepseek"
BASE_MODEL_PROVIDER_AWS = "aws"
BASE_MODEL_PROVIDER_AZURE_OPENAI = "azure_openai"
BASE_MODEL_PROVIDER_OPENAI = "openai"
BASE_MODEL_PROVIDER_TONGYI = "tongyi"
BASE_MODEL_PROVIDER_WENXIN = "wenxin"
BASE_MODEL_PROVIDER_GOOGLE = "google"
BASE_MODEL_PROVIDER_ANTHROPIC = "anthropic"
BASE_MODEL_PROVIDER_LOCALAI = "localai"


@dataclass(frozen=True)
class BaseModel:
    provider: str
    type: str
    model_name: str


BASE_MODELS = [
    BaseModel("azure_openai", "embeddings", "text-embedding-3-large"),
    BaseModel("azure_openai", "embeddings", "text-embedding-3-small"),
    BaseModel("azure_openai", "embeddings", "text-embedding-ada-002"),
    BaseModel("azure_openai", "text-generation", "gpt-4"),
    BaseModel("azure_openai", "text-generation", "gpt-4o-mini"),
    BaseModel("azure_openai", "text-generation", "o1"),
    BaseModel("azure_openai", "text-generation", "o1-preview"),
    BaseModel("byteplus", "audio", "seed-tts-1.0"),
    BaseModel("byteplus", "audio", "seed-tts-2.0"),
    BaseModel("byteplus", "audio", "volc.bigasr.sauc.duration"),
    BaseModel("byteplus", "audio", "volc.seedasr.sauc.duration"),
    BaseModel("byteplus", "text-generation", "deepseek-v3"),
    BaseModel("byteplus", "text-generation", "deepseek-v3-2-251201"),
    BaseModel("byteplus", "text-generation", "glm-4-7-251222"),
    BaseModel("byteplus", "text-generation", "kimi-k2-thinking-251104"),
    BaseModel("byteplus", "text-generation", "seed-1-6-250615"),
    BaseModel("byteplus", "text-generation", "seed-1-6-flash-250615"),
    BaseModel("byteplus", "text-generation", "seed-1-8-251228"),
    BaseModel("byteplus", "text-generation", "seed-2-0-lite-260228"),
    BaseModel("byteplus", "text-generation", "seed-2-0-mini-260215"),
    BaseModel("byteplus", "text-generation", "seed-2-0-pro-260328"),
    BaseModel("byteplus", "vision", "dreamina-seedance-2-0-260128"),
    BaseModel("byteplus", "vision", "dreamina-seedance-2-0-fast-260128"),
    BaseModel("byteplus", "vision", "seedream-5.0-lite-260128"),
    BaseModel("kimi", "text-generation", "kimi-k2.5"),
    BaseModel("minimax", "text-generation", "minimax-m2.5"),
    BaseModel("minimax", "text-generation", "minimax-m2.7"),
    BaseModel("openai", "embeddings", "text-embedding-3-large"),
    BaseModel("openai", "embeddings", "text-embedding-3-small"),
    BaseModel("openai", "embeddings", "text-embedding-ada-002"),
    BaseModel("openai", "text-generation", "gpt-3.5-turbo"),
    BaseModel("openai", "text-generation", "gpt-4"),
    BaseModel("openai", "text-generation", "gpt-4o"),
    BaseModel("openai", "text-generation", "gpt-4o-mini"),
    BaseModel("openai", "text-generation", "gpt-5"),
    BaseModel("openai", "text-generation", "gpt-5-chat-latest"),
    BaseModel("openai", "text-generation", "gpt-5-mini"),
    BaseModel("openai", "text-generation", "gpt-5-nano"),
    BaseModel("openai", "text-generation", "o1"),
    BaseModel("openai", "text-generation", "o1-mini"),
    BaseModel("openai", "text-generation", "o1-preview"),
    BaseModel("tongyi", "embeddings", "qwen3-vl-embedding"),
    BaseModel("tongyi", "embeddings", "text-embedding-v1"),
    BaseModel("tongyi", "embeddings", "text-embedding-v2"),
    BaseModel("tongyi", "reranking", "qwen3-rerank"),
    BaseModel("tongyi", "text-generation", "qwen-plus-latest"),
    BaseModel("tongyi", "text-generation", "qwen-turbo-latest"),
    BaseModel("tongyi", "text-generation", "qwen3-0.6b"),
    BaseModel("tongyi", "text-generation", "qwen3-1.7b"),
    BaseModel("tongyi", "text-generation", "qwen3-14b"),
    BaseModel("tongyi", "text-generation", "qwen3-235b-a22b"),
    BaseModel("tongyi", "text-generation", "qwen3-30b-a3b"),
    BaseModel("tongyi", "text-generation", "qwen3-32b"),
    BaseModel("tongyi", "text-generation", "qwen3-4b"),
    BaseModel("tongyi", "text-generation", "qwen3-8b"),
    BaseModel("volcengine", "audio", "seed-tts-2.0"),
    BaseModel("volcengine", "audio", "volc.bigasr.auc_turbo"),
    BaseModel("volcengine", "audio", "volc.seedasr.sauc.duration"),
    BaseModel("volcengine", "text-generation", "deepseek-v3-2-251201"),
    BaseModel("volcengine", "text-generation", "doubao-1-5-lite"),
    BaseModel("volcengine", "text-generation", "doubao-seed-2-0-code-preview-260215"),
    BaseModel("volcengine", "text-generation", "doubao-seed-2-0-lite-260215"),
    BaseModel("volcengine", "text-generation", "doubao-seed-2-0-mini-260215"),
    BaseModel("volcengine", "text-generation", "doubao-seed-2-0-pro-260215"),
    BaseModel("volcengine", "text-generation", "glm-4-7-251222"),
    BaseModel("volcengine", "vision", "doubao-seedance-2-0-260128"),
    BaseModel("volcengine", "vision", "doubao-seedance-2-0-fast-260128"),
    BaseModel("volcengine_aicc", "text-generation", "deepseek-v3-2-251201"),
    BaseModel("volcengine_aicc", "text-generation", "doubao-seed-1-6-250615"),
    BaseModel("volcengine_aicc", "text-generation", "doubao-seed-2-0-lite-260215"),
    BaseModel("volcengine_aicc", "text-generation", "doubao-seed-2-0-pro-260215"),
    BaseModel("volcengine_aicc", "text-generation", "glm-4-7-251222"),
    BaseModel("zhipu", "text-generation", "glm-3-turbo"),
    BaseModel("zhipu", "text-generation", "glm-4"),
    BaseModel("zhipu", "text-generation", "glm-4v"),
    BaseModel("zhipu", "text-generation", "glm-5"),
    BaseModel("zhipu", "text-generation", "glm-5.1"),
]
