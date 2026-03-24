import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

DATA_DIR = PROJECT_ROOT / "data"
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
OUTPUT_DIR = PROJECT_ROOT / "output"
TRAJECTORIES_DIR = OUTPUT_DIR / "trajectories"
SHAREGPT_DIR = OUTPUT_DIR / "sharegpt"

MODEL_POOL = {
    "minimax-m2.5": "minimax/minimax-m2.5",
    "glm-5": "z-ai/glm-5",
    "kimi-k2.5": "moonshotai/kimi-k2.5",
    "qwen3.5": "qwen/qwen3.5-397b-a17b",
    "gpt-5.4": "openai/gpt-5.4",
    "claude-sonnet-4.6": "anthropic/claude-sonnet-4.6",
    "glm-5-turbo": "z-ai/glm-5-turbo",
    "glm-4.7": "z-ai/glm-4.7",
    "gemini-3-flash": "google/gemini-3-flash-preview",
    "gpt-5.2-codex": "openai/gpt-5.2-codex",
    "claude-sonnet-4.5": "anthropic/claude-sonnet-4.5",
    "gemini-3.1-pro": "google/gemini-3.1-pro-preview",
}

DEFAULT_ROLES = {
    "analyzer": "google/gemini-3-flash-preview",
    "user": "z-ai/glm-5-turbo",
    "coder": "anthropic/claude-sonnet-4.5",
    "reviewer": "openai/gpt-5.2-codex",
}

MAX_CONVERSATION_TURNS = 5
MAX_FIX_ATTEMPTS = 2
MAX_TOOL_ITERATIONS = 20
TOOL_OUTPUT_MAX_CHARS = 10000
API_TIMEOUT_SECONDS = 180
MAX_RETRIES = 3
