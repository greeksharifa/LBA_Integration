# LBA Remote Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a sanitized legacy institution pipeline in `LBA_Integration`, move sanitized INQUIRER/Flipped work to `LBA_LAVIS`, and delete the temporary `LBA_Prototypes` repository without disturbing existing dirty checkouts or `fix/khu-integration`.

**Architecture:** Build every code branch in a disposable worktree. The institution branch contains a clean-room API contract and client orchestration only; it does not copy unlicensed ARVQA implementation. The INQUIRER branches are rebuilt from the public Flipped-VQA upstream tree so the original hardcoded-path commits are not ancestors of the published replacements.

**Tech Stack:** Git worktrees, Python 3, `dataclasses`, `json`, optional `gradio_client`, pytest/unittest, GitHub CLI/API.

---

## File Map

### `LBA_Integration`

- Create: `Integration/services/legacy_institution_pipeline/__init__.py`
  - Public exports for the legacy service contract.
- Create: `Integration/services/legacy_institution_pipeline/contracts.py`
  - Validates ARVQA answerability responses and the KHU sub-question result.
- Create: `Integration/services/legacy_institution_pipeline/clients.py`
  - Configurable, lazy Gradio client wrapper with no model implementation.
- Create: `Integration/services/legacy_institution_pipeline/settings.py`
  - Environment/CLI-neutral endpoint, port, media, checkpoint, and output
    settings with loopback-safe defaults.
- Create: `Integration/services/legacy_institution_pipeline/pipeline.py`
  - KAIST answerability -> KHU sub-question orchestration.
- Create: `Integration/services/legacy_institution_pipeline/README.md`
  - Provenance, service flow, inputs, outputs, limitations, and MIT notice.
- Create: `tests/test_legacy_institution_pipeline.py`
  - Contract, routing, configuration, and sanitization tests.
- Modify: `README.md`
  - Adds `demo/legacy-institution-pipeline` to the branch map on `main`.

### Rebuilt INQUIRER branches

- Reuse after sanitization:
  - `docs/inquirer_qa_summary.md`
  - `json_schema.md`
  - `thesis/inquirer_qa_summary.md`
  - `tools/normalize_inquirer_qas.py`
  - `tools/export_thesis_qas.py`
  - `tests/test_normalize_inquirer_qas.py`
  - `tests/test_export_thesis_qas.py`
- Reuse after path configuration:
  - `dataloader/dramaqa.py`
  - `dataloader/dramaqa_kg.py`
  - `dataloader/star.py`
  - `dataloader/tvqa.py`
  - `split_data.py`
  - `train.py`
- Create: `tests/test_repository_sanitization.py`
  - Fails when rebuilt branch content contains personal/server paths, fixed GPU
    selection, credentials, or live/debug breakpoint calls.
- Create: `docs/provenance/LBA_Prototypes-inventory.md`
  - Records the exact three source heads, tag/release/LFS inventory, and the
    explicit supersession decision for each head before deletion.

### LBA map

- Modify: `/home/ywjang/LBA/README.md`
  - Records final branch ownership and the local KBS artifact workspace.

## Task 1: Capture Preconditions and Isolate Work

**Files:** None.

- [ ] **Step 1: Record immutable remote preconditions**

Run:

```bash
git -C /home/ywjang/LBA/LBA_Integration ls-remote --heads origin \
  main fix/khu-integration demo/legacy-institution-pipeline
git -C /home/ywjang/LBA/Flipped-VQA ls-remote --heads origin \
  master feature/lba-inquirer-data-pipeline \
  experiment/lba-augmented-vqa-training
gh api repos/greeksharifa/Flipped-VQA \
  --jq '{fork,parent:.parent.full_name,default_branch}'
```

Expected:

- `fix/khu-integration` is
  `94579e3078c42759b09c12c7cf066b3a04653131`.
- Flipped `master` is `24b91ea2b3cd21746f9b4ae5767e9fbb9aca406c`.
- Flipped remains a fork of `mlvlab/Flipped-VQA`, default `master`.

- [ ] **Step 2: Inventory the repository that will be deleted**

Run:

```bash
gh api repos/greeksharifa/LBA_Prototypes
gh api repos/greeksharifa/LBA_Prototypes/branches --paginate
gh api repos/greeksharifa/LBA_Prototypes/tags --paginate
gh api repos/greeksharifa/LBA_Prototypes/releases --paginate
gh api repos/greeksharifa/LBA_Prototypes \
  | jq -S -c '{created_at,full_name,id,node_id}' \
  > /tmp/lba-prototypes-identity.before
git ls-remote https://github.com/greeksharifa/LBA_Prototypes.git
git clone --mirror https://github.com/greeksharifa/LBA_Prototypes.git \
  /tmp/lba-prototypes-inventory.git
git -C /tmp/lba-prototypes-inventory.git lfs ls-files --all
git ls-remote https://github.com/greeksharifa/LBA_Prototypes.git | sort \
  > /tmp/lba-prototypes-refs.before
gh api repos/greeksharifa/LBA_Prototypes/tags --paginate \
  --jq '.[].name' | sort > /tmp/lba-prototypes-tags.before
gh api repos/greeksharifa/LBA_Prototypes/releases --paginate \
  --jq '.[] | [.id,.tag_name,.target_commitish,.draft,.prerelease] | @tsv' \
  | sort > /tmp/lba-prototypes-releases.before
git -C /tmp/lba-prototypes-inventory.git lfs ls-files --all | sort \
  > /tmp/lba-prototypes-lfs.before
gh api repos/greeksharifa/LBA_Prototypes --jq .default_branch \
  > /tmp/lba-prototypes-default-branch.before
```

Expected heads:

- `main` at `ea8f12c634bdee7908937a4b1f4cda2e458ea009`
- `arvqa-answerability-demo` at
  `f572aa4d80d432f1642507f6d90de0edbe0abf9f`
- `dramaqg-gradio-bridge` at
  `cfe578bfec21cca35ede26e655a59922dbd21401`

Record whether tags, releases, and LFS objects exist. Classify:

- `main`: provenance summary to be incorporated into Integration docs;
- ARVQA head: intentionally superseded by the clean-room API contract;
- DramaQG head: intentionally superseded by the minimal MIT-noticed bridge.

Write the exact API/ref/LFS results and these classifications to
`docs/provenance/LBA_Prototypes-inventory.md` in the planning worktree. Include
these exact machine-readable lines, substituting the observed numeric counts:

```text
repository_id: 1309374491
repository_node_id: R_kgDOTgt4Gw
repository_full_name: greeksharifa/LBA_Prototypes
repository_created_at: 2026-07-23T00:30:07Z
captured_at: 2026-07-23T04:47:01Z
default_branch: main
main: ea8f12c634bdee7908937a4b1f4cda2e458ea009 | incorporated into LBA_Integration provenance
arvqa-answerability-demo: f572aa4d80d432f1642507f6d90de0edbe0abf9f | superseded by clean-room API contract
dramaqg-gradio-bridge: cfe578bfec21cca35ede26e655a59922dbd21401 | superseded by MIT-noticed bridge
tags: <count>
releases: <count>
lfs_objects: <count>
```

- [ ] **Step 3: Verify local source-object retention**

Run:

```bash
git -C /home/ywjang/LBA/archivers/LBA_Integration-local-20260723/LBA-ARVQA \
  cat-file -e f572aa4d80d432f1642507f6d90de0edbe0abf9f^{commit}
git -C /home/ywjang/LBA/archivers/LBA_Integration-local-20260723/LBA-DramaQG \
  cat-file -e cfe578bfec21cca35ede26e655a59922dbd21401^{commit}
```

Expected: both commands exit 0.

- [ ] **Step 4: Create disposable worktrees**

Before creating them, snapshot the primary checkout state:

```bash
git -C /home/ywjang/LBA/LBA_Integration status --porcelain=v1 -uall \
  > /tmp/lba-integration-status.before
git -C /home/ywjang/LBA/LBA_LAVIS status --porcelain=v1 -uall \
  > /tmp/lba-lavis-status.before
git -C /home/ywjang/LBA/LBA_LAVIS diff --binary \
  > /tmp/lba-lavis-diff.before
git -C /home/ywjang/LBA/Flipped-VQA status --porcelain=v1 -uall \
  > /tmp/lba-flipped-status.before
git -C /home/ywjang/LBA/Flipped-VQA diff --binary \
  > /tmp/lba-flipped-diff.before
```

Run:

```bash
git -C /home/ywjang/LBA/LBA_Integration worktree add \
  -b demo/legacy-institution-pipeline \
  /tmp/lba-institution-demo c01b513
git -C /home/ywjang/LBA/Flipped-VQA worktree add \
  -b inquirer/data-export-pipeline \
  /tmp/lba-inquirer-data upstream/main
```

Expected: primary checkouts remain on their original branches with unchanged
status.

## Task 2: Build the Clean-Room Institution Contract

**Files:**

- Create: `Integration/services/legacy_institution_pipeline/__init__.py`
- Create: `Integration/services/legacy_institution_pipeline/contracts.py`
- Create: `Integration/services/legacy_institution_pipeline/clients.py`
- Create: `Integration/services/legacy_institution_pipeline/settings.py`
- Create: `Integration/services/legacy_institution_pipeline/pipeline.py`
- Create: `Integration/services/legacy_institution_pipeline/README.md`
- Test: `tests/test_legacy_institution_pipeline.py`

- [ ] **Step 1: Write failing contract and routing tests**

Create tests equivalent to:

```python
import json

import pytest

from Integration.services.legacy_institution_pipeline.contracts import (
    parse_answerability,
)
from Integration.services.legacy_institution_pipeline.pipeline import (
    LegacyInstitutionPipeline,
)
from Integration.services.legacy_institution_pipeline.settings import (
    PipelineSettings,
)


class FakePredictor:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def predict(self, payload):
        self.calls.append(payload)
        return self.response


def test_pipeline_routes_answerability_to_question_generator():
    arvqa = FakePredictor(json.dumps([{
        "qid": 42,
        "question": "Why?",
        "prediction": [{"object": False}],
        "vid": "sample-video",
    }]))
    dramaqg = FakePredictor("What object is missing?")

    result = LegacyInstitutionPipeline(arvqa, dramaqg).run("42")

    assert result["sub_question"] == "What object is missing?"
    assert json.loads(dramaqg.calls[0])["qid"] == 42


def test_answerability_contract_rejects_missing_fields():
    with pytest.raises(ValueError, match="missing"):
        parse_answerability('{"qid": 42}')


def test_settings_are_loopback_safe_and_environment_configurable(monkeypatch):
    defaults = PipelineSettings.from_environment()
    assert defaults.answerability_url.startswith("http://127.0.0.1:")
    assert defaults.question_url.startswith("http://127.0.0.1:")

    monkeypatch.setenv("LBA_MEDIA_PATH", "fixtures/frame.jpg")
    monkeypatch.setenv("LBA_DATASET_ROOT", "data/institution")
    monkeypatch.setenv("LBA_ARVQA_URL", "http://127.0.0.1:17868")
    monkeypatch.setenv("LBA_DRAMAQG_URL", "http://127.0.0.1:17866")
    monkeypatch.setenv("LBA_ARVQA_CHECKPOINT", "checkpoints/arvqa.pt")
    monkeypatch.setenv("LBA_DRAMAQG_CHECKPOINT", "checkpoints/dramaqg")
    monkeypatch.setenv("LBA_OUTPUT_PATH", "artifacts/result.json")
    configured = PipelineSettings.from_environment()
    assert configured.answerability_url == "http://127.0.0.1:17868"
    assert configured.question_url == "http://127.0.0.1:17866"
    assert str(configured.media_path) == "fixtures/frame.jpg"
    assert str(configured.dataset_root) == "data/institution"
    assert str(configured.arvqa_checkpoint) == "checkpoints/arvqa.pt"
    assert str(configured.dramaqg_checkpoint) == "checkpoints/dramaqg"
    assert str(configured.output_path) == "artifacts/result.json"


def test_settings_build_configured_clients(monkeypatch):
    calls = []

    class RecordingClient:
        def __init__(self, endpoint, api_name="/predict"):
            calls.append((endpoint, api_name))

        def predict(self, payload):
            return payload

    monkeypatch.setenv("LBA_ARVQA_URL", "http://127.0.0.1:17868")
    monkeypatch.setenv("LBA_DRAMAQG_URL", "http://127.0.0.1:17866")
    LegacyInstitutionPipeline.from_settings(
        PipelineSettings.from_environment(),
        client_factory=RecordingClient,
    )
    assert calls == [
        ("http://127.0.0.1:17868", "/predict"),
        ("http://127.0.0.1:17866", "/predict"),
    ]
```

