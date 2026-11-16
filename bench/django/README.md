# Django 6.1.3 retrieval benchmark

A retrieval/localization comparison (ripgrep, hybrid-code-rag-mcp,
claude-context, Serena, plus a no-retrieval control `none`) driven by the
Grok Build CLI.

Official v2.1 results: [results/official_table.md](results/official_table.md),
[results/pilot_table.md](results/pilot_table.md), and the README chart
[results/django_bench.png](results/django_bench.png). Raw run logs are
kept locally and are not in this repository.

Start here: [METHOD.md](METHOD.md). Section 16 records the 2026-11-14
amendments after the Zakładki AI review (fifth variant, interleaving,
bootstrap CIs, authorship, external pool). The official 40 questions,
the Stage 1 pilot 10, and the other hashes in [SHA256SUMS](SHA256SUMS)
are unchanged.

A separate externally sourced pool (X01–X10) lives in
[external_questions.jsonl](external_questions.jsonl); it is **not** used
in the Stage 2 pilot. See [EXTERNAL_SHA256SUMS](EXTERNAL_SHA256SUMS).

Pinned subject tree (not vendored in this repo):
`https://github.com/django/django` tag `6.1.3`, commit
`f16e25dcb9fe55734ba4ea2b00ac34405b7df74a`.
On the benchmark host the clone is `C:\Apps\hcr-bench\django`.
