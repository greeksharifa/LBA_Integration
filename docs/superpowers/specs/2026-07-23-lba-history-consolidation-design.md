# LBA History Consolidation Design

## Goal

Preserve every branch and commit from `LBA_Integration_2022`, and integrate
`LBA_Growing_Knowledge` into the 2023 LBA snapshot without losing its source
history or submodule pins.

## Current Evidence

- Sources:
  - `git@github.com:greeksharifa/LBA_Integration_2022.git`
  - `git@github.com:greeksharifa/LBA_Growing_Knowledge.git`
- `LBA_Integration_2022:main` is exactly `LBA_Integration:2022`.
- The source `integration` and `fix/*` histories already exist in later target
  branches.
- `LBA_Integration_2022:subtask3` commit `5268982` is not reachable from any
  target ref and must be added.
- `LBA_Growing_Knowledge` has 16 commits and 30 tree leaves that are absent
  from every `LBA_Integration` branch.

## Design

### LBA_Integration_2022

Fetch all source branches and publish exact, namespaced refs in the target.
The ref manifest is authoritative:

```text
refs/heads/legacy/LBA_Integration_2022/main
  1b1f5d0aa714c412b414ef5718a3e597e4cf44e3
refs/heads/legacy/LBA_Integration_2022/integration
  89dce18e2e502dacce950ee722de340f71c9d9de
refs/heads/legacy/LBA_Integration_2022/subtask3
  5268982c1e23c4373e4fae13588731b16c15a158
refs/heads/legacy/LBA_Integration_2022/fix/kaist-integration
  e15b0e0bb819d67c2902a9b3680432fa6f32e1ea
refs/heads/legacy/LBA_Integration_2022/fix/khu-integration
  e15b0e0bb819d67c2902a9b3680432fa6f32e1ea
```

These refs point at the original source SHAs. Existing target branches remain
unchanged. This makes the missing `subtask3` commit reachable while retaining
the original branch meanings.

### LBA_Growing_Knowledge

Import source `main` into target branch `2023` at:

```text
LBA_Growing_Knowledge/
```

The source tip is fixed at
`e78d039a46c4ce772117780455e7d2c9d56313f5`. Use a non-squash
`git subtree add` so this exact tip and all 16 source commits remain ancestors
of the resulting 2023 branch. Keep the imported
`LBA_Growing_Knowledge/.gitmodules` byte-for-byte. Separately add working,
prefixed declarations to the target root `.gitmodules`.

The seven root declarations and pins are:

```text
LBA_Growing_Knowledge/AGQA_baselines_code
  https://github.com/madeleinegrunde/AGQA_baselines_code.git
  be802aec4552727f1fc17266b3033061b679c58b
LBA_Growing_Knowledge/ActionGenome
  https://github.com/JingweiJ/ActionGenome.git
  db36ffb56dfc0e78af82147af9712e870c5bfea7
LBA_Growing_Knowledge/ChatCaptioner
  https://github.com/Vision-CAIR/ChatCaptioner.git
  e4c63eeedaa40fceac52ef6a555a9ae608feaa81
LBA_Growing_Knowledge/STAR_Benchmark
  https://github.com/csbobby/STAR_Benchmark.git
  6db9d158585cb78372107dba72fedcd6b41a63e0
LBA_Growing_Knowledge/baseline_models/HME-VideoQA
  https://github.com/fanchenyou/HME-VideoQA.git
  66cc4ccff3113595b7a7230b1cc73063e4382e27
LBA_Growing_Knowledge/baseline_models/PSAC
  https://github.com/lixiangpengcs/PSAC.git
  249c36393120352bfa7af4ac1e9182bc63ee6152
LBA_Growing_Knowledge/baseline_models/hcrn-videoqa
  https://github.com/thaolmk54/hcrn-videoqa.git
  eb92c9b21aaa00f912fe5c2e5188abc47fda5211
```

Update the 2023 README with source repository, original tip SHA, import path,
and submodule initialization instructions.

## Error Handling

- Abort if any source tip differs from the investigated SHA.
- Abort unless `LBA_Integration_2022` still has exactly the five manifested
  heads and no tags; newly added or removed source refs require a new manifest
  and design review before integration.
- Abort if target `2023` is not fast-forwardable from the fetched remote.
- Do not resolve collisions by dropping source files.
- Do not update `main`, `2022`, or `2024` while integrating the 2023 snapshot.
- Push only explicit `HEAD:refs/heads/2023` and manifest refspecs. Never use
  `--mirror`, wildcard refspecs, force push, or an upstream remote as a target.

## Validation

- `git ls-remote` reports each of the five namespaced refs at the exact
  manifest SHA, not merely at a descendant.
- Source `git ls-remote --heads --tags` matches exactly the five manifested
  heads and an empty tag set.
- Source `subtask3` SHA `5268982` resolves in the target.
- All 16 `LBA_Growing_Knowledge` commits are ancestors of target `2023`.
- Prefix-stripped source and imported file trees match byte-for-byte,
  including the nested source `.gitmodules`.
- Seven root-prefixed submodule declarations resolve to their fixed gitlinks
  in a fresh clone using `git submodule update --init --recursive`.
- Before and after remote manifests match for all pre-existing refs except
  `2023`. Fixed baselines include `main=e0d058b9cefa7f880cba357f3de1676d4c803427`,
  `2022=1b1f5d0aa714c412b414ef5718a3e597e4cf44e3`, and
  `2024=f0feea5ffa87db4d23a5f77d75b228cba02cdec1`.
- `git fsck --full` succeeds.