- [ ] **Step 2: Run the tests and verify failure**

Run:

```bash
python -m pytest tests/test_legacy_institution_pipeline.py -q
```

Expected: import failure because the clean-room modules do not exist.

- [ ] **Step 3: Implement the minimal contracts**

`contracts.py` must:

- accept either a mapping, a one-element list, or JSON encoding of either;
- require `qid`, `question`, `prediction`, and `vid`;
- return a new normalized mapping;
- reject arbitrary objects and missing fields with `ValueError`;
- contain no ARVQA model code.

Minimal public shape:

```python
REQUIRED_ANSWERABILITY_FIELDS = {"qid", "question", "prediction", "vid"}


def parse_answerability(value):
    if isinstance(value, str):
        value = json.loads(value)
    if isinstance(value, list):
        if len(value) != 1:
            raise ValueError("answerability response must contain one item")
        value = value[0]
    if not isinstance(value, dict):
        raise ValueError("answerability response must be an object")
    missing = REQUIRED_ANSWERABILITY_FIELDS - value.keys()
    if missing:
        raise ValueError(f"missing answerability fields: {sorted(missing)}")
    return {key: value[key] for key in sorted(REQUIRED_ANSWERABILITY_FIELDS)}
```

- [ ] **Step 4: Implement configurable clients and orchestration**

`clients.py` must expose:

```python
class GradioPredictor:
    def __init__(self, endpoint, api_name="/predict", client_factory=None):
        ...

    def predict(self, payload):
        ...
```

Import `gradio_client.Client` only inside the default factory so unit tests do
not require model/runtime dependencies.

`settings.py` must expose a frozen `PipelineSettings` dataclass with:

- `answerability_url` defaulting to `http://127.0.0.1:7868`;
- `question_url` defaulting to `http://127.0.0.1:7866`;
- optional `media_path`, `dataset_root`, `arvqa_checkpoint`,
  `dramaqg_checkpoint`, and `output_path`;
- `from_environment()` reading `LBA_ARVQA_URL`, `LBA_DRAMAQG_URL`,
  `LBA_MEDIA_PATH`, `LBA_DATASET_ROOT`, `LBA_ARVQA_CHECKPOINT`,
  `LBA_DRAMAQG_CHECKPOINT`, and `LBA_OUTPUT_PATH`;
- validation that default bind/endpoint values are loopback-only and that an
  externally supplied non-loopback URL is an explicit operator choice.

`pipeline.py` must expose:

```python
class LegacyInstitutionPipeline:
    def __init__(self, answerability_client, question_client):
        ...

    def run(self, qid):
        answerability = parse_answerability(
            self.answerability_client.predict(str(qid))
        )
        sub_question = self.question_client.predict(
            json.dumps(answerability, ensure_ascii=False)
        )
        return {
            "answerability": answerability,
            "sub_question": str(sub_question),
        }
```

It must also expose `from_settings(settings, client_factory=None)`, constructing
both `GradioPredictor` instances from the configured endpoint/API values. This
is the tested integration point proving settings are not dead configuration.

- [ ] **Step 5: Document the contract and provenance**

The README must explicitly state:

- legacy KAIST -> KHU -> SNU intent;
- this directory is a clean-room client contract, not ARVQA source;
- no dataset/checkpoint/model implementation is included;
- KHU-derived integration behavior retains the upstream MIT notice;
- endpoints and bind addresses must be explicitly configured;
- default clients should use loopback endpoints.

- [ ] **Step 6: Run tests and branch sanitization scan**

Run:

```bash
python -m pytest tests/test_legacy_institution_pipeline.py -q
python -m compileall -q Integration/services/legacy_institution_pipeline
rg -n -i \
  '(/home/[^/]+|/data[0-9]+/|/nas-[^/]+/|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{20,}|BEGIN .*PRIVATE KEY|ipdb|pdb\.set_trace|breakpoint\(|CUDA_VISIBLE_DEVICES=[0-9])' \
  Integration/services/legacy_institution_pipeline \
  tests/test_legacy_institution_pipeline.py
```

Expected: tests pass, compile succeeds, scan has no findings.

- [ ] **Step 7: Commit the institution contract**

Run:

```bash
git add Integration/services/legacy_institution_pipeline \
  tests/test_legacy_institution_pipeline.py
git diff --cached --check
git commit -m "Add legacy institution pipeline contract" \
  -m "- Define clean-room answerability and question-service clients without copying ARVQA implementation.\n- Document the KAIST, KHU, and SNU interface boundary and test its routing contract."
```

Expected: one focused commit on `demo/legacy-institution-pipeline`.

## Task 3: Rebuild the INQUIRER Data Branch

**Files:**

- Restore and sanitize the eight files introduced by source commit `9c862eb`.
- Create: `tests/test_repository_sanitization.py`

- [ ] **Step 1: Restore only the intended source files without source history**

Run in `/tmp/lba-inquirer-data`:

```bash
git restore --source=9c862ebd69ad46819dfa8c03bf292fcd35f76c9b -- \
  docs/inquirer_qa_summary.md json_schema.md \
  thesis/inquirer_qa_summary.md tools/__init__.py \
  tools/export_thesis_qas.py tools/normalize_inquirer_qas.py \
  tests/test_export_thesis_qas.py tests/test_normalize_inquirer_qas.py
```

Expected: working tree contains the intended eight-file delta while branch
history still ends at public `upstream/main`.

- [ ] **Step 2: Write the failing sanitization test**

Create a test that scans tracked text files for:

```python
FORBIDDEN = (
    re.compile("/" + r"home/[^/\s]+/"),
    re.compile("/" + r"data[0-9]+/"),
    re.compile("/" + r"nas-[^/\s]+/"),
    re.compile(r"\bip" + r"db\b"),
    re.compile(r"\bp" + r"db\.set_trace\b"),
    re.compile(r"\bbreak" + r"point\("),
    re.compile(r"CUDA_VISIBLE_DEVICES=" + r"\d"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?:sk[-_]|ghp_)[A-Za-z0-9_-]{20,}"),
    re.compile(r"BEGIN [A-Z ]+PRIVATE KEY"),
    re.compile(
        r"(?i)(?:api[_-]?key|access[_-]?token|secret[_-]?key|password)"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{8,}"
    ),
    re.compile(
        r"(?i)(?:cookie|session[_-]?(?:id|token))"
        r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{8,}"
    ),
)
```

Build the candidate set with
`git ls-files --cached --others --exclude-standard -z` so restored-but-not-yet
staged files are included. Skip the scanner's own path, `.git`, binary files,
caches, datasets, checkpoints, and generated outputs. This avoids both missing
new files and self-matching the regex literals. Fail on tracked filenames
matching `.env`, `.env.*`, `cookie`, `cookies.txt`, or `cookies.json`.

- [ ] **Step 3: Run the test and verify failure**

Run:

```bash
python -m pytest tests/test_repository_sanitization.py -q
```

Expected: failures identify the recovered personal/server paths.

- [ ] **Step 4: Parameterize data-export roots**

Use environment-backed defaults:

```python
INQUIRER_SOURCE_ROOT = Path(
    os.environ.get("INQUIRER_SOURCE_ROOT", "data/inquirer-source")
)
INQUIRER_WORKSPACE = Path(
    os.environ.get("INQUIRER_WORKSPACE", "artifacts/inquirer")
)
DRAMAQA_ROOT = Path(os.environ.get("DRAMAQA_ROOT", "data/dramaqa"))
STAR_VIDEO_ROOT = Path(os.environ.get("STAR_VIDEO_ROOT", "data/star/videos"))
TVQA_VIDEO_ROOT = Path(os.environ.get("TVQA_VIDEO_ROOT", "data/tvqa/videos"))
HOW2QA_VIDEO_ROOT = Path(os.environ.get("HOW2QA_VIDEO_ROOT", "data/how2qa/clips"))
```

Replace documentation examples with `$INQUIRER_SOURCE_ROOT`,
`$INQUIRER_WORKSPACE`, `$DRAMAQA_ROOT`, `$STAR_VIDEO_ROOT`,
`$TVQA_VIDEO_ROOT`, `$HOW2QA_VIDEO_ROOT`, or neutral relative fixture paths.
Remove commented debugger calls instead of merely commenting them out.

- [ ] **Step 5: Run the existing and new tests**

Run:

```bash
python -m pytest tests/test_normalize_inquirer_qas.py \
  tests/test_export_thesis_qas.py -q
python -m pytest tests/test_repository_sanitization.py -q
python -m compileall -q tools tests
```

Expected: 12 existing pipeline tests pass, sanitization passes, compile
succeeds.

- [ ] **Step 6: Commit the sanitized data branch**

Run:

```bash
git add docs json_schema.md thesis tools tests
git diff --cached --check
git commit -m "Add sanitized INQUIRER data export pipeline" \
  -m "- Normalize and export generated QA with configurable source, workspace, and media roots.\n- Preserve the recovered KBS data contract while removing machine-specific paths and debug residue."
```

Record the new commit SHA.

## Task 4: Rebuild the Flipped-VQA Augmentation Branch

**Files:**

- Restore the 14-file logical delta from source commit `21e4555`.
- Modify:
  - `dataloader/dramaqa.py`
  - `dataloader/dramaqa_kg.py`
  - `dataloader/star.py`
  - `dataloader/tvqa.py`
  - `split_data.py`
  - `train.py`
  - relevant docs/tests from Task 3

- [ ] **Step 1: Create the descendant branch**

Run:

```bash
git switch -c inquirer/flipped-vqa-augmentation
```

Expected: new branch starts at sanitized Task 3 commit.

- [ ] **Step 2: Restore only the augmentation delta**

Restore the files shown by:

```bash
git diff --name-only \
  9c862ebd69ad46819dfa8c03bf292fcd35f76c9b \
  21e45554db9051a2c48eab574a68992200f82fe6
```

