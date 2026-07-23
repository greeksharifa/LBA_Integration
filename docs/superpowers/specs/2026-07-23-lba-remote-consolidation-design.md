# LBA Remote Consolidation Design

## Objective

Consolidate the recovered institution-demo and INQUIRER/Flipped-VQA work into
the existing LBA repositories without exposing credentials, machine-specific
paths, generated artifacts, or debug-only code.

## Scope

- Publish a sanitized legacy institution pipeline demo on a semantic
  `greeksharifa/LBA_Integration` branch.
- Preserve `greeksharifa/LBA_Integration:fix/khu-integration` unchanged.
- Delete the temporary private `greeksharifa/LBA_Prototypes` repository only
  after the sanitized replacement has been verified remotely.
- Move the two recovered INQUIRER/Flipped-VQA branches to
  `greeksharifa/LBA_LAVIS`.
- Remove only those two newly added branches from the pre-existing
  `greeksharifa/Flipped-VQA` fork.
- Update the LBA repository map to describe the final ownership boundaries.

## Non-Goals

- Do not delete or rewrite the pre-existing `greeksharifa/Flipped-VQA` fork.
- Do not modify the dirty `master` checkout at `/home/ywjang/LBA/Flipped-VQA`.
- Do not move datasets, checkpoints, generated QA files, or model weights.
- Do not make the legacy institution demo production-ready or retrain models.
- Do not alter `fix/khu-integration`.

## Current Provenance

### Institution demo

The two `LBA_Prototypes` branches are legacy component snapshots:

- ARVQA `f572aa4` descends from the KAIST commit pinned by
  `LBA_Integration:2023`.
- DramaQG `cfe578b` descends from the KHU history used by the 2023 integration
  snapshot.

Their intended flow is:

```text
KAIST ARVQA answerability service
  -> KHU DramaQG sub-question service
  -> existing SNU sub-answer/final-answer demo
```

The recovered source also contains CRLF churn, debug code, fixed qids, fixed
GPU selection, absolute `/home` and `/data*` paths, and inconsistent service
ports. The complete component histories must not be merged into the
`LBA_Integration` main history.

### INQUIRER and Flipped-VQA

The recovered branch ancestry is:

```text
mlvlab/Flipped-VQA upstream/main 3692f47
└── feature/lba-inquirer-data-pipeline 9c862eb
    └── experiment/lba-augmented-vqa-training 21e4555
```

The first branch normalizes and exports KBS/INQUIRER generated QA. The second
adds the KBS augmentation loaders and training path used to evaluate INQUIRER
QA with Flipped-VQA as a downstream backbone.

## Design Decisions

### 1. Sanitized institution-demo branch

Create `demo/legacy-institution-pipeline` from `LBA_Integration/main`.

Add only the integration-specific service contract under
`Integration/services/legacy_institution_pipeline/`:

- a clean-room ARVQA client interface implemented from the observed JSON/API
  contract without copying expression from the unlicensed ARVQA source;
- a minimal DramaQG bridge that preserves the upstream MIT notice and isolates
  the permitted integration-specific client behavior;
- a concise README describing the KAIST -> KHU -> SNU data flow, provenance,
  runtime dependencies, and legacy status.

The branch will reference existing component directories and will not vendor
the full unrelated ARVQA or DramaQG histories. No ARVQA implementation,
function body, comments, or documentation prose will be copied into the public
branch.

Sanitization requirements:

- no credentials, tokens, private keys, cookies, or environment dumps;
- no personal home paths or server-specific `/data*` paths;
- no fixed GPU number;
- no fixed qid or image path;
- no `ipdb`, breakpoint, debug-only early return, or generated output;
- service URLs, ports, dataset roots, image paths, checkpoints, and output
  paths must be explicit CLI arguments or environment-backed settings;
- default networking is loopback-only unless the operator explicitly selects
  another bind address.

The legacy branch documents the service contract but does not claim a
full-model end-to-end run without the external datasets and checkpoints.

### 2. Preserve the KHU-named branch

`fix/khu-integration` remains byte-for-byte unchanged at
`94579e3078c42759b09c12c7cf066b3a04653131`, even though its history is
unrelated to current `main`. It is not used as the base of the new demo branch.

### 3. Move Flipped-derived work to LBA_LAVIS

Use isolated temporary worktrees to reconstruct sanitized replacement commits
from the two existing branches. Publish the replacements to `LBA_LAVIS` as:

- `inquirer/data-export-pipeline`
- `inquirer/flipped-vqa-augmentation`

