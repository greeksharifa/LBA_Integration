# LBA Integration — 2023 snapshot

This branch preserves the 2022 LBA integration architecture and freezes the
public ARVQA and DramaQG components at the latest commits published by
`2023-12-31T23:59:59Z`. Third-party code remains in its upstream repositories;
this repository stores only submodule references.

## Frozen components

| Path | Owner / institution | Upstream | Commit |
| --- | --- | --- | --- |
| `LBA-ARVQA` | hee-suk-yoon / KAIST | <https://github.com/hee-suk-yoon/LBA-ARVQA> | `e7d34c0ed94b7a5d7698bc5e56caee64e098a800` |
| `LBA-DramaQG` | gminipark / Kyung Hee University | <https://github.com/gminipark/LBA-DramaQG> | `1ba4b00eafbdbc42ac234a01f61b25889d67a99b` |

The integration also retains the 2022 references for `DramaQA`
(`643db2beb8e19f46c872ecb14a878add7f183ea3`), `ood-diffusion`
(`72f0cddb675ce62a78f88bede0588ba63ad09c3`), and
`Scene-Graph-Extraction` (`8e63c7ded8adc2312b47007593b15d2a499ce9cd`).
The last upstream URL is a historical reference and is no longer publicly
cloneable.

The root integration is MIT licensed. `LBA-DramaQG` declares MIT; the ARVQA
snapshot has no root license file, so consult its owner before reuse.

## Setup

```bash
git clone --branch 2023 --recurse-submodules \
  https://github.com/greeksharifa/LBA_Integration.git
cd LBA_Integration
git submodule update --init --recursive
```

The integration expects datasets, model weights, checkpoints, generated
datasets, and results to be supplied separately. They are intentionally not
versioned. If recursive initialization reaches the unavailable historical
`Scene-Graph-Extraction` URL, initialize the other paths individually.
