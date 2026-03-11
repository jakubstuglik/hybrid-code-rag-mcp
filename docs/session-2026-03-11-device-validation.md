# Session Changes — OpenVINO Intel GPU Support, Device Validation, mtime Fix

**Date:** 2026-03-11
**Commits:** `eec5b4c` (committed) + uncommitted changes on top
**Author:** AI agent (OpenCode / Claude)

## Purpose

This document describes all changes made across two sessions on 2026-03-11. It is intended
for another AI agent that needs to merge these changes with its own work.

The committed work is in `eec5b4c` ("Intel Iris (openvino) embedding support").
Additional uncommitted changes build on top of that commit.

---

## Summary of All Changes

### Committed in `eec5b4c` (12 files, +369 -169 lines)

1. **OpenVINO Intel GPU embedding support** — the main feature. Allows embedding on Intel
   integrated/discrete GPUs (Iris Xe, Arc) without NVIDIA CUDA. ~15x faster than CPU-only.
2. **Config import audit** — all shared modules now take `cfg` as a required parameter instead
   of importing the base `config` module directly. This ensures override configs (like
   `self-index/config.py`) are always respected.
3. **OpenVINO config and documentation** — new config section, README instructions, and
   `requirements_openvino.txt`.

### Uncommitted (on top of `eec5b4c`)

4. **Device validation** — new function that checks hardware before loading the embedding model
5. **mtime removal from change detection** — incremental indexing no longer false-positives on cloned repos
6. **Config defaults adjustment** — base `config.py` tweaked for the current dev machine
7. **Tests** — 40 new tests for the device validation code
8. **.gitignore** — additional entries for source/schemas symlinks

---

## Committed Changes (eec5b4c): OpenVINO Support + Config Audit

### What was done

The embedding system was extended to support Intel GPU acceleration via OpenVINO as an
alternative to NVIDIA CUDA. This required:

1. A new code path in `get_embed_model()` that uses `OpenVINOEmbedding` instead of
   `HuggingFaceEmbedding` when `USE_OPENVINO_EMBEDDING=True`
2. Removing direct `import config` from all shared modules and replacing it with a
   required `cfg` parameter — so override configs (self-index, etc.) are always used
3. Updating all callers to pass `cfg=config` (where config is the merged config from
   `config_loader`)

### Files modified in `eec5b4c`

#### `shared/embedding.py` — OpenVINO branch in `get_embed_model()`

The core change. `get_embed_model()` now:
- Takes `cfg` as a **required** parameter (raises `ValueError` if None)
- Checks `cfg.USE_OPENVINO_EMBEDDING` — if True, takes the OpenVINO branch:
  - Lazy-imports `OpenVINOEmbedding` from `llama_index.embeddings.huggingface_openvino`
  - Uses `model_id_or_path=` (not `model_name=` like the HuggingFace path)
  - Injects `trust_remote_code=True` via `model_kwargs` (required for Jina model)
  - Uses `OPENVINO_EMBED_DEVICE` config for device placement
  - The `device` parameter passed to `get_embed_model()` is **completely ignored** when
    OpenVINO is active — OpenVINO manages its own device
- If OpenVINO is not enabled, falls back to the existing `HuggingFaceEmbedding` path

The `check_truncation()` function was also updated with a tokenizer access shim:
```python
# OpenVINOEmbedding uses ._tokenizer, HuggingFaceEmbedding uses ._model.tokenizer
if hasattr(embed_model, "_tokenizer"):
    tokenizer = embed_model._tokenizer
else:
    tokenizer = embed_model._model.tokenizer
```

`embed_dense_batch()` and `embed_sparse_batch()` also take `cfg` as a required parameter now.

#### `shared/indexing.py` — Config audit

Removed `import config`. `load_all_sources()` now takes `cfg` as a required parameter.

#### `shared/manifest.py` — Config audit

Removed `import config`. `map_path_to_qdrant()`, `map_path_from_qdrant()`, and
`get_source_files()` now take `cfg` as a required parameter. Raises `ValueError` if None.

#### `index_rag.py` — Caller updates

