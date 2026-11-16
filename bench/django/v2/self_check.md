# v2 self-check: are these questions actually hard?

The v1 pilot of P01–P10 showed a ceiling effect: the `none` control
(no retrieval, `read_file` only) scored 9/10 at 2. Those questions named
well-known public APIs (`HttpResponse`, `authenticate`, cache backends)
that grok-4.7 already knew. v2 is written so that a score of 2 requires
an exact file **and** a line range within ±10 of a verified span, and so
that the *identifiers themselves* are mostly private helpers, 6.x-only
machinery (tasks, CSP, template partials, fetch modes; Django 6.0 was
released 2025-12-03, Django 6.1 on 2026-08-05), or behaviour described
without names.

The clone used for keys is a depth-1 checkout of tag 6.1.3
(`f16e25dcb9fe55734ba4ea2b00ac34405b7df74a`), so git blame on a shallow clone is not
available. Locations were taken from the tree at that SHA and checked
with `../scripts/verify_keys.py`. Recency is from the 6.0 / 6.1 public
release notes plus the `RemovedInDjango2028Warning` shims in this tag
(`_get_from_db`, `URLIZE_ASSUME_HTTPS`).

## Rejected as too easy (would likely hit the file from memory)

These were considered and **not** used as exact-lookup items, because a
model that had seen the 6.0/6.1 release notes could name the path
without opening the tree:

- “Where is the class `ContentSecurityPolicyMiddleware` defined?” —
  guess `django/middleware/csp.py` (correct).
- “Where is the class `Task` / the `@task` decorator defined?” —
  guess `django/tasks/base.py` or `django/tasks/__init__.py` (often right).
- “Where is `{% partialdef %}` implemented?” —
  guess `django/template/defaulttags.py` (correct file).
- “Where is the default for `SECURE_CSP`?” —
  guess `django/conf/global_settings.py` (correct file).

Those topics still appear in **semantic** and **cross-file** items, but
the required symbols are the internals (`build_policy`, `process_response`,
`partialdef_func`, `PartialTemplate`, `_make_csp_decorator`) and a score
of 2 still needs the line range.

## Ten official items, guessed from memory (no tools)

Guesses below were made from parametric knowledge *before* treating the
answer key as known. “Hit” means the guess would have named the correct
file **and** the required symbol. Line numbers were not guessed; under
the v2 rubric a memory-only answer without a location scores at most 1
anyway.

| ID | What was asked (short) | Memory guess | Hit file+symbol? | Kept? |
| --- | --- | --- | --- | --- |
| E201 | `TASK_MIN_PRIORITY` assignment | Did not know this constant existed | No | Yes |
| E202 | `CSP.NONCE` sentinel | Maybe `django/middleware/csp.py` (wrong file) | No | Yes |
| E203 | `generate_nonce` | `django/utils/crypto.py` / `get_random_string` (wrong) | No | Yes |
| E204 | class `FetchPeers` | `django/db/models/query.py` (wrong file) | No | Yes |
| E210 | class `PartialTemplate` | `defaulttags.py` or `loader_tags.py` (wrong; it is `template/base.py`) | No | Yes |
| S201 | serialize a CSP directive mapping to a header, substituting a placeholder | Would not have named `build_policy` | No | Yes |
| S204 | private method that actually runs an immediate task | Might name `ImmediateBackend.enqueue`, miss `_execute_task` | No | Yes |
| S212 | descriptor that lazily sets an instance fetch mode to the single-row default | Would not have named `ModelStateFetchModeDescriptor` | No | Yes |
| C205 | which engine method splits `template#partial`, and which class is returned | Might guess `django.template.loader.get_template`, miss `Engine.get_template` + `PartialTemplate` | No | Yes |
| C209 | fetch-mode class that refuses to load a field, and the exception it raises | Might guess `FieldError` in `exceptions.py`; would not name `FetchRaise` in `fetch_modes.py` | No | Yes |

No replacement was required for these ten. A later model that has been
trained on this repository or on Django 6.1.3 line-for-line could of
course do better; the line-range rule and the retrieval-tool gate are
there to keep a score of 2 tied to actually looking at this checkout.

## Pool shape

Official 40: 10 exact_lookup (E201–E210), 15 semantic (S201–S215), 15
cross_file (C201–C215). Pilot 10 is a disjoint set (Q2P01–Q2P10; 3 E,
4 S, 3 C) with no shared required symbols.

