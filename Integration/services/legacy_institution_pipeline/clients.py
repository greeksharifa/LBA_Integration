"""Dependency-light prediction client adapters."""

from collections.abc import Callable
from typing import Any, Protocol


class PredictionClient(Protocol):
    def predict(self, payload: Any, *, api_name: str) -> Any:
        """Submit one payload to a named prediction API."""


ClientFactory = Callable[[str], PredictionClient]


def _default_client_factory(endpoint: str) -> PredictionClient:
    from gradio_client import Client

    return Client(endpoint)


class GradioPredictor:
    """Lazily connect to one Gradio prediction endpoint."""

    def __init__(
        self,
        endpoint: str,
        api_name: str = "/predict",
        client_factory: ClientFactory | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.api_name = api_name
        self._client_factory = client_factory or _default_client_factory
        self._client: PredictionClient | None = None

    def predict(self, payload: Any) -> Any:
        if self._client is None:
            self._client = self._client_factory(self.endpoint)
        return self._client.predict(payload, api_name=self.api_name)
