# Kotlin chunking (`.kt`, `.kts`)

This note describes how the indexer chunks Kotlin sources, how the chunk
headers line up with the existing Delphi and Java readers, and how the reader
was validated.

## Header format across languages

Every chunk produced by the AST-based readers starts with a short comment
block (the *context prefix*) so the chunk identifies itself in both BM25 and
dense retrieval. The method or class text follows the prefix.

| Language | Prefix lines | Example |
|---|---|---|
| Delphi (`pascal_reader.py`) | `// Unit: <unit> (<file>)`, then `// Class: <class header>` when the chunk belongs to a class | `// Unit: Orders (Orders.pas)`<br>`// Class: TOrderService = class(TBaseService)` |
| Java (`java_reader.py`) | `// File: <file>`, then `// Package: <package>` if declared, then `// Class: <class header>` when inside a type | `// File: OrderService.java`<br>`// Package: com.example.orders`<br>`// Class: @Service public class OrderService extends BaseService implements Auditable` |
| Kotlin (`kotlin_reader.py`) | Same as Java | `// File: OrderService.kt`<br>`// Package: com.example.orders`<br>`// Class: @Service class OrderService(private val repo: OrderRepository) : BaseService(), Auditable` |

Shared conventions:

* The `// Class:` line carries the full one-line declaration header,
  including annotations, modifiers, the primary constructor (Kotlin) and the
  supertypes. The header is collapsed to a single line.
* Nested types (Java and Kotlin) prefix the `// Class:` line with the
  outer-class chain joined by ` > `: `// Class: OrderService > companion
  object Factory`, `// Class: Outer > Middle > static class Inner`. An
  unnamed companion object appears as `Outer > companion object`.
  Top-level types are unchanged. The declaration line inside a
  `class_summary` stays the raw header.
* Code outside a class (Delphi routines outside a class, Kotlin top-level
  functions, properties and type aliases) gets the file-level lines only.
* Method signatures are not part of the prefix. They appear as the first
  line of each method chunk and as the member list of the `class_summary`
  chunk, in every language.
* Metadata keys are shared: `unit_name` (file stem), `class_name` and
  `package_name` (Java and Kotlin). The relative `file_path` is stored in
  metadata, not in the prefix text.
* Kotlin uses the Java prefix builder format byte-for-byte, and a test checks
  this. Delphi differs only in using `// Unit: Name (File.pas)` in place of
  the `File` and `Package` lines, because Delphi has no packages.

## Kotlin reader design

The reader is `src/shared/readers/kotlin_reader.py`. It uses the `kotlin`
grammar from `tree_sitter_language_pack`, which is already a dependency, so
no new package is needed. It is registered for `.kt` and `.kts`.

It mirrors the Java reader:

| Kotlin construct | Chunk `node_type` |
|---|---|
| class / interface / object / companion object / enum, data, sealed, value class | `class_summary` (header + member signatures, no bodies); `class_overview` for large types |
| Body-less declaration (`data class Order(val id: Long)`) | `class_summary` with the declaration text |
| Member, top-level and extension functions | `method_declaration` (metadata: `function_name`, plus `receiver_type` for extension functions) |
| Secondary constructor | `constructor_declaration` |
| `init { }` block | `initializer_block` |
| Property (member or top-level) | `field_declaration` |
| Enum entries | in the enum's summary (`enum_constant` only when no summary exists) |
| `typealias` | `type_alias_declaration` |
| Imports | one `import_group` |
| Comments of 40 characters or more outside summarised classes | `block_comment` |
| Three or more consecutive trivial functions (6 lines or fewer) | `method_group` |
| `.kts` top-level statements (e.g. `plugins { }`, `dependencies { }`) | `script_body` |
| Nothing recognised | `full_file` |

Notes:

* The node type names match the Java and Groovy ones, so the reranker
  handles Kotlin chunks without any change to its overview/detail logic. The
  only reranker change is that `Foo.kt` / `Foo.kts` in a query now counts as
  a target identifier, as `Foo.java` already does.
* Class summaries carry `kotlin_kind` (`class`, `data class`,
  `sealed class`, `enum class`, `interface`, `object`,
  `companion object`, ...). Nested types also carry `outer_class`.
* Oversized chunks are split with the same `TokenTextSplitter` settings as
  Java. Unlike Java, every split part of any Kotlin chunk keeps the prefix,
  not just class summaries.