- Added `cfg=config` to all calls to `get_embed_model()`, `embed_dense_batch()`,
  `embed_sparse_batch()`, `load_all_sources()`, and manifest functions
- Removed old monkey-patching pattern (`shared.manifest.config = config`)

#### `rag_mcp.py` — Caller updates

- Added `cfg=config` to `get_embed_model(device=config.MCP_EMBED_DEVICE, cfg=config)`
- Removed monkey-patching
- When OpenVINO is enabled, `MCP_EMBED_DEVICE` is effectively ignored by `get_embed_model()`

#### `validate_rag.py` — Caller updates

- Added `cfg=config` to `get_embed_model()` call
- Removed monkey-patching

#### `query_test_index.py` — Caller updates

- Added `cfg=config` to `get_embed_model()` call
- Removed monkey-patching

#### `config.py` — New section 6a (OPENVINO)

Added after the existing section 6 (COMPUTE DEVICES):

```python
# ════════════════════════════════════════════════════════════════════
# 6a. OPENVINO (INTEL GPU ACCELERATION)
# ════════════════════════════════════════════════════════════════════
USE_OPENVINO_EMBEDDING = False  # Set True to use OpenVINO for embeddings
OPENVINO_EMBED_DEVICE = "GPU"   # GPU / CPU / AUTO
```

With full documentation comments explaining prerequisites, verification, and performance.

#### `self-index/config.py` — OpenVINO enabled for self-indexing

```python
USE_OPENVINO_EMBEDDING = True
OPENVINO_EMBED_DEVICE = "GPU"
EMBED_MODEL_KWARGS = {}  # Override to avoid float16 CUDA issues on CPU-only systems
```

The `INDEX_EMBED_DEVICE` and `MCP_EMBED_DEVICE` are set to `"cpu"` with comments noting
they are ignored when OpenVINO is active.

#### `requirements_openvino.txt` — NEW FILE

```
llama-index-embeddings-openvino==0.6.1
openvino==2026.0.0
openvino-tokenizers==2026.0.0.0
optimum==2.1.0
optimum-intel==1.27.0
nncf==3.0.0
```

Separate from main `requirements.txt` — only needed on Intel GPU systems.

#### `README.md` — Section 3.2 (Intel GPU / OpenVINO)

User-facing setup instructions: install, verify GPU visibility, configure.

#### `tests/shared/test_manifest.py` — Updated for `cfg` parameter

All 59 manifest tests updated to pass `cfg=mock_config` to the functions that now require it.

---

## Uncommitted Changes (on top of eec5b4c)

### 1. `shared/embedding.py` — Device validation functions (NEW CODE, lines 87-209)

**What was added:**

- `DeviceCheckResult` dataclass (line 87) — holds `ok: bool`, `errors: List[str]`, `warnings: List[str]`
- `_check_cuda_available()` (line 102) — wraps `torch.cuda.is_available()` with ImportError safety
- `_check_cuda_device_name()` (line 112) — wraps `torch.cuda.get_device_name(0)` with safety
- `_check_openvino_devices()` (line 124) — wraps `openvino.Core().available_devices` with safety
- `validate_device_config(cfg)` (line 134) — main validation function

**How `validate_device_config` works:**

It reads three config attributes (with safe `getattr` defaults):
- `USE_OPENVINO_EMBEDDING` (default `False`)
- `OPENVINO_EMBED_DEVICE` (default `"GPU"`)
- `INDEX_EMBED_DEVICE` (default `"cpu"`)

Then probes actual hardware and checks for mismatches:

| Scenario | Result |
|----------|--------|
| OpenVINO enabled, but not installed | **ERROR** — cannot proceed |
| OpenVINO enabled, GPU requested, no Intel GPU | **ERROR** — cannot proceed |
| OpenVINO enabled, CUDA also available | **WARNING** — CUDA is typically faster |
| CUDA device requested, no CUDA available | **ERROR** — cannot proceed |
| CPU device, CUDA GPU available | **WARNING** — suggest CUDA |
| CPU device, Intel GPU available via OpenVINO | **WARNING** — suggest OpenVINO |
| Everything matches | OK, no messages |

