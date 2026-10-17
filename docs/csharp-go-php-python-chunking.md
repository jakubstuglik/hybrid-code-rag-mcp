# C#, Go, PHP and Python chunking

The C#, Go and PHP readers, and the rewritten Python reader, produce the same
chunk shapes as the Java and Kotlin readers (see
[kotlin-chunking.md](kotlin-chunking.md)). The reranker therefore treats them
like Java: `class_summary` / `class_overview` are the overview chunks, and
methods, constructors and fields are detail chunks.

All four readers share `src/shared/readers/_structured.py`
(`StructuredReaderBase`). It builds the context prefix, splits oversized
chunks with the same limits as Kotlin (`MAX_CHUNK_CHARS` 24000,
`MAX_SUMMARY_CHARS` 6000), re-prepends the prefix to every split part, groups
runs of three or more trivial methods (six lines or fewer) into
`method_group`, writes the `class_overview` sentence for large types, and
merges runs of per-line `//` comments into one `block_comment`.

Grammars come from `tree-sitter-language-pack` (`python`, `csharp`, `go`,
`php`); no extra dependency is needed.

## Context prefix

| Reader | Prefix lines |
|---|---|
| Python | `# File: orders/service.py`<br>`# Module: shop.orders.service`<br>`# Class: class OrderService(BaseService):` |
| C# | `// File: OrderService.cs`<br>`// Namespace: Shop.Orders`<br>`// Class: public sealed class OrderService : IOrderService` |
| Go | `// File: store.go`<br>`// Package: orders`<br>`// Class: type Store struct` |
| PHP | `// File: OrderController.php`<br>`// Namespace: App\Http\Controllers`<br>`// Class: final class OrderController extends Controller` |

Nested types prefix the `Class:` line with the outer type chain, as in Java.
`package_name` holds the dotted Python module's package, the C# or PHP
namespace, or the Go package. `unit_name` is the file stem.

The Python module path is found by walking up the directories that contain
`__init__.py`.

## Node types

| Construct | Python | C# | Go | PHP |
|---|---|---|---|---|
| Type summary (header, doc, fields, member signatures) | `class` | `class`, `struct`, `interface`, `record`, `record struct`, `enum` | `struct`, `interface` types, plus the signatures of methods declared on them in the same file | `class`, `interface`, `trait`, `enum` |
| `class_overview` | summary over 6000 chars | same | same | same |
| `method_declaration` | `def` (methods and functions) | methods, operators, destructors, local functions | functions, methods | methods, top-level functions |
| `constructor_declaration` | `__init__` | constructors | `func New<Type>(...)` | `__construct` |
| `field_declaration` | runs of class or module assignments | fields, properties (`{ get; set; }`), indexers, events | `var` blocks | properties |
| `constant_declaration` | runs in which every assigned name is uppercase | — | `const` blocks | `const` |
| `type_alias_declaration` | — | delegates | other named types | — |
| `import_group` | `import` / `from` | `using` | `import` | `use` |
| `block_comment` | module docstring | free-standing comments | package doc and free comments | free-standing comments |
| `script_body` | other top-level statements | top-level statements | — | other top-level code |

Doc comments directly above a declaration (`///`, `/** */`, Go `//` runs, the
first paragraph of a Python docstring in summaries) stay with that
declaration and are not emitted as separate `block_comment` chunks.

Extra metadata: `csharp_kind` and `partial` (C#), `receiver_type` (Go),
`php_kind` (PHP), `decorators` (Python), `function_name` on methods.

## Limits and known gaps

* Go: a struct summary lists only the methods declared in the same file.
  Methods in other files of the package are still indexed as
  `method_declaration` chunks with `class_name` set to the receiver type.
* PHP: a file with no declarations whose inline HTML is more than 30% of the
  file is treated as a template and indexed as text. `.blade.php` and
  `.phtml` always use the text reader.
* C# `partial` classes produce one summary per file; each carries
  `partial=True`.
* Changing reader output requires a `--clear` rebuild of indexes that contain
  these file types.

## Rerank profiles

Each of the four readers sets a `RERANK_PROFILE` built with
`java_style_profile()`: its file-stem pattern, its test paths (`test_*.py`,
`conftest.py`, `*_test.go`, `testdata/`, `*Test.php`, `tests/`, `*.Tests/`,
`*Tests.cs`, ...) and the declaration forms the generic rules miss (Python
assignments, PHP `const` / `$property`, Go method receivers as
`Owner.member`, C# properties and `=>` members). See
[reranker.md](reranker.md).