* Grammar gaps: tree-sitter-kotlin wraps some valid constructs in `ERROR`
  nodes, such as abstract interface members and enum-class members after
  `;`. The reader descends into `ERROR` nodes inside class bodies, so those
  members are still found. Comments that the grammar attaches to the
  package or import headers are recovered as standalone comments. A `where`
  clause that starts on a new line is handled as described under "Fix:
  `where` clauses on a new line" below.

## Change to existing Java chunks (reindex required)

Java chunks belonging to **nested** types (static nested, inner, nested
enum/interface/record classes, at any depth) now carry the outer-class chain
in their `// Class:` line, e.g.

    before: // Class: public static class Line
    after:  // Class: OrderService > public static class Line

Chunks of top-level Java classes are byte-identical to before. Because chunk
text feeds both BM25 and the embeddings, **existing Java indexes must be
rebuilt** to pick up the new headers. Delphi chunks are unchanged.

## Known limitations

* A `where` clause on a new line directly after a `//` comment (for example
  `fun <T> f(): T // note` followed by `where T : A`) is not rejoined and is
  still mis-parsed. This form is rare.

## Fix: `where` clauses on a new line

**Problem.** tree-sitter-kotlin ends a declaration at a line break that comes
right before `where`, so in

    fun <T> pick(a: T, b: T): T
        where T : Comparable<T>,
              T : Cloneable {
        ...
    }

the function ended at `: T` and the `where` line was parsed as a bogus
property. The function chunk and its class-summary line lost the `where`
clause and the whole body, a `field_declaration` chunk starting with `where`
was emitted, and the members after it lost their class. Class and interface
headers with `where` on a new line had the same problem. A `where` clause on
the same line as the signature, or a line break *after* `where`, was always
parsed correctly.

**Fix.** `_join_where_clauses()` parses a copy of the file in which the line
break before `where` is moved after the keyword
(`T\n    where T : A` becomes `T where\n    T : A`). The copy has the same
length and the same line breaks, so byte offsets and line numbers of every
declaration and body are unchanged. Chunk text and headers are still taken
from the original file. As a result:

* function signatures in method chunks and class summaries, and the
  `// Class:` line of classes and interfaces, keep the full `where` clause
  (multi-line, several constraints, collapsed to one line in headers);
* this works for member, top-level and extension functions, block bodies,
  expression bodies (`= ...`) and body-less interface functions;
* method chunk boundaries and bodies are the same as for functions without
  `where`, and the header format (`File`, `Package`, `Class`) is unchanged.

Tests: `TestWhereClause` and `TestJoinWhereClauses` in
`test_kotlin_reader.py` (17 tests). On ep-komputerpokladowy (1,381 Kotlin
files) there are only 2 `where` clauses, both on the same line as the class
header, and the reader output for all files is identical before and after
the fix, so that index does not need a rebuild.

## Validation

New tests are in `src_test/shared/readers/test_kotlin_reader.py`:

* Registry wiring for `.kt` and `.kts`, with existing readers unchanged.
* The prefix builder gives the same output as Java's for every combination
  of arguments.
* A sample file covering classes, annotated multi-line headers, secondary
  constructors, `init` blocks, properties, named and unnamed companion
  objects, inner classes, data, sealed and enum classes, interfaces with
  abstract members, objects, type aliases, extension functions, generic
  reified extensions and `suspend` functions.
* Trivial-method grouping, oversized splitting with the prefix kept,
  `class_overview` for large classes, and comment filtering.
* `.kts` script bodies, empty and missing files, `full_file` fallback, and
  files with no package.
* `test_nested_class_headers.py`: nested, multi-level, inner, named and
  unnamed companion objects (Kotlin), static nested, inner, nested
  enum and interface (Java), trivial-method groups inside nested classes,
  and an identical chain format between Java and Kotlin.
* A header-consistency suite that runs the Delphi, Java and Kotlin readers
  on equivalent sources and checks that:
  * every chunk starts with a header;
  * class-member chunks end their header with a `Class` line;
  * Java and Kotlin have the identical label sequence
    `File, Package, Class`;
  * Delphi has `Unit, Class`;
  * the `Class` line carries the inheritance in all three;
  * all three share `unit_name` metadata.
* Reranker target extraction for `.kt` and `.kts` file names.

Results: test_kotlin_reader.py and test_nested_class_headers.py 76/76 passed. Full suite 2322 passed, 128 skipped (previous baseline 2246 passed, 128 skipped; the difference is the 76 new tests).

After the `where` fix: Kotlin reader tests 85/85 passed (`test_kotlin_reader.py` and
`test_kotlin_reader_coverage.py`). Full suite 2355 passed, 128 skipped (previous 2338
passed, 128 skipped; the difference is the 17 new tests). `pytest tests`: 54 passed.