## v2.1 (2026-11-15): why the v2 pilot still hit the ceiling, and what changed

The v2 pilot's `none` runs all opened the file they named from memory
(e.g. `django/tasks/base.py` for `TASK_MAX_PRIORITY`) and read the line
numbers off it. The questions named either the identifier or a
self-describing subsystem (tasks, CSP), so the path was easy to infer.
v2.1 removes file access from `none` (pure memory) and moves the old
behaviour to the `read_only` control. Items were also replaced so that the
path is hard to infer even for `read_only`.

### New v2.1 pilot pool (Q3P01–Q3P10)

| id | cat | answer | why it is hard without search |
|---|---|---|---|
| Q3P01 | E | `django/utils/http.py:214-225` `split_directive_names` | 6.x helper; name does not imply `utils/http.py` |
| Q3P02 | E | `django/core/mail/handler.py:8` `DEFAULT_MAILER_BACKEND` | 6.1 mailers module; one-line constant |
| Q3P03 | E | `django/template/defaultfilters.py:669-691` `_walk_items` | private helper in a 997-line module |
| Q3P04 | S | `django/http/request.py:436-442` `HttpRequest._check_data_too_big` | described without identifiers; private, new in 6.x |
| Q3P05 | S | `django/contrib/staticfiles/storage.py:246-252` `HashedFilesMixin.is_in_ignored_block` | described by behaviour only |
| Q3P06 | S | `django/core/checks/mail.py:41-63` `check_mailers_production_backend` | 6.1-only check |
| Q3P07 | S | `django/dispatch/dispatcher.py:27-38` `_restore_context` | private async helper, behaviour only |
| Q3P08 | C | `django/core/mail/handler.py:44-78` + `django/core/mail/exceptions.py:13-18` | 6.1 mailers, two files |
| Q3P09 | C | `django/db/backends/sqlite3/_functions.py:515-516` + `django/db/models/functions/uuid.py:80-85` | backend registration + expression method |
| Q3P10 | C | `django/contrib/auth/__init__.py:391-399` + `django/contrib/auth/backends.py:65-78` | behaviour only, caller in another file |

### Replaced items in `questions.jsonl`

| id | old (guessable) | new |
|---|---|---|
| E201 | `TASK_MIN_PRIORITY` (tasks/base.py) | `_get_permission_metadata` — `contrib/auth/management/__init__.py:114-124` |
| E202 | `CSP.NONCE` (utils/csp.py) | `NO_DEFAULT_MAILER_WARNING` — `core/mail/deprecation.py:24-27` |
| E203 | `generate_nonce` (utils/csp.py) | `_traverse_ancestors` — `db/models/fields/related_descriptors.py:120-129` |
| E204 | `FetchPeers` (fetch_modes.py) | `trim_value` — `utils/text.py:264-278` |
| E205 | `_make_csp_decorator` (views/decorators/csp.py) | `get_blank_choice_label` — `db/models/utils.py:74-81` |
| E207 | `CONTEXT_KEY` (utils/csp.py) | `safe_makedirs` — `utils/_os.py:60-62` |
| E208 | `FieldFetchBlocked` (core/exceptions.py) | `translation_catalog_exists` — `utils/translation/trans_real.py:481-493` |
| S202 | nonce helper (duplicate of E203) | `Signal._flag_dead_receivers` — `dispatch/dispatcher.py:526-533` |
| S207 | `check_tasks` (tasks/checks.py) | `QuerySet._handle_order_with_respect_to` — `db/models/query.py:938-967` |
| S209 | `LazyNonce` (utils/csp.py) | `Media._normalize_css` — `forms/widgets.py:158-165` |
| S215 | `QuerySet.fetch_mode` (duplicate of C210) | `HttpRequest.accepted_types_by_precedence` — `http/request.py:110-119` |

New symbols were taken from a diff of definitions between Django 5.2 and
this commit where possible (new or moved code), checked against the
checkout with `scripts/verify_keys.py`, and every new span equals the AST
`lineno..end_lineno` of the symbol. The remaining 29 items are unchanged.
Expected effect: `none` loses the ability to copy line numbers, so items
need a recalled ±10-line range; `read_only` has to infer non-obvious
paths before it can read anything.
