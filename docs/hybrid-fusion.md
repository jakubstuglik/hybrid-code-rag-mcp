# Hybrid fusion

How hybrid-code-rag-mcp combines the dense (embedding) and sparse (BM25) search legs, and how the weight between them is chosen. All settings here are query-time only: change them in the project config and restart the MCP server, no reindex.

> [!IMPORTANT]
> **Recommended default: `HYBRID_FUSION = "minmax"` with `HYBRID_ALPHA_MODE = "fixed"`** (the behaviour of every earlier version). In our measurements no other combination beat it overall, and adaptive alpha with the default `HYBRID_ALPHA_IDENT = 0.3` made identifier queries worse (see [Measured results](#measured-results)). Try the other modes only together with your own validation suite.

Each query runs two searches in the same Qdrant collection: a dense (embedding) leg and a sparse BM25 leg, each returning up to `HYBRID_PREFETCH_K` candidates. Fusion merges the two lists into one ranked list, which is cut to the reranker input size. `HYBRID_FUSION` in the project config chooses how ([fusion modes](#fusion-modes)). `HYBRID_ALPHA_MODE` can pick the alpha per query ([query-adaptive alpha](#query-adaptive-alpha)); the default `"fixed"` uses one alpha for every query.

## Fusion modes

| | `"minmax"` (default) | `"rrf"` | `"dbsf"` |
|---|---|---|---|
| Uses | raw scores of each leg | rank of each chunk in each leg | raw scores of each leg |
| Fused score | each leg's scores are min-max scaled to 0..1, then `alpha * dense + (1 - alpha) * sparse` (a chunk missing from a leg gets 0 for it) | `(k + 1) * (alpha / (k + rank_dense) + (1 - alpha) / (k + rank_sparse))`, ranks from 1, no term for a leg that missed the chunk | each leg is scaled with its mean `mu` and population standard deviation `sigma`: `(s - (mu - 3*sigma)) / (6*sigma)`, clipped to 0..1 (if `sigma` is 0, every score on that leg is 1), then `alpha * dense + (1 - alpha) * sparse` (a chunk missing from a leg gets 0 for it) |
| `HYBRID_ALPHA` (0.5) | weight of the scaled dense score; 0 = BM25 only, 1 = dense only | weight of the dense rank term; 0.5 ranks exactly like classic unweighted RRF | weight of the distribution-scaled dense score; 0 = BM25 only, 1 = dense only |
| `HYBRID_RRF_K` (60) | ignored | flattens the rank curve: large k lets deep ranks still count, small k rewards the top of each list | ignored |
| Score range | 0..1 | 0..1 (first in both legs = 1.0, first in one leg only = `alpha` or `1 - alpha`), so the reranker's bonuses and penalties keep their meaning | 0..1, so the reranker's bonuses and penalties keep their meaning |

### minmax

Min-max fusion depends on the shape of each leg's score distribution: one very strong hit raises that leg's maximum and squeezes everything below it, and a chunk found by only one leg can reach at most `alpha` while one-leg hits of the other leg compete on the same scale. Rank fusion ignores score magnitudes, so it is stable when the two legs' score scales differ a lot from query to query.

### rrf

Weighted Reciprocal Rank Fusion uses only the rank of a chunk in each leg, not its score, so it is not affected by how the two legs' score scales differ. `HYBRID_ALPHA` weighs the dense rank term against the sparse one (0.5 = classic unweighted RRF) and `HYBRID_RRF_K` (default 60, a number >= 0) controls how fast the weight of deeper ranks falls. The `(k + 1)` factor only rescales, so scores stay in 0..1 for the reranker. The cost is that score gaps are lost: a weak hit ranked third by BM25 alone weighs as much as a strong one.

### dbsf

Distribution-based score fusion (`"dbsf"`) keeps the score gaps within a leg like min-max, but takes its scale from the leg's mean and standard deviation. One outlier clips at the edge of 0..1 instead of setting the minimum or the maximum, so the other hits on that leg stay spread through the middle of the range. It is worth trying when a leg often has a single score far from the others (for example one very large BM25 value) and the chunks just below it should stay distinguishable. An empty leg contributes 0; the other leg is still normalised and weighted, so its scores stay in 0..1.

### Query-adaptive alpha

`HYBRID_ALPHA_MODE` chooses the dense weight per query. It is orthogonal to fusion: `"minmax"`, `"rrf"` and `"dbsf"` each keep the formula in the table above and use the chosen number as `alpha`. The default is `"fixed"`, which uses `HYBRID_ALPHA` for every query and is the behaviour of earlier versions. `"adaptive"` classifies the query with the rules below and looks up a weight. There is no classifier and no model. An unknown mode fails at startup. A dense-only collection ignores the mode. Query-time only: no reindex.

| Class | When | Setting | Default |
|---|---|---|---|
| `identifier` | the query is essentially code names | `HYBRID_ALPHA_IDENT` | `0.3` (more BM25) |
| `mixed` | a sentence that also names a symbol, or a short plain query | `HYBRID_ALPHA_MIXED` | `None`, meaning `HYBRID_ALPHA` |
| `natural` | a descriptive phrase with no code token | `HYBRID_ALPHA_NL` | `None`, meaning `HYBRID_ALPHA` |

Natural-language queries keep `HYBRID_ALPHA` unless you set `HYBRID_ALPHA_NL`. Only identifier-like queries move, and the default move is toward BM25 (0.3 dense / 0.7 sparse). `HYBRID_ALPHA_IDENT` may be `0.3` or any other number in [0, 1]; omitted and `None` both mean 0.3. `HYBRID_ALPHA_MIXED` and `HYBRID_ALPHA_NL` may be `None` or a number in [0, 1]. A boolean, a string, or a number outside that range fails at startup. The three weights are ignored while the mode is `"fixed"`, and a bad value still fails at load.

With `"minmax"` and `"dbsf"`, the chosen alpha is the weight of the scaled dense score (`alpha * dense + (1 - alpha) * sparse`). With `"rrf"`, it is the weight of the dense rank term; 0.5 is still classic RRF, and an identifier query at 0.3 puts more of that term on BM25 rank. `HYBRID_RRF_K` is unchanged.

### Query-shape rules

A token is identifier-like when it matches a shape the reranker and the symbol lookup already treat as code, plus paths and preprocessor directives:

- snake_case, including `SCREAMING_SNAKE` (`do_numa_page`, `SYSCALL_DEFINE`, `PAGE_SIZE`);
- camelCase or PascalCase with an inner capital, including an all-caps prefix (`getUserForJWT`, `HttpClient`, `HTTPServer`, `IDisposable`);
- ALL_CAPS of at least 3 characters (`EINTR`, `NULL`), except a function word (`THE`, `HOW`);
- a qualified name (`Store::flush`, `foo::bar`, `node->next`, `fmt.Println`, `StringBuilder.Append`), using the reranker's rule for dotted names;
- a call (`schedule()`, `a.b()`, `Foo::bar()`);
- a path, glob or dotted file with a known code extension (`include/linux/sched.h`, `*.h`, `sched.h`);
- a backticked name (`` `do_numa_page` ``);
- a PHP variable (`$var`, `$session`);
- a preprocessor directive (`#include`, `#define`, and `#if` / `#ifdef` / `#ifndef` / `#elif` / `#endif` / `#undef` / `#pragma`);
- a keyword form the symbol lookup already accepts (`struct page_pool`, `function main`).

A plain word is a run of letters. Digits and punctuation are not words, so a string of numbers is not a natural-language query. Stop words (English function words such as `the`, `how`, `where`, `is`, plus the symbol-lookup list such as `defined`) still count toward the word total below. They do not count toward the plain-word budget next to a symbol.

- **identifier** — at least one identifier-like token, and at most 3 plain words outside those tokens that are not stop words. A query that is only a path or a symbol (`include/linux/sched.h`, `do_numa_page`, `Store::flush`) has no plain words left, so it is identifier. `where is do_numa_page defined` is identifier because the other words are stop words.
- **natural** — no identifier-like token, and at least 4 words. `how does the scheduler pick the next task` is natural.
- **mixed** — everything else. That includes a descriptive sentence that also names one symbol (`how does the scheduler pick the next task using do_numa_page`), a plain query shorter than 4 words (`page fault`, `what is this`), an empty string, whitespace, numbers and punctuation.

A fully capitalized sentence is identifier when its content words are ALL_CAPS tokens of 3 or more characters. Function words in caps stay stop words.

### Overrides, reports and the MCP server

`validate_rag.py --alpha` replaces `HYBRID_ALPHA`. In fixed mode that value is the alpha for every query. In adaptive mode it is the base used for mixed and natural queries when `HYBRID_ALPHA_MIXED` / `HYBRID_ALPHA_NL` are unset. `HYBRID_ALPHA_IDENT`, and an explicit mixed or natural value, stay as configured. In adaptive mode the JSON report adds `alpha` and `query_shape` on each test. Fixed-mode JSON is unchanged.

The MCP server in fixed mode builds one retriever per request with `HYBRID_ALPHA`, the same kwargs as before. In adaptive mode it builds a retriever for that query's alpha. It does not write alpha onto a retriever another request is using, so concurrent queries can carry different weights. The log line `retriever ready` includes the alpha mode (`fixed` or `adaptive`, and the shape when adaptive).

## Measured results

Measured on the public evaluation suites: 7 small open-source repositories in six languages (124 questions), 7 large ones (382 questions), and a Linux kernel index with 452 questions plus a separate 40-question held-out set. Scores are `(2 * PASS + PARTIAL) / (2 * n)`, pooled over all questions of a group. All runs used `HYBRID_ALPHA = 0.5` and `HYBRID_PREFETCH_K = 100` on CPU. The held-out set was scored only after all settings were fixed; nothing was tuned on it.

### minmax vs rrf

| Suites | `minmax` | `rrf`, k = 60 | `rrf`, k = 20 |
|---|---|---|---|
| small repositories (7 indexes, 124 questions) | 97.2% | 96.8% | 96.8% |
| large repositories (7 indexes, 382 questions) | 80.1% | 78.9% | 80.0% |
| Linux kernel (452 questions) | 57.9% | 58.2% | 59.1% |
| Linux kernel, held-out (40 questions) | 62.5% | 58.8% | 58.8% |

k was chosen on the first three rows; the held-out set was scored only afterwards. Rank fusion helped a few kernel questions whose answer is found only by the dense leg, but the gain did not carry over to the held-out questions, and per repository the differences go both ways (a few points up or down). k = 20 was at least as good as k = 60 almost everywhere, so start with `HYBRID_RRF_K = 20` if you try it. RRF is most worth testing on very large repositories where the two legs' scores are on very different scales. Query latency is the same in both modes (p50 about 60 ms on CPU in these runs; the fusion itself merges a few hundred items).

### dbsf and adaptive alpha

Adaptive alpha used the defaults (`HYBRID_ALPHA_IDENT = 0.3`, mixed and natural = `HYBRID_ALPHA`). "Semantic" is the subset of questions in the categories that describe behaviour in plain language (semantic behaviour, natural-language how/where); "identifier" is the subset that names symbols (precise identifier, method lookup, class overview, types/enums).

| Suites | `minmax` | `dbsf` | `minmax` + adaptive | `dbsf` + adaptive | `rrf` k = 20 + adaptive |
|---|---|---|---|---|---|
| small repositories (124 questions) | 97.2% | 97.6% | 97.2% | 96.4% | 94.8% |
| large repositories (382 questions) | 80.1% | 79.5% | 77.6% | 77.5% | 77.5% |
| Linux kernel (452 questions) | 57.9% | 58.7% | 56.9% | 57.6% | 57.5% |
| Linux kernel, held-out (40 questions) | 62.5% | 61.3% | 62.5% | 62.5% | 60.0% |
| all of the above except held-out (958) | **71.8%** | **72.0%** | 70.4% | 70.6% | 70.3% |
| semantic questions (317) | **67.2%** | 65.8% | 67.0% | 65.6% | 65.9% |
| identifier questions (424) | 82.9% | **83.8%** | 80.8% | 81.4% | 80.5% |

Per query shape (adaptive classification, same 958 questions):

| Shape | n | `minmax` | `minmax` + adaptive |
|---|---|---|---|
| identifier | 310 | 88.5% | 84.0% |
| mixed | 222 | 61.7% | 61.7% |
| natural | 426 | 64.9% | 64.9% |

What this shows:

- **`dbsf`** is about even with `minmax` overall (+0.2) and slightly better on identifier questions, but it lost 7 points on the semantic questions of the large repositories (84.8% -> 77.7%) and 1.3 points on the kernel held-out set. It is not a safe default.
- Query latency was the same for every combination (p50 about 60 ms, p95 about 110 ms on CPU).

> [!WARNING]
> **Adaptive alpha with the default `HYBRID_ALPHA_IDENT = 0.3` hurt identifier queries**: 88.5% -> 84.0% on identifier-shaped queries, and every question it made worse was one classified as identifier. Mixed and natural queries get the same alpha as in fixed mode, so semantic questions stayed level (67.2% -> 67.0%; the one semantic question that dropped had been classified as identifier). Moving identifier queries toward BM25 was the wrong direction on these code bases, probably because the reranker and the exact symbol lookup already handle names. A higher `HYBRID_ALPHA_IDENT` (above `HYBRID_ALPHA`) has not been measured; validate on your own suite before using adaptive mode.

## Which one to use

Keep `"minmax"` and `"fixed"` unless your own validation suite shows a clear gain. `"rrf"` (start with `HYBRID_RRF_K = 20`) is most worth testing on very large repositories whose two legs score on very different scales; `"dbsf"` when one leg often has a single outlier score. Check the natural-language questions of your suite separately before switching. A/B one index without editing its config:

```
python src/validate_rag.py --config <name> --set HYBRID_FUSION=dbsf
python src/validate_rag.py --config <name> --set HYBRID_FUSION=rrf --set HYBRID_RRF_K=20
python src/validate_rag.py --config <name> --set HYBRID_ALPHA_MODE=adaptive --set HYBRID_ALPHA_IDENT=0.3
```

All modes and both alpha modes are query-time only (no reindex). The defaults are exactly the behaviour of earlier versions; an unknown value fails at startup with a clear error.

See also: the parameter table in [configuration.md](configuration.md) and the reranker in [reranker.md](reranker.md).
