"""
PAIMANA Platform — Application Configuration
Loaded from environment variables via Pydantic Settings.
"""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "PAIMANA Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    API_DEBUG: bool = False

    # ── Server ───────────────────────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://paimana_user:paimana_dev_password@localhost:5432/paimana"

    # ── Auth (Firebase) ──────────────────────────────────────────────────────
    # Path to Firebase service-account JSON (download from Firebase Console →
    # Project Settings → Service Accounts → Generate new private key)
    FIREBASE_SERVICE_ACCOUNT_PATH: str = "./firebase-service-account.json"

    # ── Storage ──────────────────────────────────────────────────────────────
    STORAGE_BACKEND: str = "local"   # local | supabase
    LOCAL_STORAGE_PATH: str = "./storage"
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "paimana-documents"

    # ── ML ───────────────────────────────────────────────────────────────────
    ML_ENABLED: bool = False
    ML_MIN_TRAINING_PROJECTS: int = 50
    ML_MIN_SNAPSHOTS_PER_PROJECT: int = 3
    MODEL_STORAGE_PATH: str = "./app/ml/models"

    # ── Logging ──────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
