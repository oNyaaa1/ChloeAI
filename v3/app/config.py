from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "ChloeAI"
    host: str = "127.0.0.1"
    port: int = 8000
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_chat_model: str = "qwen2.5:7b"
    ollama_embed_model: str = "nomic-embed-text"
    mysql_url: str = "mysql+pymysql://chloe:change_me@127.0.0.1:3306/chloeai?charset=utf8mb4"
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_collection: str = "chloe_memory"
    memory_top_k: int = 5
    approval_expiry_minutes: int = 30
    workspace_dir: str = "./workspace"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