Use `git restore --source=21e4555 -- <listed paths>`, then retain the sanitized
Task 3 versions of shared docs, tools, and tests.

- [ ] **Step 3: Add failing path-configuration tests**

Create `dataloader/inquirer_paths.py` with pure path-resolver functions, then
write tests first that call the not-yet-implemented functions with a temporary
`inquirer_source_root`. Assert that DramaQA, STAR, TVQA, and How2QA inputs are
resolved below that root rather than a fixed home directory. Loader tests must
not instantiate Torch models or load real datasets.

Run:

```bash
python -m pytest tests/test_repository_sanitization.py \
  tests/test_inquirer_loader_paths.py -q
```

Expected: loader-path tests fail before parameterization.

- [ ] **Step 4: Implement configurable augmentation paths**

Add `--inquirer-source-root` to `train.py`, defaulting to
`$INQUIRER_SOURCE_ROOT` or `data/inquirer-source`. Use `pathlib.Path` joins in
`dataloader/inquirer_paths.py`, all augmented loaders, and `split_data.py`; do
not retain disabled examples with old absolute paths.

- [ ] **Step 5: Run focused validation**

Run:

```bash
python -m pytest tests/test_repository_sanitization.py \
  tests/test_inquirer_loader_paths.py -q
python -m pytest tests/test_normalize_inquirer_qas.py \
  tests/test_export_thesis_qas.py -q
python -m compileall -q dataloader tools tests split_data.py train.py eval.py
```

Expected: all focused tests pass and compilation succeeds.

- [ ] **Step 6: Commit the sanitized augmentation branch**

Run:

```bash
git add .gitignore dataloader eval.py llama split_data.py train.py tests
git diff --cached --check
git commit -m "Add sanitized INQUIRER Flipped-VQA augmentation" \
  -m "- Add KG-aware loaders and augmentation training controls on top of the sanitized export pipeline.\n- Resolve all generated-QA inputs from configurable roots instead of personal server paths."
```

Record the new commit SHA and verify:

```bash
git merge-base --is-ancestor \
  inquirer/data-export-pipeline \
  inquirer/flipped-vqa-augmentation
```

Expected: exit 0.

## Task 5: Push, Verify, Document, and Delete

**Files:**

- Modify: `/home/ywjang/LBA/LBA_Integration/README.md`
- Modify: `/home/ywjang/LBA/README.md`

- [ ] **Step 1: Push the institution demo branch**

Run:

```bash
git -C /tmp/lba-institution-demo push -u origin \
  demo/legacy-institution-pipeline
```

Expected: remote SHA equals the local branch SHA.

- [ ] **Step 2: Push sanitized INQUIRER branches to LBA_LAVIS**

Run:

```bash
git -C /tmp/lba-inquirer-data push --atomic \
  https://github.com/greeksharifa/LBA_LAVIS.git \
  inquirer/data-export-pipeline:refs/heads/inquirer/data-export-pipeline \
  inquirer/flipped-vqa-augmentation:refs/heads/inquirer/flipped-vqa-augmentation
```

Expected: both remote refs match recorded sanitized SHAs.

Verify exact remote values and ancestry from the published refs:

```bash
test "$(git -C /tmp/lba-inquirer-data rev-parse inquirer/data-export-pipeline)" = \
  "$(git ls-remote https://github.com/greeksharifa/LBA_LAVIS.git \
    refs/heads/inquirer/data-export-pipeline | cut -f1)"
test "$(git -C /tmp/lba-inquirer-data rev-parse inquirer/flipped-vqa-augmentation)" = \
  "$(git ls-remote https://github.com/greeksharifa/LBA_LAVIS.git \
    refs/heads/inquirer/flipped-vqa-augmentation | cut -f1)"
git -C /tmp/lba-inquirer-data merge-base --is-ancestor \
  inquirer/data-export-pipeline inquirer/flipped-vqa-augmentation
```

Verify the old source commits are not ancestors:

```bash
! git -C /tmp/lba-inquirer-data merge-base --is-ancestor \
  9c862ebd69ad46819dfa8c03bf292fcd35f76c9b \
  inquirer/data-export-pipeline
! git -C /tmp/lba-inquirer-data merge-base --is-ancestor \
  21e45554db9051a2c48eab574a68992200f82fe6 \
  inquirer/flipped-vqa-augmentation
```

Expected: both negated commands succeed.

- [ ] **Step 3: Import matching local refs into LBA_LAVIS without checkout**

Run:

```bash
git -C /home/ywjang/LBA/LBA_LAVIS fetch origin \
  refs/heads/inquirer/data-export-pipeline:refs/remotes/origin/inquirer/data-export-pipeline \
  refs/heads/inquirer/flipped-vqa-augmentation:refs/remotes/origin/inquirer/flipped-vqa-augmentation
git -C /home/ywjang/LBA/LBA_LAVIS branch \
  inquirer/data-export-pipeline \
  origin/inquirer/data-export-pipeline
git -C /home/ywjang/LBA/LBA_LAVIS branch \
  inquirer/flipped-vqa-augmentation \
  origin/inquirer/flipped-vqa-augmentation
```

Expected: no checkout or working-tree change.

- [ ] **Step 4: Remove only the migrated refs from the old Flipped fork**

Run:

```bash
git -C /home/ywjang/LBA/Flipped-VQA push --atomic origin \
  --force-with-lease=refs/heads/feature/lba-inquirer-data-pipeline:9c862ebd69ad46819dfa8c03bf292fcd35f76c9b \
  --force-with-lease=refs/heads/experiment/lba-augmented-vqa-training:21e45554db9051a2c48eab574a68992200f82fe6 \
  :refs/heads/feature/lba-inquirer-data-pipeline \
  :refs/heads/experiment/lba-augmented-vqa-training
```

