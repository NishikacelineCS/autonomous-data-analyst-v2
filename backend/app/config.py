"""
backend/app/config.py — Application Configuration
===================================================
ARCHITECTURAL DECISION: Why Pydantic Settings?

In production AI systems, configuration is dangerous to get wrong. If an API key
is missing, you want to find out at startup, not mid-analysis when a user is
waiting. Pydantic Settings provides:

1. TYPE VALIDATION AT STARTUP: int fields can't be "abc", enum fields must be
   one of the allowed values. Fail loudly at boot, not silently at runtime.

2. AUTOMATIC .env LOADING: No manual dotenv.load_dotenv() calls; Pydantic
   reads the .env file automatically.

3. ENVIRONMENT VARIABLE OVERRIDE: Any setting can be overridden by setting
   an environment variable. This is how 12-factor app principles work.
   In production (Docker, Railway, AWS), you set env vars directly — no .env file.

4. SINGLE SOURCE OF TRUTH: Every config value flows from this one object.
   No scattered os.getenv() calls throughout the codebase.

Usage anywhere in the codebase:
    from app.config import settings
    api_key = settings.anthropic_api_key
"""

import os
from typing import Literal, List
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central application settings. Reads from .env file and environment variables.

    Field naming convention: lowercase with underscores (Python) maps to
    UPPERCASE_WITH_UNDERSCORES in environment variables automatically.
    e.g., anthropic_api_key → ANTHROPIC_API_KEY
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Don't fail if .env has unknown variables
    )

    # ── Application Identity ──────────────────────────────────────────────────
    app_name: str = Field(
        default="Autonomous Multi-Agent Data Analyst System",
        description="Human-readable name shown in API docs and logs",
    )
    app_version: str = Field(default="1.0.0")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Controls logging verbosity, error detail level, and feature flags",
    )
    debug: bool = Field(
        default=True,
        description="If True: reload server on code changes, show detailed tracebacks",
    )

    # ── API Server ────────────────────────────────────────────────────────────
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000, ge=1024, le=65535)
    api_prefix: str = Field(default="/api/v1")

    # ── Frontend ──────────────────────────────────────────────────────────────
    frontend_port: int = Field(default=8501)
    frontend_api_url: str = Field(
        default="http://localhost:8000",
        description="URL the Streamlit frontend uses to reach the FastAPI backend",
    )

    # ── AI Model Configuration ────────────────────────────────────────────────
    anthropic_api_key: str = Field(
        default="",
        description="Anthropic API key. Get from https://console.anthropic.com/",
    )
    claude_model: str = Field(
        default="claude-sonnet-4-20250514",
        description=(
            "Claude model ID. Sonnet 4 recommended: best reasoning/cost ratio "
            "for repeated multi-agent calls. Use Opus 4 for maximum accuracy."
        ),
    )
    claude_max_tokens: int = Field(
        default=4096,
        ge=100,
        le=8192,
        description="Max tokens per LLM response. 4096 covers most analytical outputs.",
    )

    google_api_key: str = Field(default="", description="Optional Gemini API key")
    gemini_model: str = Field(default="gemini-1.5-pro")

    active_ai_provider: Literal["anthropic", "gemini"] = Field(
        default="anthropic",
        description="Which AI provider to use. Switch here to change the entire system.",
    )

    # ── Storage ───────────────────────────────────────────────────────────────
    upload_dir: str = Field(
        default="./data/uploads",
        description="Directory where user-uploaded datasets are stored",
    )
    session_dir: str = Field(
        default="./data/sessions",
        description="Directory for per-session analysis results (JSON)",
    )
    max_file_size_mb: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum upload file size in megabytes",
    )

    # ── ChromaDB ──────────────────────────────────────────────────────────────
    chroma_persist_dir: str = Field(
        default="./data/chroma_db",
        description=(
            "ChromaDB stores analysis summaries as vector embeddings. "
            "Enables semantic search over past analyses for follow-up questions."
        ),
    )
    chroma_collection_name: str = Field(default="analysis_memory")

    # ── DuckDB ────────────────────────────────────────────────────────────────
    duckdb_path: str = Field(
        default="./data/analytics.duckdb",
        description=(
            "DuckDB file path. Use ':memory:' for ephemeral mode. "
            "File mode persists tables across server restarts."
        ),
    )

    # ── Security ──────────────────────────────────────────────────────────────
    secret_key: str = Field(
        default="change-this-in-production",
        min_length=16,
        description="Used for signing session tokens. Generate: secrets.token_hex(32)",
    )
    allowed_origins: str = Field(
        default="http://localhost:8501,http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    log_format: Literal["json", "text"] = Field(
        default="text",
        description="'text' for development readability, 'json' for production log aggregators",
    )

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    max_requests_per_minute: int = Field(default=60)
    max_concurrent_analyses: int = Field(
        default=5,
        description="Limit simultaneous LangGraph workflows to control API costs",
    )

    # ── Computed Properties ───────────────────────────────────────────────────
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated origins string into a list for CORS middleware."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def max_file_size_bytes(self) -> int:
        """Convert max_file_size_mb to bytes for FastAPI file validation."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    # ── Validation ────────────────────────────────────────────────────────────
    @model_validator(mode="after")
    def validate_api_keys(self) -> "Settings":
        """
        Validate required API keys at startup.

        This runs once when the Settings object is first created (at import time).
        Fail-fast: better to crash with a clear error at startup than to fail
        mysteriously during an analysis workflow.
        """
        if self.active_ai_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError(
                "\n\n❌ ANTHROPIC_API_KEY is not set!\n"
                "   1. Get your key from: https://console.anthropic.com/\n"
                "   2. Set it in your .env file: ANTHROPIC_API_KEY=sk-ant-...\n"
            )
        if self.active_ai_provider == "gemini" and not self.google_api_key:
            raise ValueError(
                "\n\n❌ GOOGLE_API_KEY is not set!\n"
                "   Set it in your .env file: GOOGLE_API_KEY=...\n"
            )
        return self

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def ensure_directories(self) -> None:
        """
        Create all required directories at startup if they don't exist.
        Called from main.py lifespan handler.
        """
        dirs = [
            self.upload_dir,
            self.session_dir,
            self.chroma_persist_dir,
            os.path.dirname(self.duckdb_path) if self.duckdb_path != ":memory:" else None,
        ]
        for directory in dirs:
            if directory:
                os.makedirs(directory, exist_ok=True)


# =============================================================================
# SINGLETON PATTERN
# =============================================================================
# `settings` is instantiated once at module import time. All other modules
# import this single instance:
#
#   from app.config import settings
#
# This means configuration is loaded ONCE and shared. It also means that if
# a required env var is missing, the import itself will raise an error —
# which surfaces the problem immediately when the server starts.
#
# In tests, you can override settings:
#   from app.config import settings
#   settings.debug = True  # or monkeypatch via pytest fixtures
# =============================================================================
settings = Settings()