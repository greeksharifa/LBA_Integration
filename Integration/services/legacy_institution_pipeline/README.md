# Legacy institution pipeline contract

This package defines the client boundary for the legacy handoff from KAIST
answerability, through KHU question generation, to SNU integration. It is a
clean-room interface implementation. It is not ARVQA source code and does not
copy or provide an ARVQA model implementation.

The package contains no datasets, checkpoints, model weights, or model
implementations. Deployments must supply those assets to their independently
operated services. When KHU-derived integration behavior is redistributed, the
applicable upstream MIT copyright and permission notice must be preserved.

## Contract

`LegacyInstitutionPipeline.run(qid)` sends `str(qid)` to the answerability
service. That service must return a mapping, a one-element list containing a
mapping, or a JSON encoding of either form. The normalized mapping must include
`qid`, `question`, `prediction`, and `vid`.

The pipeline JSON-encodes the normalized mapping and submits it to the question
service. The question service must return a mapping; the pipeline returns a new
dictionary containing that result. Invalid response shapes raise `ValueError`.

```python
from Integration.services.legacy_institution_pipeline import (
    LegacyInstitutionPipeline,
    PipelineSettings,
)

pipeline = LegacyInstitutionPipeline.from_settings(
    PipelineSettings.from_environment()
)
result = pipeline.run("question-7")
```

The Gradio runtime dependency is loaded only when a request is first sent, so
contract consumers and unit tests can import this package without installing
`gradio_client`.

## Configuration

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `LBA_ARVQA_URL` | `http://127.0.0.1:7868` | Answerability endpoint |
| `LBA_DRAMAQG_URL` | `http://127.0.0.1:7866` | Question endpoint |
| `LBA_ARVQA_API_NAME` | `/predict` | Answerability API name |
| `LBA_DRAMAQG_API_NAME` | `/predict` | Question API name |
| `LBA_MEDIA_PATH` | unset | Optional deployment media path |
| `LBA_DATASET_ROOT` | unset | Optional deployment dataset root |
| `LBA_ARVQA_CHECKPOINT` | unset | Optional answerability checkpoint reference |
| `LBA_DRAMAQG_CHECKPOINT` | unset | Optional question checkpoint reference |
| `LBA_OUTPUT_PATH` | unset | Optional output path |

Defaults deliberately connect only to loopback services. Connecting to a
non-loopback host is an explicit deployment choice: set the corresponding URL
environment variable to a valid `http` or `https` URL. No remote host is
discovered implicitly.

## Limitations

This package only validates and routes the service-level data contract. It does
not start services, load media, resolve dataset or checkpoint paths, perform
authentication, retry failed calls, or interpret model predictions. Operators
remain responsible for network access control, service compatibility, data
licensing, and output persistence.
