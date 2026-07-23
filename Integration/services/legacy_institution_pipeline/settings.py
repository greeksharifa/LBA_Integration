"""Environment-backed settings for institution service endpoints."""

import os
from dataclasses import dataclass
from urllib.parse import urlparse


_DEFAULT_ANSWERABILITY_URL = "http://127.0.0.1:7868"
_DEFAULT_QUESTION_URL = "http://127.0.0.1:7866"


def _validate_url(value: str, name: str) -> None:
    try:
        parsed = urlparse(value)
        hostname = parsed.hostname
        _ = parsed.port
    except ValueError as error:
        raise ValueError(f"{name} must be a valid HTTP(S) URL") from error

    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(f"{name} must be a valid HTTP(S) URL")


def _optional_environment_value(name: str) -> str | None:
    return os.environ.get(name) or None


@dataclass(frozen=True)
class PipelineSettings:
    """Configuration for the answerability-to-question pipeline."""

    answerability_url: str = _DEFAULT_ANSWERABILITY_URL
    question_url: str = _DEFAULT_QUESTION_URL
    answerability_api_name: str = "/predict"
    question_api_name: str = "/predict"
    media_path: str | None = None
    dataset_root: str | None = None
    arvqa_checkpoint: str | None = None
    dramaqg_checkpoint: str | None = None
    output_path: str | None = None

    def __post_init__(self) -> None:
        _validate_url(self.answerability_url, "answerability_url")
        _validate_url(self.question_url, "question_url")

    @classmethod
    def from_environment(cls) -> "PipelineSettings":
        answerability_url = os.environ.get(
            "LBA_ARVQA_URL",
            _DEFAULT_ANSWERABILITY_URL,
        )
        question_url = os.environ.get(
            "LBA_DRAMAQG_URL",
            _DEFAULT_QUESTION_URL,
        )
        _validate_url(answerability_url, "LBA_ARVQA_URL")
        _validate_url(question_url, "LBA_DRAMAQG_URL")

        return cls(
            answerability_url=answerability_url,
            question_url=question_url,
            answerability_api_name=os.environ.get(
                "LBA_ARVQA_API_NAME",
                "/predict",
            ),
            question_api_name=os.environ.get(
                "LBA_DRAMAQG_API_NAME",
                "/predict",
            ),
            media_path=_optional_environment_value("LBA_MEDIA_PATH"),
            dataset_root=_optional_environment_value("LBA_DATASET_ROOT"),
            arvqa_checkpoint=_optional_environment_value("LBA_ARVQA_CHECKPOINT"),
            dramaqg_checkpoint=_optional_environment_value(
                "LBA_DRAMAQG_CHECKPOINT"
            ),
            output_path=_optional_environment_value("LBA_OUTPUT_PATH"),
        )
