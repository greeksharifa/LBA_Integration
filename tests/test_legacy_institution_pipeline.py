import importlib
import json
import sys
import types

import pytest


from Integration.services.legacy_institution_pipeline import (
    GradioPredictor,
    LegacyInstitutionPipeline,
    PipelineSettings,
    parse_answerability,
)


ANSWERABILITY = {
    "qid": "question-7",
    "question": "Who is speaking?",
    "prediction": "answerable",
    "vid": "episode-1",
}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (ANSWERABILITY, ANSWERABILITY),
        ([ANSWERABILITY], ANSWERABILITY),
        (json.dumps(ANSWERABILITY), ANSWERABILITY),
        (json.dumps([ANSWERABILITY]), ANSWERABILITY),
    ],
)
def test_parse_answerability_accepts_supported_shapes(value, expected):
    result = parse_answerability(value)

    assert result == expected
    assert result is not ANSWERABILITY


@pytest.mark.parametrize(
    "value",
    [
        object(),
        [],
        [ANSWERABILITY, ANSWERABILITY],
        ["not a mapping"],
        "{not-json}",
        json.dumps("not a mapping"),
    ],
)
def test_parse_answerability_rejects_invalid_shapes(value):
    with pytest.raises(ValueError):
        parse_answerability(value)


@pytest.mark.parametrize("missing_key", ["qid", "question", "prediction", "vid"])
def test_parse_answerability_requires_contract_fields(missing_key):
    value = {key: item for key, item in ANSWERABILITY.items() if key != missing_key}

    with pytest.raises(ValueError, match=missing_key):
        parse_answerability(value)


def test_pipeline_routes_normalized_answerability_json_to_question_service():
    class RecordingPredictor:
        def __init__(self, result):
            self.result = result
            self.payloads = []

        def predict(self, payload):
            self.payloads.append(payload)
            return self.result

    answerability = RecordingPredictor([ANSWERABILITY])
    question_result = {"question": "What happens next?"}
    question = RecordingPredictor(question_result)
    pipeline = LegacyInstitutionPipeline(answerability, question)

    result = pipeline.run(7)

    assert answerability.payloads == ["7"]
    assert len(question.payloads) == 1
    assert json.loads(question.payloads[0]) == ANSWERABILITY
    assert result == question_result
    assert result is not question_result


def test_pipeline_rejects_non_mapping_question_result():
    class Predictor:
        def __init__(self, result):
            self.result = result

        def predict(self, payload):
            return self.result

    pipeline = LegacyInstitutionPipeline(
        Predictor(ANSWERABILITY),
        Predictor(["not", "a", "mapping"]),
    )

    with pytest.raises(ValueError, match="question service"):
        pipeline.run("q1")


