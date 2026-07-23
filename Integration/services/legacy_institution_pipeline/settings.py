"""Environment-backed settings for institution service endpoints."""

import ipaddress
import os
import re
import unicodedata
from dataclasses import dataclass
from urllib.parse import urlparse


_DEFAULT_ANSWERABILITY_URL = "http://127.0.0.1:7868"
_DEFAULT_QUESTION_URL = "http://127.0.0.1:7866"
_HOST_LABEL = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?")


def _has_forbidden_characters(value: str) -> bool:
    return "\\" in value or any(
        character.isspace() or unicodedata.category(character) == "Cc"
        for character in value
    )


def _is_valid_hostname(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        return True

    try:
        ascii_hostname = hostname.encode("idna").decode("ascii")
    except UnicodeError:
        return False

    if ascii_hostname.endswith("."):
        ascii_hostname = ascii_hostname[:-1]
    if not ascii_hostname or len(ascii_hostname) > 253:
        return False
    return all(
        _HOST_LABEL.fullmatch(label) is not None
        for label in ascii_hostname.split(".")
    )


def _validate_url(value: str, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or _has_forbidden_characters(value)
    ):
        raise ValueError(f"{name} must be a valid HTTP(S) URL")

    try:
        parsed = urlparse(value)
        hostname = parsed.hostname
        _ = parsed.port
        has_empty_port = parsed.netloc.rsplit("@", 1)[-1].endswith(":")
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a valid HTTP(S) URL") from error

    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or not hostname
        or not _is_valid_hostname(hostname)
        or has_empty_port
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError(f"{name} must be a valid HTTP(S) URL")


def _validate_api_name(value: str, name: str) -> None:
    if (
        not isinstance(value, str)
        or not value
        or not value.startswith("/")
        or _has_forbidden_characters(value)
    ):
        raise ValueError(
            f"{name} must be a nonempty slash-prefixed API name "
            "without whitespace, control characters, or backslashes"
        )


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
        _validate_api_name(
            self.answerability_api_name,
            "answerability_api_name",
        )
        _validate_api_name(self.question_api_name, "question_api_name")

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
