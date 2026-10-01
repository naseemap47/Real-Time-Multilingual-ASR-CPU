from fastapi import APIRouter
from src.core.config import load_app_config
from src.engines import EngineFactory

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check():
    """Service health check endpoint."""
    return {"status": "ok", "service": "real-time-multilingual-asr-cpu"}


@router.get("/models")
def list_models():
    """List available ASR engines and their configurations."""
    config = load_app_config()
    available_engines = EngineFactory.list_available_engines()
    
    result = []
    for engine_name in available_engines:
        if engine_name in config.models:
            cfg = config.models[engine_name]
            result.append({
                "id": cfg.name,
                "name": cfg.display_name,
                "version": cfg.version,
                "languages": cfg.languages,
                "device": cfg.device,
                "quantization": cfg.quantization,
                "streaming_supported": cfg.streaming_supported
            })
        else:
            result.append({
                "id": engine_name,
                "name": engine_name.replace("_", " ").title(),
                "version": "1.0",
                "languages": ["en", "zh", "id"],
                "device": "cpu",
                "quantization": "int8",
                "streaming_supported": True
            })
    return {"models": result}
