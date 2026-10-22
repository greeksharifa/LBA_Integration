# LBA Integration

Canonical integration hub for the Learning by Asking (LBA) project. Use the
dated branches for reproducible snapshots and `main` for the current repository
map and integration baseline.

## Branches

| Branch | Purpose | Status |
| --- | --- | --- |
| [`2022`](https://github.com/greeksharifa/LBA_Integration/tree/2022) | Exact, history-preserving import of `greeksharifa/LBA_Integration_2022` `main` | Historical snapshot; current scene-graph generation uses the pinned `cross-graph-attention` submodule on `main` |
| [`2023`](https://github.com/greeksharifa/LBA_Integration/tree/2023) | 2022 architecture with public KAIST ARVQA and KHU DramaQG frozen at the 2023 year-end cutoff | Reproducible snapshot at `ef499a26bd3b371e219abefd8458dd667130854c` |
| [`2024`](https://github.com/greeksharifa/LBA_Integration/tree/2024) | Current integration tree plus curated SNU/LAVIS video-processing work and public components frozen at the 2024 year-end cutoff | Reproducible snapshot at `f0feea5ffa87db4d23a5f77d75b228cba02cdec1` |
| [`demo/legacy-institution-pipeline`](https://github.com/greeksharifa/LBA_Integration/tree/demo/legacy-institution-pipeline) | Sanitized legacy KAIST answerability to KHU question-generation service contract and client orchestration | Published at `73e38070bf5f77a3d07dec20fe2e6ac9b8b96415`; contains no copied ARVQA model implementation |
| [`fix/khu-integration`](https://github.com/greeksharifa/LBA_Integration/tree/fix/khu-integration) | Earlier KHU integration work retained as historical context | Unchanged at `94579e3078c42759b09c12c7cf066b3a04653131`; not folded into the sanitized demo contract |
| [`server-preserve/20261022/lba-integration-local-20260723`](https://github.com/greeksharifa/LBA_Integration/tree/server-preserve/20261022/lba-integration-local-20260723) | Preserves the recovered `LBA_Integration-local-20260723` checkout and its component revisions | Published separately because its `main` history diverged from the current repository `main`; not merged into the canonical baseline |
| `main` | Canonical navigation and current tracked integration baseline | Active hub; not a dated reproducibility guarantee |

## Related repository branches

| Repository / branch | Purpose | Status |
| --- | --- | --- |
| [`LBA_LAVIS:inquirer/data-export-pipeline`](https://github.com/greeksharifa/LBA_LAVIS/tree/inquirer/data-export-pipeline) | Sanitized INQUIRER normalization and data-export pipeline | Published at `d482657b2114acf70ccdc4ec6b59cc868254572f` |
| [`LBA_LAVIS:inquirer/flipped-vqa-augmentation`](https://github.com/greeksharifa/LBA_LAVIS/tree/inquirer/flipped-vqa-augmentation) | Flipped-VQA augmentation built on the sanitized INQUIRER export branch | Published at `638bcb83a4d9cc26432480622b2982b200622b17` |
| [`LBA_LAVIS:server-preserve/20261022/lba-lavis-sq-instructblip`](https://github.com/greeksharifa/LBA_LAVIS/tree/server-preserve/20261022/lba-lavis-sq-instructblip) | Preserves the server's SQ-InstructBLIP checkout, including Qwen2.5-VL Questioner generation | Published separately because the local and remote `SQ-InstructBLIP` histories diverged; not merged into the existing branch |
| [`greeksharifa/Flipped-VQA:master`](https://github.com/greeksharifa/Flipped-VQA/tree/master) | Pre-existing fork of `mlvlab/Flipped-VQA` | Retained unchanged at `24b91ea2b3cd21746f9b4ae5767e9fbb9aca406c`; migrated INQUIRER source refs were removed after guarded publication |

## Ownership and provenance

| Area | Owner / institution | Upstream and license |
| --- | --- | --- |
| Integration repository | `greeksharifa`; LBA consortium integration | This repository; root `LICENSE.txt` (BSD-3-Clause) |
| `LBA-ARVQA` | `hee-suk-yoon`; KAIST | <https://github.com/hee-suk-yoon/LBA-ARVQA>; no root license in the referenced snapshot |
| `LBA-DramaQG` | `gminipark`; Kyung Hee University | <https://github.com/gminipark/LBA-DramaQG>; MIT |
| `SeViLA` | `Yui010206`; UNC | <https://github.com/Yui010206/SeViLA>; BSD-3-Clause, Salesforce |
| `cross-graph-attention` | `youngyoung1021`; scene-graph generator | <https://github.com/youngyoung1021/cross-graph-attention>; pinned submodule |
| LAVIS base | Salesforce | <https://github.com/salesforce/LAVIS>; BSD-3-Clause |
| `LBA_SNU` and local orchestration | SNU integration team | Tracked in this repository under the root license |

Submodule licenses govern their own source. A missing license is not permission
to reuse that component; contact its owner when terms are unclear.

## Current `main` map

| Path | Contents | Current gitlink |
| --- | --- | --- |
| `LBA-ARVQA` | KAIST answerability/video reasoning | `066672025e136a9b4b24d076b0d6d665c1c5e58f` |
| `LBA-DramaQG` | KHU question generation | `76a181828577593ab5c216c8eee18104872bfbda` |
| `SeViLA` | video-language localization and answering | `419e7281da60169d98ca7e81dbce10c8d4019b6b` |
| `cross-graph-attention` | ARVQA scene-graph generation | pinned submodule |
| `Integration/` | historical KAIST/KHU exchange code and sample formats | tracked files |
| `LBA_SIMPLE_LAVIS/` | local LAVIS model, evaluation, and UI code | tracked files |
| `LBA_SNU/` | SNU orchestration and Gradio integration demo | tracked files |
| `output_sample/` | small historical output examples | tracked files |

## Clone and initialize

```bash
git clone --recurse-submodules \
  https://github.com/greeksharifa/LBA_Integration.git
cd LBA_Integration
git submodule update --init --recursive
```

For a snapshot, add `--branch 2022`, `--branch 2023`, or `--branch 2024` to
the clone command. Submodule commits are pinned by the selected parent branch;
do not use `git submodule foreach git pull` for a reproducible checkout.

## Demo entrypoints

These UI entrypoints are present in the repository; each loads its own model
and dependencies:

```bash
streamlit run LBA_SIMPLE_LAVIS/app/main.py
python LBA_SNU/demo.py --port 7862
python LBA_SIMPLE_LAVIS/projects/instructblip/run_demo.py
```

## Artifact policy

Keep datasets, source videos/images, model weights and checkpoints, virtual
environments, caches, logs, and generated datasets/results outside Git. Store
only small, intentional fixtures or historical examples. Configure artifact
paths locally, initialize submodules from their public upstreams, and never
commit credentials or machine-specific secrets.

## Server inventory provenance

The container-level LBA map that was outside any Git repository is preserved
as a dated source snapshot at
[`docs/server-inventory/LBA-container-README.md`](docs/server-inventory/LBA-container-README.md).
This snapshot records the original local inventory and attribution; use this
README and the branch links above as the current repository map. Independent archived
child source patches and exact restoration bases are retained in the
[server source preservation index](docs/server-inventory/README.md).

The `greeksharifa/Flipped-VQA` fork is archived and read-only. The server's
separate `local/flipped-vqa-workspace` branch contains DramaQA sub-question source
that is absent from the migrated INQUIRER branch. Its complete commit patches and
[comparison evidence](docs/server-inventory/flipped-vqa-comparison.md) are retained
in this repository; the fork's `master` branch was not changed.
