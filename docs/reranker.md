# Reranker

After hybrid retrieval (BM25 + dense, Relative Score Fusion) and branch-overlay
dedup, every result list goes through `rerank_results()` in
`src/shared/reranker.py`. The reranker adds bonuses and penalties to the fused
score and re-sorts. It is a query-time step: changing it never needs a reindex.

## Generic core + per-language profiles

The core knows only language-neutral concepts:

- overview phrasing ("what is X", "describe X", "explain X", "structure of X", ...);
- target identifiers: path components, capitalised identifiers, digit-bearing
  file stems, and code-shaped identifiers (see below);
- the generic chunk types `class_overview`, `class_summary`(`_split`),
  `method_group`, comment chunks and `import_group`;
- the score arithmetic and the query-intent rules.

Everything language- or format-specific lives in a `RerankProfile`
(`src/shared/rerank_profile.py`). Each reader attaches its profile as
`<Reader>.rerank_profile` (the `RERANK_PROFILE` constant at the end of each
`*_reader.py`).

**Which profiles are active.** By default, only the profiles of the readers
registered for the extensions in `SOURCE_DIRS` (`rerank_profiles_for_config`).
A Java-only project is never influenced by the SQL, Delphi or C++ rules. Set
`RERANK_PROFILES` in a project config to override the selection:

```python
RERANK_PROFILES = ["java", "hibernate_mapping", "sql"]   # or "all"
```

Profile names: `delphi`, `delphi_forms`, `delphi_project`, `fastreport`,
`sql`, `python`, `java`, `groovy`, `kotlin`, `javascript`, `csharp`, `go`,
`php`, `cpp`, `qt_forms`, `hibernate_mapping`, `jasperreports`.

### Profile fields

| Field | Used for |
|---|---|
| `target_patterns` | Pull target identifiers (file stems, class/object names) out of a query |
| `overview_types`, `artifact_overview_types`, `detail_types`, `import_types` | Classify the reader's node types for overview queries |
| `overview_query_patterns` | Extra overview phrasings |
| `domains` | Query intents (e.g. "report structure") that make one chunk type the primary answer |
| `targets_code_class` | Predicate: the query names a code class, so artefact overviews (forms, reports) are demoted |
| `declaration_name_patterns` | Names a chunk declares, beyond the generic rules (properties, constants, Go receivers, JS/TS arrow properties, ...) |
| `test_path_patterns` | File paths that hold test code in this language |
| `binding_path_patterns`, `binding_text_patterns` | Thin glue layers (JNI, C API wrappers, FFI) |
| `is_declaration_chunk` | Predicate `(node_type, file_path)` for declaration-only chunks (headers, prototypes) |

`java_style_profile(name, file_stem_pattern, test_paths=(), declaration_names=())`
builds a profile for readers that emit the Java chunk conventions (Java,
Kotlin, Groovy, Python, C#, Go, PHP).

## Overview queries

When the query is an overview query, the reranker over-fetches
`OVERFETCH_MULTIPLIER` (10) × `top_k` candidates (`get_retrieval_top_k`), then
re-scores them and trims back to `top_k`:

| Adjustment | Value |
|---|---|
| Primary overview chunk (`class_overview`, `class_summary`, or a domain's primary type) | +0.65 |
| Secondary overview type from a profile | +0.25 |
| Artefact overview (form, report, mapping) / class summary in domain mode | +0.10 |
| Artefact overview when the query names a code class | −0.15 |
| Chunk matches the target file/class (scaled by match) | +0.15 |
| Overview chunk of a non-target file (scaled by 1 − match) | −0.40 |
| Comment chunk of a non-target file | −0.30 |
| Import / include list | −0.25 |
| Detail chunk (method, field, ...) | −0.05 |
| Overview chunk whose class name **exactly** equals a target | +0.20 |
| Overview chunk whose class name only **contains** the target (e.g. `ParserOptions` for `Parser`) | −0.10 |

## Query-intent rules (all queries)

Non-overview queries are retrieved with `top_k` candidates and keep their
original order **unless** one of these rules fires:

| Rule | Adjustment | Exemption |
|---|---|---|
| The query contains a code-shaped identifier and the chunk declares that name | +0.25 (+0.10 more when the owner also matches) | Overview queries use the target rules instead |
| Test file (core `tests/`, `__tests__/`, `__mocks__/` + profile `test_path_patterns`) | −0.15 | The query mentions tests (`test`, `spec`, `fixture`, `mock`, `stub`, `assert…`, `pytest`/`junit`/`gtest`..., `test_x`, `x_test`, `…Test`) |
| Binding / glue chunk (profile `binding_*` patterns) | −0.15 | The query mentions JNI, Java, C API, FFI, bindings, wrappers or `extern "C"` |
| Declaration-only chunk (profile `is_declaration_chunk`), non-overview queries only | −0.10 | The query asks for a declaration, header, prototype, signature, interface, abstract or forward declaration |

**Code-shaped identifiers** (`extract_code_identifiers`): `snake_case`,
`camelCase`, `PascalCase` with at least two humps, and qualified names
`Owner::member`, `Owner.member`, `obj->member`. File names such as
`server.go` are not identifiers.

**Declared names** (`chunk_declared_names`) come from reader metadata
(`object_name`, `function_name`, ...), the generic `def` / `function` /
`func` / `class` / `procedure` keywords, the first `name(` or `Owner::name(`
signature on the first code lines (comment, decorator and header lines are
skipped), and the `declaration_name_patterns` of the profile that owns the
chunk's file. A call on the right-hand side of an assignment is not a
declaration.

## Changing the reranker

- Constants are at the top of each section in `src/shared/reranker.py`.
- Unit tests: `src_test/shared/test_reranker.py`, `test_reranker_intent.py`,
  `test_rerank_profiles.py`.
- Re-run the validation suites of every project the change can affect
  (`python src/validate_rag.py --config <name> --tests <suite.yaml>`), see
  [docs/validation/validation-tests-guide.md](validation/validation-tests-guide.md).