The second branch remains a descendant of the first. Their Flipped-VQA upstream
history is preserved; they are not rebased onto the unrelated `LBA_LAVIS` code
history. The replacement commits must remove personal `/home/...` paths,
server-specific `/data*` paths, debug statements, breakpoints, and generated
artifact references from both code and documentation. Configurable CLI
arguments, environment-backed settings, test fixtures, or neutral placeholders
replace values that are operationally required. New remote SHAs are recorded
during implementation.

After both new remote refs match the verified commits, delete only:

- `greeksharifa/Flipped-VQA:feature/lba-inquirer-data-pipeline`
- `greeksharifa/Flipped-VQA:experiment/lba-augmented-vqa-training`

The existing fork, `master`, and upstream relationship remain unchanged.

### 4. Delete the temporary prototype repository last

Delete `greeksharifa/LBA_Prototypes` only after:

1. all remote heads, tags, releases, LFS state, and default-branch metadata
   have been inventoried;
2. the three current heads (`main` `ea8f12c...`, ARVQA `f572aa4...`, and
   DramaQG `cfe578b...`) have been classified as migrated or intentionally
   superseded;
3. the local archived ARVQA and DramaQG object stores still resolve the two
   source commits, and the provenance summary from `main` is included in the
   Integration documentation;
4. the sanitized institution-demo branch is present on
   `greeksharifa/LBA_Integration`;
5. its staged and committed content passes the sensitive-data scan;
6. the remote branch commit matches the local commit;
7. the retained adapter files compile and their lightweight tests pass.

No permanent duplicate bundle is created because the two source commits remain
in the explicitly retained local archive object stores and their source code is
either superseded by clean-room adapters or intentionally not republished.

## Validation

### Institution demo

- Build and commit in an isolated temporary worktree based on
  `LBA_Integration/main`; do not switch or clean the primary checkout.
- Parse/compile all new Python files.
- Run unit tests with model loading and remote Gradio calls mocked.
- Verify configurable endpoint, port, qid, media path, checkpoint, and output
  path handling.
- Scan the branch diff and reachable new blobs for credential patterns,
  `/home/`, `/data*`, fixed GPU selection, `ipdb`, and generated artifacts.
- Verify `fix/khu-integration` is
  `94579e3078c42759b09c12c7cf066b3a04653131` before and after all pushes.

### INQUIRER branches

- Build in isolated temporary worktrees; do not switch, clean, or modify the
  dirty primary `LBA_LAVIS` and `Flipped-VQA` checkouts.
- Record the source SHAs:
  - data export source: `9c862ebd69ad46819dfa8c03bf292fcd35f76c9b`
  - augmentation source: `21e45554db9051a2c48eab574a68992200f82fe6`
- Record and verify the new sanitized remote SHAs.
- Verify the data-export branch is an ancestor of the augmentation branch.
- Re-run the 12 data-pipeline tests and compile the augmented loaders.
- Scan the complete two-branch delta for personal paths, server-specific data
  paths, credentials, fixed GPU selection, and debug statements.
- Verify the two old refs are absent from `greeksharifa/Flipped-VQA`.
- Before and after ref deletion, verify that `greeksharifa/Flipped-VQA` still
  exists, remains a fork of `mlvlab/Flipped-VQA`, has default branch `master`,
  and retains `master` at
  `24b91ea2b3cd21746f9b4ae5767e9fbb9aca406c`.

### Repository deletion

- Verify the new Integration branch before deletion.
- Delete `LBA_Prototypes`.
- Confirm the repository is no longer returned by the GitHub API.

## Documentation

- Update `LBA_Integration/README.md` on `main` with the legacy demo branch and
  its limitations in a separate documentation commit, then push and verify the
  new `main` SHA.
- Update `/home/ywjang/LBA/README.md` so that:
  - `LBA_Integration` owns the legacy institution pipeline demo;
  - `LBA_LAVIS` owns the two INQUIRER/Flipped-derived branches;
  - `/home/ywjang/kbs/Flipped-VQA` remains the local data/checkpoint/export
    workspace;
  - the pre-existing Flipped-VQA fork is not described as a newly created
    repository.

## Residual Risks

- ARVQA has no root license in the pinned snapshot. The public branch therefore
  uses a clean-room client contract and provenance only, not ARVQA-derived code
  or a copied ARVQA source tree.
- Full runtime validation requires external models, checkpoints, datasets, and
  GPUs; this consolidation validates interfaces and import/compile behavior
  only.
- The dirty local Flipped-VQA `master` checkout remains intentionally
  unaudited and unchanged.
