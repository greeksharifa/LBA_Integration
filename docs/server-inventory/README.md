# Server source preservation

This folder preserves the LBA container map and source changes from independent archived/vendor checkouts. These patches record existing implementation and local environment choices; they are not applied to current integration code.

- [Container map snapshot](LBA-container-README.md): attributed original inventory.
- [Patch manifest](patch-manifest.json): exact source/base commits, SHA-256 and paths for five independent child repositories.
- [Flipped-VQA comparison](flipped-vqa-comparison.md), [workspace patch manifest](flipped-vqa-workspace-manifest.json), and [ignored-backup patch manifest](flipped-vqa-unchanged-manifest.json): retained workspace versus the existing INQUIRER augmentation branch; the workspace series reconstructs its source tree and the backup patch preserves its four changed/added source files.
- `patches/`: VideoChat2 recovery environment, DramaQA Flipped-VQA evaluation, ARVQA and DramaQG launchers, and SeViLA evaluation workflows. Each patch was checked against its exact base using an isolated Git index.

To restore a patch, clone its original upstream, check out the manifest base commit, then run `git am <patch>` for commit-mail patches. The ignored-backup `flipped-vqa-unchanged.patch` is a plain diff; restore it with `git apply <patch>` instead. Review local data/model/cache paths and dependencies before execution. Syntax and patch application checks do not establish GPU/model/data availability or benchmark reproducibility. Notebook outputs in the small preserved patch are historical observations. Large datasets, media, model weights, environments and generated results stay outside this source archive.

On 2026-10-22 the user requested deletion of the local LLaVA checkout and the archived DeepSeek-VL2/vLLM children. Their prior local-only source is not included here. The retained Flipped-VQA workspace was compared with the existing migrated INQUIRER branch; missing source is preserved here as commit patches.
