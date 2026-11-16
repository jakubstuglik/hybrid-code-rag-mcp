# Django 6.1.3 retrieval benchmark — v2

Harder question pool, stricter location rubric, and a system prompt that
requires the retrieval tool. Frozen v1 artefacts in `../` (hashes in
`../SHA256SUMS`) are left untouched and remain the historical record of
the Stage 2 pilot.

- Checkout: Django tag `6.1.3`, commit `f16e25dcb9fe55734ba4ea2b00ac34405b7df74a`
- Official pool: `questions.jsonl` / `answer_key.jsonl` (E201–E210, S201–S215, C201–C215)
- Pilot pool (v2.1): `pilot21_questions.jsonl` / `pilot21_answer_key.jsonl` (Q3P01–Q3P10)
- Pilot pool (v2, run 14/15.11, historical): `pilot_questions.jsonl` / `pilot_answer_key.jsonl` (Q2P01–Q2P10)
- Prompts: `prompts/system_v2.txt` (retrieval variants), `prompts/system_v21_none.txt` (`none`, pure memory),
  `prompts/system_v21_read_only.txt` (`read_only` control); `prompts/system_v2_none.txt` is the v2-pilot `none` prompt (historical)
- Controls and v2.1 changes: `../METHOD.md` §18
- Rubric: `grading.md` (score 2 needs file + symbol + line range ±10)
- Night run: `NIGHT_CHECKLIST.md`, entry point `night/run_night_v21.ps1`

Verify keys (from `bench/django`):

```
python scripts/verify_keys.py --repo C:\Apps\hcr-bench\django --questions v2\questions.jsonl
python scripts/verify_keys.py --repo C:\Apps\hcr-bench\django --questions v2\pilot_questions.jsonl
python scripts/verify_keys.py --repo C:\Apps\hcr-bench\django --questions v2\pilot21_questions.jsonl
```