Errors are fatal (indexing aborts). Warnings prompt user confirmation (skippable with `--yes`).

**No existing code was modified** in this file. The new code was inserted between `is_zero_vector()` (line 84) and `get_embed_model()` (now line 212). All existing functions, signatures, and line numbers shifted down by ~125 lines.

### 2. `index_rag.py` — Two changes

#### 2a. Device validation call (lines 326-342, inside `run_indexing()`)

Added at the very top of `run_indexing()`, before any model loading or Qdrant connection:

```python
check = validate_device_config(config)
if check.errors:
    for err in check.errors:
        log_error(err)
    log_error("Fix the device configuration and re-run.")
    sys.exit(1)
if check.warnings:
    for warn_msg in check.warnings:
        log_warn(warn_msg)
    if not args.yes:
        confirm = input("Continue anyway? [y/N]: ").strip().lower()
        if confirm not in ("y", "yes"):
            log("Aborted.")
            sys.exit(0)
```

Also added `validate_device_config` to the import block (line 32).

**Key behavior:** Errors abort with `sys.exit(1)`. Warnings prompt interactively unless `--yes` flag was passed. This runs BEFORE `get_embed_model()` is ever called, so misconfigured systems get a clear message instead of a PyTorch/OpenVINO stack trace.

#### 2b. mtime removal from change detection (lines 414-420, inside `determine_actions()`)

**Before:**
```python
if current["hash"] != old_entry.get("hash", "") or int(
    current["mtime"]
) != int(old_entry.get("mtime", 0)):
    actions["modify"].append(path_key)
```

**After:**
```python
# Compare by content hash only — mtime differs across machines
# (git clone, copy, different OS) even when content is identical.
# Hash (SHA-256) is already computed for every file, so mtime
# adds no fast-path benefit, only false-positive re-indexing.
if current["hash"] != old_entry.get("hash", ""):
    actions["modify"].append(path_key)
```

**Why:** When the same repo is cloned on a different machine, file mtimes differ even though content is identical. Since SHA-256 hash is already computed unconditionally for every file, mtime provided zero fast-path benefit but caused false-positive full re-indexing (e.g., 12,533 files flagged as modified when only 30 actually changed). mtime is still stored in the manifest as informational metadata — only the comparison logic changed.

### 3. `config.py` — Two default value changes

```diff
-EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}
+#EMBED_MODEL_KWARGS = {"torch_dtype": "float16"}
+EMBED_MODEL_KWARGS = {}
```

And:

```diff
-USE_OPENVINO_EMBEDDING = False
+USE_OPENVINO_EMBEDDING = True
```

**Context:** The first change disables float16 in the base config because on CPU-only systems (no CUDA), `torch_dtype: float16` causes assertion errors. The second change enables OpenVINO by default since the dev machine has an Intel GPU. **These are dev-machine-specific tweaks** — other machines may want different defaults. The self-index override config (`self-index/config.py`) already had both of these set correctly from the previous session.

### 4. `tests/shared/test_embedding_device.py` — NEW FILE (40 tests)

Comprehensive test suite for the device validation code. Structure:

| Test class | Tests | What it covers |
|------------|-------|----------------|
| `TestDeviceCheckResult` | 4 | Dataclass defaults, independent instances |
| `TestCheckCudaAvailable` | 4 | CUDA available, not available, torch missing, import error |
| `TestCheckCudaDeviceName` | 4 | Name returned, not available, torch missing, runtime error |
| `TestCheckOpenvinoDevices` | 4 | Devices returned, CPU only, not installed, init exception |
| `TestValidateDeviceConfigOpenVINO` | 6 | OV not installed, GPU missing, GPU ok, CUDA warning, CPU device, case insensitive |
| `TestValidateDeviceConfigPyTorch` | 7 | CUDA missing, cuda:0 missing, CUDA ok, CPU+CUDA warn, CPU+OV warn, no GPU, OV CPU only |
| `TestValidateDeviceConfigEdgeCases` | 11 | Missing attrs, empty config, both GPUs, early return, actionable messages, requirements mention |

