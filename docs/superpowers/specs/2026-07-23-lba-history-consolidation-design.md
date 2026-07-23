# LBA History Consolidation Design

## Goal

Preserve every branch and commit from `LBA_Integration_2022`, and integrate
`LBA_Growing_Knowledge` into the 2023 LBA snapshot without losing its source
history or submodule pins.

## Current Evidence

- `LBA_Integration_2022:main` is exactly `LBA_Integration:2022`.
- The source `integration` and `fix/*` histories already exist in later target
  branches.
- `LBA_Integration_2022:subtask3` commit `5268982` is not reachable from any
  target ref and must be added.
- `LBA_Growing_Knowledge` has 16 commits and 30 tree leaves that are absent
  from every `LBA_Integration` branch.

## Design

### LBA_Integration_2022

Fetch all source branches and publish exact, namespaced refs in the target:

```text
legacy/LBA_Integration_2022/main
legacy/LBA_Integration_2022/integration
legacy/LBA_Integration_2022/subtask3
legacy/LBA_Integration_2022/fix-kaist-integration
legacy/LBA_Integration_2022/fix-khu-integration
```

These refs point at the original source SHAs. Existing target branches remain
unchanged. This makes the missing `subtask3` commit reachable while retaining
the original branch meanings.

### LBA_Growing_Knowledge

Import source `main` into target branch `2023` at:

```text
LBA_Growing_Knowledge/
```

Use a non-squash subtree merge so all 16 source commits remain ancestors of
the resulting 2023 branch. Move the imported submodule declarations into the
target root `.gitmodules` with the directory prefix applied. Add the missing
`baseline_models/PSAC` declaration and retain the exact seven gitlink SHAs.

Update the 2023 README with source repository, original tip SHA, import path,
and submodule initialization instructions.

## Error Handling

- Abort if any source tip differs from the investigated SHA.
- Abort if target `2023` is not fast-forwardable from the fetched remote.
- Do not resolve collisions by dropping source files.
- Do not update `main`, `2022`, or `2024` while integrating the 2023 snapshot.

## Validation

- All five legacy branch tips are reachable from target namespaced refs.
- Source `subtask3` SHA `5268982` resolves in the target.
- All 16 `LBA_Growing_Knowledge` commits are ancestors of target `2023`.
- Prefix-stripped source and imported file trees match.
- Seven prefixed submodules resolve to their original gitlink SHAs.
- `git fsck --full` succeeds.

