# LBA Integration

Canonical integration hub for the Learning by Asking (LBA) project. Use the
dated branches for reproducible snapshots and `main` for the current repository
map and integration baseline.

## Branches

| Branch | Purpose | Status |
| --- | --- | --- |
| [`2022`](https://github.com/greeksharifa/LBA_Integration/tree/2022) | Exact, history-preserving import of `greeksharifa/LBA_Integration_2022` `main` | Published at `1b1f5d0aa714c412b414ef5718a3e597e4cf44e3`; historical `Scene-Graph-Extraction` URL is no longer public |
| [`2023`](https://github.com/greeksharifa/LBA_Integration/tree/2023) | 2022 architecture with public KAIST ARVQA and KHU DramaQG frozen at the 2023 year-end cutoff | Reproducible snapshot at `ef499a26bd3b371e219abefd8458dd667130854c` |
| [`2024`](https://github.com/greeksharifa/LBA_Integration/tree/2024) | Current integration tree plus curated SNU/LAVIS video-processing work and public components frozen at the 2024 year-end cutoff | Reproducible snapshot at `0a9476963e9e07e7c99c575efa78309cdc8e92c2` |
| `main` | Canonical navigation and current tracked integration baseline | Active hub; not a dated reproducibility guarantee |

## Ownership and provenance

| Area | Owner / institution | Upstream and license |
| --- | --- | --- |
| Integration repository | `greeksharifa`; LBA consortium integration | This repository; root `LICENSE.txt` (BSD-3-Clause) |
| `LBA-ARVQA` | `hee-suk-yoon`; KAIST | <https://github.com/hee-suk-yoon/LBA-ARVQA>; no root license in the referenced snapshot |
| `LBA-DramaQG` | `gminipark`; Kyung Hee University | <https://github.com/gminipark/LBA-DramaQG>; MIT |
| `SeViLA` | `Yui010206`; UNC | <https://github.com/Yui010206/SeViLA>; BSD-3-Clause, Salesforce |
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