Then verify:

```bash
gh api repos/greeksharifa/Flipped-VQA \
  --jq '{fork,parent:.parent.full_name,default_branch}'
git -C /home/ywjang/LBA/Flipped-VQA ls-remote --heads origin master
test -z "$(git -C /home/ywjang/LBA/Flipped-VQA ls-remote --heads origin \
  feature/lba-inquirer-data-pipeline experiment/lba-augmented-vqa-training)"
```

Expected: fork/default/master preconditions are unchanged.

- [ ] **Step 5: Update and push `LBA_Integration/main` documentation**

In the planning worktree, add the demo branch to `README.md`, explicitly mark
it as a sanitized legacy service contract, and preserve
`fix/khu-integration`.

Commit:

```bash
git add README.md docs/provenance/LBA_Prototypes-inventory.md \
  docs/superpowers/plans/2026-07-23-lba-remote-consolidation.md
git diff --cached --check
git commit -m "Document consolidated LBA branches" \
  -m "- Add the sanitized legacy institution pipeline to the canonical branch map.\n- Record the guarded INQUIRER migration and retained historical branch boundaries."
```

Fast-forward the clean primary `main` worktree explicitly:

```bash
git -C /home/ywjang/LBA/LBA_Integration fetch origin main
test "$(git -C /home/ywjang/LBA/LBA_Integration rev-parse origin/main)" = \
  e0d058b9cefa7f880cba357f3de1676d4c803427
test -z "$(git -C /home/ywjang/LBA/LBA_Integration status --porcelain)"
git -C /home/ywjang/LBA/LBA_Integration merge-base --is-ancestor \
  origin/main main
git -C /home/ywjang/LBA/LBA_Integration merge --ff-only \
  codex/lba-remote-consolidation-plan
git -C /home/ywjang/LBA/LBA_Integration push origin main
```

Expected: `main` advances from local `c01b513` through the reviewed plan/docs
commit; no remote commit is overwritten.

- [ ] **Step 6: Update the local LBA map**

Update `/home/ywjang/LBA/README.md` with:

- `LBA_Integration:demo/legacy-institution-pipeline`;
- `LBA_LAVIS:inquirer/data-export-pipeline`;
- `LBA_LAVIS:inquirer/flipped-vqa-augmentation`;
- `/home/ywjang/kbs/Flipped-VQA` as local artifacts only;
- `greeksharifa/Flipped-VQA` as a retained pre-existing fork.

- [ ] **Step 7: Re-run destructive-action gates**

Verify:

```bash
git -C /home/ywjang/LBA/LBA_Integration ls-remote --heads origin \
  demo/legacy-institution-pipeline fix/khu-integration
git -C /home/ywjang/LBA/LBA_LAVIS ls-remote --heads origin \
  inquirer/data-export-pipeline inquirer/flipped-vqa-augmentation
git -C /home/ywjang/LBA/archivers/LBA_Integration-local-20260723/LBA-ARVQA \
  cat-file -e f572aa4^{commit}
git -C /home/ywjang/LBA/archivers/LBA_Integration-local-20260723/LBA-DramaQG \
  cat-file -e cfe578b^{commit}
test "$(git -C /home/ywjang/LBA/LBA_Integration ls-remote origin \
  refs/heads/fix/khu-integration | cut -f1)" = \
  94579e3078c42759b09c12c7cf066b3a04653131
test "$(git -C /home/ywjang/LBA/Flipped-VQA ls-remote origin \
  refs/heads/master | cut -f1)" = \
  24b91ea2b3cd21746f9b4ae5767e9fbb9aca406c
test -z "$(git -C /home/ywjang/LBA/Flipped-VQA ls-remote --heads origin \
  feature/lba-inquirer-data-pipeline experiment/lba-augmented-vqa-training)"
test "$(git -C /tmp/lba-institution-demo rev-parse HEAD)" = \
  "$(git -C /tmp/lba-institution-demo ls-remote origin \
    refs/heads/demo/legacy-institution-pipeline | cut -f1)"
test "$(git -C /tmp/lba-inquirer-data rev-parse inquirer/data-export-pipeline)" = \
  "$(git -C /home/ywjang/LBA/LBA_LAVIS ls-remote origin \
    refs/heads/inquirer/data-export-pipeline | cut -f1)"
test "$(git -C /tmp/lba-inquirer-data rev-parse inquirer/flipped-vqa-augmentation)" = \
  "$(git -C /home/ywjang/LBA/LBA_LAVIS ls-remote origin \
    refs/heads/inquirer/flipped-vqa-augmentation | cut -f1)"
git -C /tmp/lba-inquirer-data merge-base --is-ancestor \
  inquirer/data-export-pipeline inquirer/flipped-vqa-augmentation
git -C /tmp/lba-prototypes-inventory.git remote update --prune
git ls-remote https://github.com/greeksharifa/LBA_Prototypes.git | sort \
  > /tmp/lba-prototypes-refs.live
gh api repos/greeksharifa/LBA_Prototypes/tags --paginate \
  --jq '.[].name' | sort > /tmp/lba-prototypes-tags.live
gh api repos/greeksharifa/LBA_Prototypes/releases --paginate \
  --jq '.[] | [.id,.tag_name,.target_commitish,.draft,.prerelease] | @tsv' \
  | sort > /tmp/lba-prototypes-releases.live
git -C /tmp/lba-prototypes-inventory.git lfs ls-files --all | sort \
  > /tmp/lba-prototypes-lfs.live
gh api repos/greeksharifa/LBA_Prototypes --jq .default_branch \
  > /tmp/lba-prototypes-default-branch.live
gh api repos/greeksharifa/LBA_Prototypes \
  | jq -S -c '{created_at,full_name,id,node_id}' \
  > /tmp/lba-prototypes-identity.live
cmp /tmp/lba-prototypes-refs.before /tmp/lba-prototypes-refs.live
cmp /tmp/lba-prototypes-tags.before /tmp/lba-prototypes-tags.live
cmp /tmp/lba-prototypes-releases.before /tmp/lba-prototypes-releases.live
cmp /tmp/lba-prototypes-lfs.before /tmp/lba-prototypes-lfs.live
cmp /tmp/lba-prototypes-default-branch.before \
  /tmp/lba-prototypes-default-branch.live
cmp /tmp/lba-prototypes-identity.before \
  /tmp/lba-prototypes-identity.live
test "$(git -C /tmp/lba-prototypes-inventory.git rev-parse refs/heads/main)" = \
  ea8f12c634bdee7908937a4b1f4cda2e458ea009
test "$(git -C /tmp/lba-prototypes-inventory.git rev-parse \
  refs/heads/arvqa-answerability-demo)" = \
  f572aa4d80d432f1642507f6d90de0edbe0abf9f
test "$(git -C /tmp/lba-prototypes-inventory.git rev-parse \
  refs/heads/dramaqg-gradio-bridge)" = \
  cfe578bfec21cca35ede26e655a59922dbd21401
(cd /tmp/lba-institution-demo && \
  python -m pytest tests/test_legacy_institution_pipeline.py -q)
python -m compileall -q \
  /tmp/lba-institution-demo/Integration/services/legacy_institution_pipeline
! git -C /tmp/lba-institution-demo grep -n -I -E \
  '(/home/[^/]+|/data[0-9]+/|/nas-[^/]+/|AKIA[0-9A-Z]{16}|(sk[-_]|ghp_)[A-Za-z0-9_-]{20,}|BEGIN .*PRIVATE KEY|api[_-]?key[[:space:]]*[:=]|access[_-]?token[[:space:]]*[:=]|secret[_-]?key[[:space:]]*[:=]|password[[:space:]]*[:=]|cookie[[:space:]]*[:=]|session[_-]?(id|token)[[:space:]]*[:=]|ipdb|pdb\.set_trace|breakpoint\(|CUDA_VISIBLE_DEVICES=[0-9])' \
  HEAD -- Integration/services/legacy_institution_pipeline \
  tests/test_legacy_institution_pipeline.py
! git -C /tmp/lba-institution-demo log -p origin/main..HEAD -- \
  Integration/services/legacy_institution_pipeline \
  tests/test_legacy_institution_pipeline.py | rg -n -i \
  '(/home/[^/]+|/data[0-9]+/|/nas-[^/]+/|AKIA[0-9A-Z]{16}|(?:sk[-_]|ghp_)[A-Za-z0-9_-]{20,}|BEGIN .*PRIVATE KEY|api[_-]?key\s*[:=]|access[_-]?token\s*[:=]|secret[_-]?key\s*[:=]|password\s*[:=]|cookie\s*[:=]|session[_-]?(?:id|token)\s*[:=]|ipdb|pdb\.set_trace|breakpoint\(|CUDA_VISIBLE_DEVICES=[0-9])'
! git -C /tmp/lba-institution-demo ls-tree -r --name-only HEAD | \
  rg '(^|/)(\.env(?:\..*)?|cookies?(?:\.(?:txt|json))?)$'
prototype_manifest=/home/ywjang/LBA/LBA_Integration/docs/provenance/LBA_Prototypes-inventory.md
prototype_tag_count="$(wc -l < /tmp/lba-prototypes-tags.live)"
prototype_release_count="$(wc -l < /tmp/lba-prototypes-releases.live)"
prototype_lfs_count="$(wc -l < /tmp/lba-prototypes-lfs.live)"
rg -F -x 'repository_id: 1309374491' "$prototype_manifest"
rg -F -x 'repository_node_id: R_kgDOTgt4Gw' "$prototype_manifest"
rg -F -x 'repository_full_name: greeksharifa/LBA_Prototypes' "$prototype_manifest"
rg -F -x 'repository_created_at: 2026-07-23T00:30:07Z' "$prototype_manifest"
rg -F -x 'captured_at: 2026-07-23T04:47:01Z' "$prototype_manifest"
rg -F -x 'deletion_status: already absent before publication' "$prototype_manifest"
rg -F -x 'deletion_confirmed_at: 2026-07-23T06:45:51Z' "$prototype_manifest"
rg -F -x 'authenticated_owner_id: 26247624' "$prototype_manifest"
rg -F -x 'default_branch: main' "$prototype_manifest"
rg -F -x 'main: ea8f12c634bdee7908937a4b1f4cda2e458ea009 | incorporated into LBA_Integration provenance' "$prototype_manifest"
rg -F -x 'arvqa-answerability-demo: f572aa4d80d432f1642507f6d90de0edbe0abf9f | superseded by clean-room API contract' "$prototype_manifest"
rg -F -x 'dramaqg-gradio-bridge: cfe578bfec21cca35ede26e655a59922dbd21401 | superseded by MIT-noticed bridge' "$prototype_manifest"
rg -F -x "tags: ${prototype_tag_count}" "$prototype_manifest"
rg -F -x "releases: ${prototype_release_count}" "$prototype_manifest"
rg -F -x "lfs_objects: ${prototype_lfs_count}" "$prototype_manifest"
```

Expected: new refs exist, `fix/khu-integration` is unchanged, and both local
source objects remain. The SHA equality check passes, tests/compile pass, and
the content/history scans have no findings. Confirm the Step 2 tag, release,
LFS, and head classification inventory and the three exact provenance SHAs are
present in the pushed Integration docs.

