# Flipped-VQA source comparison

Comparison date: 2026-10-22. The local `LBA/Flipped-VQA` workspace is retained. Its exact fork `greeksharifa/Flipped-VQA` is archived/read-only; `master` remains `24b91ea2b3cd21746f9b4ae5767e9fbb9aca406c`.

## Related migrated implementation

`greeksharifa/LBA_LAVIS:inquirer/flipped-vqa-augmentation` (`638bcb83a4d9cc26432480622b2982b200622b17`) is the existing related source home. It contains the original Flipped-VQA baseline and a separate INQUIRER augmentation/data-export pipeline. The local workspace contains three subsequent commits ending at `5b05038dbb3e615e2cc92b489c1a85a6052cbb4f`.

The local DramaQA sub-question/VQA-Introspect dataloaders, statistics helper, launchers and workflow/checkpoint documentation are absent from the migrated branch. Shared dataloader/engine/tokenizer/train files also differ because the migrated branch implements INQUIRER-specific paths and augmentation. The archived uncertainty workspace adds another independent DramaQA evaluation helper patch, preserved as `patches/flipped-vqa-upstream.patch`. These are distinct changes; no runtime merge or cherry-pick was performed.

## Preservation and reconstruction

The [workspace manifest](flipped-vqa-workspace-manifest.json) binds the three commit patches to the exact base and HEAD tree. Applying the full series in a temporary index reproduced the source HEAD tree exactly. Use `git am patches/flipped-vqa-workspace/*.patch` from a clone at the manifest base to restore the commit series. These patches preserve source and docs, not ignored datasets/checkpoints or a validated training environment.

The ignored `/home/ywjang/LBA/Flipped-VQA/Flipped-VQA_unchanged` backup differs from its base in three tracked source/docs files (`README.md`, `engine.py`, `eval.py`) and adds the small `test.sh` launcher. Those four exact changes are retained in [a base-specific patch](patches/flipped-vqa-unchanged.patch) and [manifest](flipped-vqa-unchanged-manifest.json); the patch reconstructs the listed file hashes from `24b91ea2...`. The launcher and evaluation side effect were preserved as source only and were not run.

`/home/ywjang/kbs/Flipped-VQA` is a separate, non-Git artifact workspace. Its LICENSE, dataset registry, KG/How2QA loaders, tokenizer, export helpers, tests and documentation are already present in the migrated INQUIRER branch. The branch has newer path overrides, safer How2QA segment normalization, rank-gated routine loader logs, and path-symbolic docs/tests; KBS variants are older and include workstation-specific paths. The only KBS source file absent from that tree is a zero-byte, unreferenced `conditional_prob.py`. The KBS `split_data.py` variant is a manual dataset JSON generator with an absolute external data path; the migrated tree already contains a path-configurable version of the same generator, so the old variant was not copied. KBS LICENSE content matches the canonical LICENSE. Dataset files, weights, generated thesis outputs and artifacts remain excluded. `greeksharifa/VQA_Commonsense` is an unrelated LXMERT project. The public `mlvlab/Flipped-VQA` branch diverges from the local workspace, so no upstream push was attempted.
