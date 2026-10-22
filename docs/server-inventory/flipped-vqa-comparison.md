# Flipped-VQA source comparison

Comparison date: 2026-10-22. The local `LBA/Flipped-VQA` workspace is retained. Its exact fork `greeksharifa/Flipped-VQA` is archived/read-only; `master` remains `24b91ea2b3cd21746f9b4ae5767e9fbb9aca406c`.

## Related migrated implementation

`greeksharifa/LBA_LAVIS:inquirer/flipped-vqa-augmentation` (`638bcb83a4d9cc26432480622b2982b200622b17`) is the existing related source home. It contains the original Flipped-VQA baseline and a separate INQUIRER augmentation/data-export pipeline. The local workspace contains three subsequent commits ending at `5b05038dbb3e615e2cc92b489c1a85a6052cbb4f`.

The local DramaQA sub-question/VQA-Introspect dataloaders, statistics helper, launchers and workflow/checkpoint documentation are absent from the migrated branch. Shared dataloader/engine/tokenizer/train files also differ because the migrated branch implements INQUIRER-specific paths and augmentation. The archived uncertainty workspace adds another independent DramaQA evaluation helper patch, preserved as `patches/flipped-vqa-upstream.patch`. These are distinct changes; no runtime merge or cherry-pick was performed.

## Preservation and reconstruction

The [workspace manifest](flipped-vqa-workspace-manifest.json) binds the three commit patches to the exact base and HEAD tree. Applying the full series in a temporary index reproduced the source HEAD tree exactly. Use `git am patches/flipped-vqa-workspace/*.patch` from a clone at the manifest base to restore the commit series. These patches preserve source and docs, not ignored datasets/checkpoints or a validated training environment.

`/home/ywjang/kbs/Flipped-VQA` is a separate, non-Git artifact workspace. It includes additional conditional-probability, KG/How2QA and thesis-QA code and differs from the retained Git workspace; it is not covered by these patches or a source-push completion claim. `greeksharifa/VQA_Commonsense` is an unrelated LXMERT project. The public `mlvlab/Flipped-VQA` branch diverges from the local workspace, so no upstream push was attempted.