All hardware detection is mocked via `unittest.mock.patch` on the three helper functions. No real GPU/OpenVINO probing happens during tests.

### 5. `.gitignore` — Additional entries

Added duplicate entries for `source` and `schemas` symlinks (with and without leading `/`). These are symlinks to external data directories that should never be committed.

---

## Architecture: How OpenVINO Integrates

```
config.py (or override)
  USE_OPENVINO_EMBEDDING = True/False
  OPENVINO_EMBED_DEVICE = "GPU"/"CPU"/"AUTO"
  INDEX_EMBED_DEVICE = "cuda"/"cpu"        (ignored when OpenVINO active)
  MCP_EMBED_DEVICE = "cpu"                 (ignored when OpenVINO active)
       │
       ▼
validate_device_config(cfg)    ← called first in run_indexing()
  probes: torch.cuda, openvino.Core()
  returns: errors (abort) / warnings (prompt)
       │
       ▼
get_embed_model(device=..., cfg=...)
  if USE_OPENVINO_EMBEDDING:
    → OpenVINOEmbedding(model_id_or_path=..., device=OPENVINO_EMBED_DEVICE)
  else:
    → HuggingFaceEmbedding(model_name=..., device=INDEX_EMBED_DEVICE)
```

Key design decisions:
- OpenVINO is a **completely separate code path** — no mixing with PyTorch CUDA/CPU logic
- `device` parameter to `get_embed_model()` is **ignored** when OpenVINO is active
- `trust_remote_code=True` is injected via `model_kwargs` for OpenVINO (vs top-level kwarg for HuggingFace)
- Dynamic VRAM cap (`EMBED_DYNAMIC_VRAM_CAP`) is NOT used in the OpenVINO path
- OpenVINO deps are in separate `requirements_openvino.txt` — not in main `requirements.txt`

---

## How to Verify

```bash
# Run all tests (should be 913 total — 873 original + 40 new)
.venv\Scripts\python.exe -m pytest --tb=short -q

# Run only the new device validation tests
.venv\Scripts\python.exe -m pytest tests/shared/test_embedding_device.py -v
```

---

## Merge Notes

### Committed changes (`eec5b4c`)

- **`shared/embedding.py`**: `get_embed_model()` signature changed from `(device=None)` to `(device=None, cfg=None)`. New OpenVINO branch inside. Tokenizer shim in `check_truncation()`. `embed_dense_batch()` and `embed_sparse_batch()` gained `cfg` parameter.
- **`shared/indexing.py`**: `load_all_sources()` gained `cfg` parameter. `import config` removed.
- **`shared/manifest.py`**: Three functions gained `cfg` parameter. `import config` removed.
- **`index_rag.py`**, **`rag_mcp.py`**, **`validate_rag.py`**, **`query_test_index.py`**: All shared function calls now pass `cfg=config`. Old monkey-patching removed.
- **`tests/shared/test_manifest.py`**: All 59 tests pass `cfg=mock_config`.
- **`config.py`**: New section 6a added (lines ~148-171).
- **`self-index/config.py`**: Three new settings added.
- **`requirements_openvino.txt`**: New file.
- **`README.md`**: Section 3.2 added.

### Uncommitted changes

- **`shared/embedding.py`**: All new code is an INSERT between line 84 and the old line 85 (now 212). No existing lines were modified. If the other branch modified `get_embed_model()` or later functions, the merge should be clean — just a line number shift.
- **`index_rag.py`**: Two separate change locations — the import block (line 32) and `run_indexing()` (lines 326-342), and `determine_actions()` (lines 414-420). If the other branch modified different parts of these functions, the merge should be clean.
- **`config.py`**: The two value changes (EMBED_MODEL_KWARGS and USE_OPENVINO_EMBEDDING) may conflict if the other branch also changed these. Take whichever values are correct for the target machine.
- **`tests/shared/test_embedding_device.py`**: Entirely new file, no merge conflict possible.
- **`.gitignore`**: Append-only changes, should merge cleanly.
