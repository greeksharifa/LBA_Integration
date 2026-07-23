"""Routing for the clean-room institution service contract."""

import json
from typing import Any, Protocol

from .clients import ClientFactory, GradioPredictor
from .contracts import parse_answerability
from .settings import PipelineSettings


class Predictor(Protocol):
    def predict(self, payload: Any) -> Any:
        """Return the service prediction for one payload."""


class LegacyInstitutionPipeline:
    """Route an identifier through answerability and question services."""

    def __init__(
        self,
        answerability_predictor: Predictor,
        question_predictor: Predictor,
    ) -> None:
        self.answerability_predictor = answerability_predictor
        self.question_predictor = question_predictor

    def run(self, qid: Any) -> dict[str, Any]:
        answerability_value = self.answerability_predictor.predict(str(qid))
        normalized = parse_answerability(answerability_value)
        question_value = self.question_predictor.predict(
            json.dumps(normalized, ensure_ascii=False)
        )
        return {
            "answerability": normalized,
            "sub_question": str(question_value),
        }

    @classmethod
    def from_settings(
        cls,
        settings: PipelineSettings,
        client_factory: ClientFactory | None = None,
    ) -> "LegacyInstitutionPipeline":
        return cls(
            GradioPredictor(
                settings.answerability_url,
                api_name=settings.answerability_api_name,
                client_factory=client_factory,
            ),
            GradioPredictor(
                settings.question_url,
                api_name=settings.question_api_name,
                client_factory=client_factory,
            ),
        )
