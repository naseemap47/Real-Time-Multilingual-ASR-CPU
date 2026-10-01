import os
import yaml
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from src.core.schema import EngineConfig


class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"


class AudioConfig(BaseModel):
    sample_rate: int = 16000
    channels: int = 1
    sample_width: int = 2
    chunk_duration_ms: int = 200


class AppConfig(BaseModel):
    server: ServerConfig = Field(default_factory=ServerConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    default_model: str = "qwen3_asr"
    default_pipeline: str = "streaming_pcm"
    models: Dict[str, EngineConfig] = Field(default_factory=dict)


def load_app_config(config_dir: str = "config") -> AppConfig:
    """Load default app configuration and model configurations from YAML files."""
    default_yaml_path = os.path.join(config_dir, "default_config.yaml")
    
    config_dict: Dict[str, Any] = {}
    if os.path.exists(default_yaml_path):
        with open(default_yaml_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f) or {}

    app_config = AppConfig(**config_dict)

    # Load model configuration files
    models_dir = os.path.join(config_dir, "models")
    if os.path.exists(models_dir):
        for filename in os.listdir(models_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                model_yaml_path = os.path.join(models_dir, filename)
                with open(model_yaml_path, "r", encoding="utf-8") as f:
                    model_dict = yaml.safe_load(f) or {}
                    if "name" in model_dict:
                        engine_cfg = EngineConfig(**model_dict)
                        app_config.models[engine_cfg.name] = engine_cfg

    return app_config
