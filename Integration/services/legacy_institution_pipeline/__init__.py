"""Public contract for the clean-room legacy institution pipeline."""

from .clients import GradioPredictor
from .contracts import parse_answerability
from .pipeline import LegacyInstitutionPipeline
from .settings import PipelineSettings

__all__ = [
    "GradioPredictor",
    "LegacyInstitutionPipeline",
    "PipelineSettings",
    "parse_answerability",
]