- [ ] **Step 8: Delete `LBA_Prototypes` and verify absence**

Already-absent contingency: if the initial inventory was captured successfully,
but immediately before publication the active authenticated account is the
repository owner, its numeric owner ID matches the inventory record, the
owner's repository list contains no `LBA_Prototypes`, the REST API returns 404,
and Git reports the repository as not found, record
`deletion_status: already absent before publication` in the provenance
manifest and do not call any repository-deletion API. This exception applies
only while no repository with the same full name has been recreated. The
identity and live inventory comparisons below remain mandatory whenever this
task performs the deletion itself.

If the repository remains present and the contingency does not apply, run:

```bash
prototype_repository_node_id="$(
  jq -r '.node_id' /tmp/lba-prototypes-identity.before
)"
test "$prototype_repository_node_id" = 'R_kgDOTgt4Gw'
gh api graphql \
  -f query='mutation($id: ID!) {
    deleteRepository(input: {repositoryId: $id}) {
      clientMutationId
    }
  }' \
  -F id="$prototype_repository_node_id"
gh api repos/greeksharifa/LBA_Prototypes
```

Expected: either the already-absent contingency is fully evidenced without a
delete call, or the immutable node-ID-targeted mutation succeeds and the final
REST API call returns 404.

## Task 6: Final Verification and Worktree Cleanup

**Files:** None.

- [ ] **Step 1: Run final ref and ancestry verification**

Verify all new remote SHAs, the INQUIRER ancestry, absence of old Flipped refs,
unchanged Flipped `master`, and unchanged `fix/khu-integration`.

- [ ] **Step 2: Confirm primary checkout preservation**

Run:

```bash
git -C /home/ywjang/LBA/LBA_Integration status --porcelain=v1 -uall \
  > /tmp/lba-integration-status.after
git -C /home/ywjang/LBA/LBA_LAVIS status --porcelain=v1 -uall \
  > /tmp/lba-lavis-status.after
git -C /home/ywjang/LBA/LBA_LAVIS diff --binary \
  > /tmp/lba-lavis-diff.after
git -C /home/ywjang/LBA/Flipped-VQA status --porcelain=v1 -uall \
  > /tmp/lba-flipped-status.after
git -C /home/ywjang/LBA/Flipped-VQA diff --binary \
  > /tmp/lba-flipped-diff.after
cmp /tmp/lba-integration-status.before \
  /tmp/lba-integration-status.after
cmp /tmp/lba-lavis-status.before /tmp/lba-lavis-status.after
cmp /tmp/lba-lavis-diff.before /tmp/lba-lavis-diff.after
cmp /tmp/lba-flipped-status.before /tmp/lba-flipped-status.after
cmp /tmp/lba-flipped-diff.before /tmp/lba-flipped-diff.after
```

Expected: pre-existing user changes remain; no cleanup command has been run in
any primary checkout.

- [ ] **Step 3: Remove only clean disposable worktrees**

Run:

```bash
git -C /home/ywjang/LBA/LBA_Integration worktree remove \
  /tmp/lba-institution-demo
git -C /home/ywjang/LBA/Flipped-VQA worktree remove \
  /tmp/lba-inquirer-data
git -C /home/ywjang/LBA/LBA_Integration worktree remove \
  /tmp/lba-remote-consolidation-plan
test -d /tmp/lba-prototypes-inventory.git
```

Expected: removals succeed only after all work is committed and pushed.
After the deletion audit is complete, remove only the exact temporary mirror
`/tmp/lba-prototypes-inventory.git`:

```bash
test "$(realpath /tmp/lba-prototypes-inventory.git)" = \
  /tmp/lba-prototypes-inventory.git
rm -rf -- /tmp/lba-prototypes-inventory.git
test ! -e /tmp/lba-prototypes-inventory.git
```

- [ ] **Step 4: Remove migrated local refs from the old Flipped checkout**

Run only after the worktree removal and remote verification:

```bash
git -C /home/ywjang/LBA/Flipped-VQA update-ref -d \
  refs/heads/inquirer/data-export-pipeline \
  "$(git -C /home/ywjang/LBA/LBA_LAVIS rev-parse inquirer/data-export-pipeline)"
git -C /home/ywjang/LBA/Flipped-VQA update-ref -d \
  refs/heads/inquirer/flipped-vqa-augmentation \
  "$(git -C /home/ywjang/LBA/LBA_LAVIS rev-parse inquirer/flipped-vqa-augmentation)"
git -C /home/ywjang/LBA/Flipped-VQA update-ref -d \
  refs/heads/feature/lba-inquirer-data-pipeline \
  9c862ebd69ad46819dfa8c03bf292fcd35f76c9b
git -C /home/ywjang/LBA/Flipped-VQA update-ref -d \
  refs/heads/experiment/lba-augmented-vqa-training \
  21e45554db9051a2c48eab574a68992200f82fe6
```

Expected: the matching semantic refs remain in `LBA_LAVIS`; no corresponding
local or remote recovery refs remain in the old Flipped checkout.

- [ ] **Step 5: Report the final mapping**

Report:

```text
greeksharifa/LBA_Integration | demo/legacy-institution-pipeline | LBA/LBA_Integration
greeksharifa/LBA_LAVIS | inquirer/data-export-pipeline | LBA/LBA_LAVIS
greeksharifa/LBA_LAVIS | inquirer/flipped-vqa-augmentation | LBA/LBA_LAVIS
```

Also report that `fix/khu-integration` and the pre-existing Flipped fork were
preserved, and `LBA_Prototypes` was deleted.
