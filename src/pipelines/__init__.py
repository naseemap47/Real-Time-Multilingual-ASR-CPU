from src.pipelines.base import BasePipelineAdapter
from src.pipelines.streaming_pcm import StreamingPCMPipeline
from src.pipelines.vad_pipeline import VADBufferedPipeline


class PipelineFactory:
    """Factory for instantiating pluggable audio pipelines."""

    _PIPELINES = {
        "streaming_pcm": StreamingPCMPipeline,
        "vad_buffered": VADBufferedPipeline,
    }

    @classmethod
    def create_pipeline(cls, pipeline_name: str, **kwargs) -> BasePipelineAdapter:
        if pipeline_name not in cls._PIPELINES:
            raise ValueError(f"Unknown pipeline '{pipeline_name}'. Available: {list(cls._PIPELINES.keys())}")
        return cls._PIPELINES[pipeline_name](**kwargs)
