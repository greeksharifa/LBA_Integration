# LBA Integration — 2024 snapshot

This branch preserves the KAIST, Kyung Hee University (KHU), and Seoul
National University (SNU) integration code from `main` and freezes public
components at the latest compatible commits published by
`2024-12-31T23:59:59Z`.

## Components and provenance

| Path | Role and owner | Upstream / license | Frozen commit |
| --- | --- | --- | --- |
| `LBA-ARVQA` | answerability reasoning; hee-suk-yoon / KAIST | <https://github.com/hee-suk-yoon/LBA-ARVQA>; no root license in this snapshot | `0a3c12884c099eab3d06813617b7f99674b373ab` |
| `LBA-DramaQG` | sub-question generation; gminipark / KHU | <https://github.com/gminipark/LBA-DramaQG>; MIT | `853e110f9eb62c673552af186d6acc9b98d4d3ac` |
| `SeViLA` | video-language localization/answering; Yui010206 / UNC | <https://github.com/Yui010206/SeViLA>; BSD-3-Clause, Salesforce | `419e7281da60169d98ca7e81dbce10c8d4019b6b` |
| `LBA_SIMPLE_LAVIS` | local LAVIS-derived model and evaluation integration | <https://github.com/salesforce/LAVIS>; BSD-3-Clause | tracked in this repository |
| `Integration/` | KAIST/KHU exchange formats and historical integration samples | LBA project collaborators | tracked in this repository |
| `LBA_SNU/` | SNU orchestration and final-answer/demo layer | SNU integration team | tracked in this repository |

The integration repository is maintained at
<https://github.com/greeksharifa/LBA_Integration> and its root code is under
`LICENSE.txt`. Submodules retain their own license and reuse terms.

## Integration flow

The runtime accepts video or image context plus a main question. KAIST modules
provide answerability/video evidence, KHU produces a clarifying sub-question,
and the SNU layer combines the returned sub-answer with the main question to
produce a final answer. JSON files under `Integration/` and `output_sample/`
show historical interchange formats; they are examples, not regenerated build
products.

## Setup

```bash
git clone --branch 2024 --recurse-submodules \
  https://github.com/greeksharifa/LBA_Integration.git
cd LBA_Integration
git submodule update --init --recursive
```

Install the Python/CUDA dependencies required by the selected component and
its README. The local LAVIS paths require PyTorch, torchvision, decord,
OpenCV, OmegaConf, transformers, and the UI package used by the chosen demo.

Actual UI entrypoints present in this branch are:

```bash
# Streamlit multipage LAVIS application
streamlit run LBA_SIMPLE_LAVIS/app/main.py

# SNU Gradio video/question integration (loads a large model at startup)
python LBA_SNU/demo.py --port 7862

# Upstream-style InstructBLIP Gradio image demo
python LBA_SIMPLE_LAVIS/projects/instructblip/run_demo.py
```

Datasets, videos, model weights/checkpoints, caches, virtual environments, and
generated datasets/results are not versioned. Configure their paths locally;
do not commit credentials or machine-specific artifacts. Existing tracked
sample outputs are retained only for historical compatibility.
