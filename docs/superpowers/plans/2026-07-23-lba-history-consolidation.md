# LBA History Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fully preserve `LBA_Integration_2022` refs and integrate all `LBA_Growing_Knowledge` content and history into `LBA_Integration:2023`.

**Architecture:** Exact legacy refs are copied without rewriting. `LBA_Growing_Knowledge:main` is added with a non-squash subtree merge at `LBA_Growing_Knowledge/`; its nested `.gitmodules` remains archival while root `.gitmodules` gains functional prefixed declarations.

**Tech Stack:** Git, git-subtree, Git submodules, Markdown

---

### Task 1: Lock remote manifests

**Files:**
- Reference: `docs/superpowers/specs/2026-07-23-lba-history-consolidation-design.md`

- [ ] **Step 1: Fetch target and source refs**

```bash
git fetch --prune origin
git remote add integration-2022 git@github.com:greeksharifa/LBA_Integration_2022.git
git remote add growing-knowledge git@github.com:greeksharifa/LBA_Growing_Knowledge.git
git fetch --prune integration-2022 '+refs/heads/*:refs/remotes/integration-2022/*' '+refs/tags/*:refs/tags/integration-2022/*'
git fetch --prune growing-knowledge '+refs/heads/*:refs/remotes/growing-knowledge/*'
```

Expected: no fetch conflict.

- [ ] **Step 2: Verify fixed tips and source ref inventory**

```bash
test "$(git rev-parse integration-2022/main)" = 1b1f5d0aa714c412b414ef5718a3e597e4cf44e3
test "$(git rev-parse integration-2022/integration)" = 89dce18e2e502dacce950ee722de340f71c9d9de
test "$(git rev-parse integration-2022/subtask3)" = 5268982c1e23c4373e4fae13588731b16c15a158
test "$(git rev-parse integration-2022/fix/kaist-integration)" = e15b0e0bb819d67c2902a9b3680432fa6f32e1ea
test "$(git rev-parse integration-2022/fix/khu-integration)" = e15b0e0bb819d67c2902a9b3680432fa6f32e1ea
test "$(git rev-parse growing-knowledge/main)" = e78d039a46c4ce772117780455e7d2c9d56313f5
test "$(git ls-remote --heads integration-2022 | wc -l | tr -d ' ')" = 5
test -z "$(git ls-remote --tags integration-2022)"
```

Expected: every test exits 0.

- [ ] **Step 3: Record immutable target refs**

```bash
git ls-remote --heads origin > /tmp/lba-integration-heads-before.tsv
test "$(git rev-parse origin/main)" = e0d058b9cefa7f880cba357f3de1676d4c803427
test "$(git rev-parse origin/2022)" = 1b1f5d0aa714c412b414ef5718a3e597e4cf44e3
test "$(git rev-parse origin/2023)" = ef499a26bd3b371e219abefd8458dd667130854c
test "$(git rev-parse origin/2024)" = f0feea5ffa87db4d23a5f77d75b228cba02cdec1
```

Expected: all SHAs match.

### Task 2: Publish exact LBA_Integration_2022 refs

**Files:** None; refs only.

- [ ] **Step 1: Push five explicit namespaced refs**

```bash
git push origin \
  integration-2022/main:refs/heads/legacy/LBA_Integration_2022/main \
  integration-2022/integration:refs/heads/legacy/LBA_Integration_2022/integration \
  integration-2022/subtask3:refs/heads/legacy/LBA_Integration_2022/subtask3 \
  integration-2022/fix/kaist-integration:refs/heads/legacy/LBA_Integration_2022/fix/kaist-integration \
  integration-2022/fix/khu-integration:refs/heads/legacy/LBA_Integration_2022/fix/khu-integration
```

Expected: five new branches; no force update.

- [ ] **Step 2: Verify exact remote tips**

Run `git ls-remote --heads origin 'refs/heads/legacy/LBA_Integration_2022/*'` and compare every row to the spec manifest.

Expected: five exact SHA/ref pairs.

### Task 3: Import LBA_Growing_Knowledge

**Files:**
- Create: `LBA_Growing_Knowledge/**`

- [ ] **Step 1: Confirm clean feature branch based on origin/2023**

```bash
git status --short
git merge-base --is-ancestor origin/2023 HEAD
test ! -e LBA_Growing_Knowledge
```

Expected: clean status, directory absent.

- [ ] **Step 2: Add non-squashed subtree**

```bash
git subtree add \
  --prefix=LBA_Growing_Knowledge \
  growing-knowledge \
  e78d039a46c4ce772117780455e7d2c9d56313f5
```

Expected: merge commit; source tip is a parent/ancestor.

- [ ] **Step 3: Verify source ancestry and tree equality**

```bash
git merge-base --is-ancestor e78d039a46c4ce772117780455e7d2c9d56313f5 HEAD
git diff --exit-code \
  e78d039a46c4ce772117780455e7d2c9d56313f5^{tree} \
  HEAD:LBA_Growing_Knowledge
```

Expected: both commands exit 0.

### Task 4: Make prefixed submodules functional

**Files:**
- Modify: `.gitmodules`
- Modify: `README.md`

- [ ] **Step 1: Add seven root `.gitmodules` declarations**

Add the exact path/URL pairs from the design spec, including:

```ini
[submodule "LBA_Growing_Knowledge/baseline_models/PSAC"]
	path = LBA_Growing_Knowledge/baseline_models/PSAC
	url = https://github.com/lixiangpengcs/PSAC.git
```

Do not modify `LBA_Growing_Knowledge/.gitmodules`.

- [ ] **Step 2: Add README provenance section**

Document source URL, tip `e78d039...`, import path, 2023 scope, and:

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

- [ ] **Step 3: Validate declarations and pins**

```bash
git config -f .gitmodules --get-regexp '^submodule\..*\.path$' | rg 'LBA_Growing_Knowledge/' | wc -l
git ls-tree -r HEAD LBA_Growing_Knowledge | rg '^160000' | wc -l
```

Expected: both counts are 7.

- [ ] **Step 4: Commit submodule and README changes**

```bash
git add .gitmodules README.md
git commit -m "docs: register growing knowledge submodules"
```

### Task 5: Validate and publish 2023

**Files:** All imported and modified files.

- [ ] **Step 1: Run structural validation**

```bash
git diff --check origin/2023...HEAD
git fsck --full
git merge-base --is-ancestor e78d039a46c4ce772117780455e7d2c9d56313f5 HEAD
```

- [ ] **Step 2: Reconcile a changed remote safely**

```bash
git fetch origin
```

If `origin/2023` changed from `ef499a2...`, merge it with `git merge --no-ff origin/2023`, resolve conflicts without dropping imported files, and rerun validation. Do not rebase away subtree parentage.

- [ ] **Step 3: Push only the 2023 branch**

```bash
git push origin HEAD:refs/heads/2023
```

- [ ] **Step 4: Verify remote state**

Fresh-fetch origin, verify remote `2023` equals local HEAD, all five legacy refs equal the manifest, all pre-existing refs except `2023` equal `/tmp/lba-integration-heads-before.tsv`, and `git fsck --full` succeeds.

