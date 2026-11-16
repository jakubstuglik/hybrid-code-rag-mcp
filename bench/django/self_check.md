# Ripgrep self-check (semantic honesty)

The semantic questions are written so that a literal `rg` of words or short phrases from the question should not uniquely land on the ground-truth file. Exact-lookup questions are *expected* to be greppable: they name the identifier on purpose.

Five semantic questions were drawn with `random.Random(20261114).sample(...)` from the 14 semantic items. After a wording fix on S02 (a three-word phrase `the cookie in` had been unique to `django/middleware/csrf.py`), the set is:

`S02`, `S04`, `S08`, `S09`, `S10`

Method, run on 14 November 2026 against `C:\Apps\hcr-bench\django` at `6.1.3` (`f16e25dcb9fe55734ba4ea2b00ac34405b7df74a`):

- Search root: `django/`, `*.py` only, `tests/` excluded (the same scope the harness will index).
- For each content word of length ≥ 4, `rg -l -i` with a word boundary.
- Conjunction of the two rarest words that actually occur somewhere in the tree.
- Every three-word phrase from the question, `rg -l -i` as a literal.

A question **fails** this check if a single question word or a three-word phrase matches only the ground-truth file (or a subset of it), or if the conjunction of the two rarest occurring words equals that file.

A later wording pass also removed `cache-busting` from S12 (not in this sample): that hyphenated term appeared only in `django/contrib/staticfiles/storage.py`. After the change, the same unique-hit scan over all 14 semantic questions reported no remaining unique word or phrase hits.

## S02 — form-protection secret, reversible encoding, constant-time compare

Ground truth: `django/middleware/csrf.py` (`_does_token_match`, `_unmask_cipher_token`).

Words such as `form-protection`, `recovered`, `reversibly`, and `differed` occur in **zero** library files. The rarest words that do occur (`counterpart`, `leak`) hit `django/contrib/gis/gdal/geomtype.py` and `django/template/loaders/cached.py`, not the CSRF middleware. Their conjunction is empty. `secret` hits eight files including the ground truth, which is not a unique solve. Three-word phrases that exist at all (`by the browser`, `that does not`) point at other modules.

**Result:** ripgrep of the question text does not solve S02.

## S04 — secret too close to login name / mailbox

Ground truth: `django/contrib/auth/password_validation.py` (`UserAttributeSimilarityValidator`).

`fuzzy`, `holder`, `mailbox`, and `finds` each hit a **different** unrelated file (compilemessages, settings, SMTP, findstatic). The conjunction of the two rarest occurring words is empty. `rejected` hits three files, one of which is the ground truth — not unique. No three-word phrase from the question appears in `django/*.py`.

**Result:** ripgrep of the question text does not solve S04.

## S08 — attach a zone to a naive datetime

Ground truth: `django/utils/timezone.py` (`make_aware`).

`refuse` occurs nowhere. `carries` occurs once, in `django/db/models/fields/related.py`. The conjunction of `carries` and `attached` is that related-field file, **not** `timezone.py`. `zone` hits 26 files. Three-word phrases match migrations, task backends, and `django/utils/crypto.py`, not the ground truth alone.

**Result:** ripgrep of the question text does not solve S08. (An agent that ANDs rare words would be sent to the wrong file.)

## S09 — join paths without escaping the root

Ground truth: `django/utils/_os.py` (`safe_join`).

`insignificant` and `walks` occur nowhere. `upward` and `stays` hit `django/template/context.py` and multipart/template loaders respectively; their conjunction is empty. Common words such as `directory`, `root`, and `components` hit many files. The only three-word phrase hit, `the result is`, appears in nine unrelated files.

**Result:** ripgrep of the question text does not solve S09.

## S10 — allocate a new session identifier

Ground truth: `django/contrib/sessions/backends/base.py` (`_get_new_session_key`).

`retry` occurs nowhere in this scope. `visitor` hits `django/contrib/sessions/models.py` (the `Session` model), which is **not** the allocation helper. The conjunction of `visitor` and `fresh` is empty. `session` hits 28 files. Three-word phrases such as `already in use` point at `runserver`, PostgreSQL operations, and `django/db/models/base.py`.

**Result:** ripgrep of the question text does not solve S10. Grepping `visitor` alone would even suggest the wrong sessions file.

## Conclusion

On these five sampled semantic questions, literal ripgrep of the question’s words and short phrases does not uniquely (or even jointly) identify the ground-truth implementation. The semantic set is honest enough to start from. Exact-lookup items remain deliberately greppable.
