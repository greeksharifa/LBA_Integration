"""Value normalization for the institution-service boundary."""

import json
from collections.abc import Mapping
from typing import Any


_REQUIRED_FIELDS = ("qid", "question", "prediction", "vid")


def parse_answerability(value: Any) -> dict[str, Any]:
    """Normalize a supported answerability response into a new dictionary."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError("answerability response is not valid JSON") from error

    if isinstance(value, list):
        if len(value) != 1:
            raise ValueError("answerability response list must contain one item")
        value = value[0]

    if not isinstance(value, Mapping):
        raise ValueError("answerability response must be a mapping")

    normalized = dict(value)
    missing = [field for field in _REQUIRED_FIELDS if field not in normalized]
    if missing:
        raise ValueError(
            "answerability response is missing required field(s): "
            + ", ".join(missing)
        )

    try:
        json.dumps(normalized, ensure_ascii=False)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(
            "answerability response must be entirely JSON-serializable"
        ) from error
    return normalized