def test_settings_have_loopback_defaults(monkeypatch):
    for name in (
        "LBA_ARVQA_URL",
        "LBA_DRAMAQG_URL",
        "LBA_ARVQA_API_NAME",
        "LBA_DRAMAQG_API_NAME",
        "LBA_MEDIA_PATH",
        "LBA_DATASET_ROOT",
        "LBA_ARVQA_CHECKPOINT",
        "LBA_DRAMAQG_CHECKPOINT",
        "LBA_OUTPUT_PATH",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = PipelineSettings.from_environment()

    assert settings.answerability_url == "http://127.0.0.1:7868"
    assert settings.question_url == "http://127.0.0.1:7866"
    assert settings.answerability_api_name == "/predict"
    assert settings.question_api_name == "/predict"
    assert settings.media_path is None
    assert settings.dataset_root is None
    assert settings.arvqa_checkpoint is None
    assert settings.dramaqg_checkpoint is None
    assert settings.output_path is None


def test_settings_read_alternate_endpoints_and_optional_paths(monkeypatch):
    values = {
        "LBA_ARVQA_URL": "https://arvqa.example.test:8443",
        "LBA_DRAMAQG_URL": "http://questions.example.test:9000",
        "LBA_ARVQA_API_NAME": "/answerability",
        "LBA_DRAMAQG_API_NAME": "/generate",
        "LBA_MEDIA_PATH": "media/sample.mp4",
        "LBA_DATASET_ROOT": "datasets/dramaqa",
        "LBA_ARVQA_CHECKPOINT": "checkpoints/arvqa",
        "LBA_DRAMAQG_CHECKPOINT": "checkpoints/dramaqg",
        "LBA_OUTPUT_PATH": "outputs/result.json",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    settings = PipelineSettings.from_environment()

    assert settings.answerability_url == values["LBA_ARVQA_URL"]
    assert settings.question_url == values["LBA_DRAMAQG_URL"]
    assert settings.answerability_api_name == values["LBA_ARVQA_API_NAME"]
    assert settings.question_api_name == values["LBA_DRAMAQG_API_NAME"]
    assert settings.media_path == values["LBA_MEDIA_PATH"]
    assert settings.dataset_root == values["LBA_DATASET_ROOT"]
    assert settings.arvqa_checkpoint == values["LBA_ARVQA_CHECKPOINT"]
    assert settings.dramaqg_checkpoint == values["LBA_DRAMAQG_CHECKPOINT"]
    assert settings.output_path == values["LBA_OUTPUT_PATH"]


@pytest.mark.parametrize(
    "value",
    [
        "",
        "localhost:7868",
        "ftp://127.0.0.1/service",
        "http:///missing-host",
    ],
)
def test_settings_reject_invalid_urls(monkeypatch, value):
    monkeypatch.setenv("LBA_ARVQA_URL", value)

    with pytest.raises(ValueError, match="LBA_ARVQA_URL"):
        PipelineSettings.from_environment()


def test_pipeline_settings_are_frozen():
    settings = PipelineSettings()

    with pytest.raises(AttributeError):
        settings.answerability_url = "http://127.0.0.1:9999"


def test_from_settings_wires_endpoints_and_api_names_to_client_factory():
    client_calls = []
    prediction_calls = []

    class FakeClient:
        def __init__(self, endpoint):
            self.endpoint = endpoint

        def predict(self, payload, *, api_name):
            prediction_calls.append((self.endpoint, payload, api_name))
            if self.endpoint.endswith(":8001"):
                return ANSWERABILITY
            return {"generated": "question"}

    def client_factory(endpoint):
        client_calls.append(endpoint)
        return FakeClient(endpoint)

    settings = PipelineSettings(
        answerability_url="http://127.0.0.1:8001",
        question_url="http://127.0.0.1:8002",
        answerability_api_name="/classify",
        question_api_name="/generate",
    )
    pipeline = LegacyInstitutionPipeline.from_settings(
        settings,
        client_factory=client_factory,
    )

    assert client_calls == []
    assert pipeline.run(42) == {"generated": "question"}
    assert client_calls == [
        "http://127.0.0.1:8001",
        "http://127.0.0.1:8002",
    ]
    assert prediction_calls[0] == (
        "http://127.0.0.1:8001",
        "42",
        "/classify",
    )
    assert prediction_calls[1][0] == "http://127.0.0.1:8002"
    assert json.loads(prediction_calls[1][1]) == ANSWERABILITY
    assert prediction_calls[1][2] == "/generate"


def test_gradio_predictor_default_client_import_is_lazy(monkeypatch):
    clients_module_name = "Integration.services.legacy_institution_pipeline.clients"
    clients_module = importlib.import_module(clients_module_name)
    real_import = __import__
    imported_gradio = []

    fake_module = types.ModuleType("gradio_client")

    class FakeClient:
        def __init__(self, endpoint):
            self.endpoint = endpoint

        def predict(self, payload, *, api_name):
            return self.endpoint, payload, api_name

    fake_module.Client = FakeClient
    monkeypatch.setitem(sys.modules, "gradio_client", fake_module)

    def recording_import(name, *args, **kwargs):
        if name == "gradio_client":
            imported_gradio.append(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", recording_import)
    predictor = clients_module.GradioPredictor("http://127.0.0.1:7868")

    assert imported_gradio == []
    assert predictor.predict("payload") == (
        "http://127.0.0.1:7868",
        "payload",
        "/predict",
    )
    assert imported_gradio == ["gradio_client"]


def test_gradio_predictor_reuses_lazily_created_client():
    factory_calls = []

    class FakeClient:
        def predict(self, payload, *, api_name):
            return payload, api_name

    def client_factory(endpoint):
        factory_calls.append(endpoint)
        return FakeClient()

    predictor = GradioPredictor(
        "http://127.0.0.1:8123",
        api_name="/custom",
        client_factory=client_factory,
    )

    assert factory_calls == []
    assert predictor.predict("first") == ("first", "/custom")
    assert predictor.predict("second") == ("second", "/custom")
    assert factory_calls == ["http://127.0.0.1:8123"]
