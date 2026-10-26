"""
C and C++ file reader (.c, .h, .cpp) using Tree-sitter.

Chunking strategy:

1. Context prefix on every chunk: file name, namespace, and owning class.
2. Class summary: header plus member signatures, with no method bodies.
   Q_OBJECT, signals, and slots stay in the summary.
3. Class overview: a short natural-language summary when the class summary
   is longer than MAX_SUMMARY_CHARS.
4. One chunk per function body (inline or Class::method). Trivial bodies
   are grouped. A signature split across preprocessor branches keeps every
   branch and the body in that one chunk.
5. CVS ``$Log:`` comment blocks are left out of every chunk.
6. Includes are one include_group. Free prototypes are one declaration_group.

.h and .cpp are parsed as C++. .c is parsed as C.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

from llama_index.core import Document
from llama_index.core.node_parser import TokenTextSplitter
from tree_sitter import Node
from tree_sitter_language_pack import get_parser

from shared.log import log_warn
from shared.readers._base import (
    BaseFileReader,
    get_file_datetime,
    read_file_with_encoding_and_bytes,
)
from shared.rerank_profile import RerankProfile, compile_all
from shared.symbol_policy import SymbolMatcher, apply_symbol_policy, get_symbol_policy

_CPP_PARSER = get_parser("cpp")
_C_PARSER = get_parser("c")

_TYPE_SPECIFIERS = {"class_specifier", "struct_specifier", "union_specifier"}
_RECURSE_TYPES = {
    "translation_unit",
    "preproc_ifdef",
    "preproc_ifndef",
    "preproc_if",
    "preproc_else",
    "preproc_elif",
    "preproc_elifdef",
    "preproc_elifndef",
    "linkage_specification",
    "declaration_list",
    "template_declaration",
    "type_definition",
    "ERROR",
}
_NAME_TYPES = {
    "identifier",
    "field_identifier",
    "destructor_name",
    "operator_name",
    "type_identifier",
    "namespace_identifier",
    "template_function",
    "template_type",
}
_SCOPE_TYPES = {
    "namespace_identifier",
    "type_identifier",
    "template_type",
    "qualified_identifier",
}
_QT_PAREN_MACROS = (
    "Q_PROPERTY",
    "Q_ENUM",
    "Q_ENUMS",
    "Q_FLAGS",
    "Q_INTERFACES",
    "Q_CLASSINFO",
    "Q_DECLARE_METATYPE",
    "Q_DISABLE_COPY",
)


def _node_text(node: Node, content_bytes: bytes) -> str:
    """Return the source text of a node."""
    return content_bytes[node.start_byte : node.end_byte].decode(
        "utf-8", errors="replace"
    )


def _collapse(text: str) -> str:
    """Collapse whitespace to a single line."""
    return " ".join(text.split())


def _span_node(node: Node) -> Node:
    """Include a surrounding template_declaration in the chunk span."""
    parent = node.parent
    if parent is not None and parent.type == "template_declaration":
        return parent
    return node


def _blank_paren_macro(text: str, name: str) -> str:
    """Replace ``NAME(...)`` with spaces of the same length. Newlines stay."""
    needle = name
    start = 0
    while True:
        idx = text.find(needle, start)
        if idx == -1:
            return text
        after = idx + len(needle)
        if idx > 0 and (text[idx - 1].isalnum() or text[idx - 1] == "_"):
            start = after
            continue
        j = after
        while j < len(text) and text[j] in " \t":
            j += 1
        if j >= len(text) or text[j] != "(":
            start = after
            continue
        depth = 0
        k = j
        while k < len(text):
            ch = text[k]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    k += 1
                    text = text[:idx] + (" " * (k - idx)) + text[k:]
                    start = idx + (k - idx)
                    break
            k += 1
        else:
            return text


def _normalize_qt(text: str) -> str:
    """Rewrite Qt keywords so the C++ grammar can see the declarations.

    Replacements keep the same length and do not add or remove newlines,
    so tree-sitter line and byte positions still match the original text.
    """
    for name in _QT_PAREN_MACROS:
        text = _blank_paren_macro(text, name)

    def _access_slots(match: re.Match[str]) -> str:
        return (match.group(1) + ":").ljust(len(match.group(0)))

    text = re.sub(
        r"\b(public|protected|private)[ \t]+slots[ \t]*:",
        _access_slots,
        text,
    )
    text = re.sub(
        r"\bQ_SLOTS[ \t]*:",
        lambda m: "public:".ljust(len(m.group(0))),
        text,
    )
    text = re.sub(
        r"\bQ_SIGNALS[ \t]*:",
        lambda m: "public:".ljust(len(m.group(0))),
        text,
    )
    text = re.sub(
        r"\bsignals[ \t]*:",
        lambda m: "public:".ljust(len(m.group(0))),
        text,
    )
    text = re.sub(r"\bQ_OBJECT\b", lambda m: " " * len(m.group(0)), text)
    return text


# A line holding only an attribute-like annotation macro between a function's
# parameter list and its body, e.g. lock-context annotations:
#     static void f(struct x *p)
#         __releases(&p->lock)
#     {
_ANNOTATION_LINE = re.compile(
    r"(?m)(\)[ \t]*(?:/\*[^\n]*?\*/)?[ \t]*\n)"
    r"((?:[ \t]*(?:__[A-Za-z]\w*|[A-Z][A-Z0-9_]{2,})[ \t]*\((?:[^()\n]|\([^()\n]*\))*\)"
    r"[ \t]*(?:/\*[^\n]*?\*/)?[ \t]*\n)+)(?=[ \t]*\{)"
)


def _blank_annotation_lines(text: str) -> str:
    """Blank annotation-macro lines between ``)`` and ``{`` (same length,
    newlines kept) so the grammar sees a plain function definition."""

    def _repl(match: re.Match[str]) -> str:
        return match.group(1) + re.sub(r"[^\n]", " ", match.group(2))

    return _ANNOTATION_LINE.sub(_repl, text)


# Attribute-like macros between the return type and the name of a function
# (``asmlinkage __visible void __softirq_entry __do_softirq(void)``,
# ``static void noinline __cold f(void)``).  The grammar takes the first
# unknown word as the type and gives up on the rest, which loses the name
# or splits the header from the body.  Used only when the plain parse has
# errors.
_ATTR_WORDS = frozenset(
    "asmlinkage noinline notrace noinstr __always_inline __visible __cold __hot "
    "__init __exit __ref __sched __weak __noreturn __must_check __latent_entropy "
    "__attribute_const__ __pure __malloc __cpuidle __kprobes __used __maybe_unused "
    "__flatten __meminit __meminitdata __softirq_entry __irq_entry __naked "
    "__noinline __no_kcsan __no_sanitize_address __nocfi __nocfi_generic "
    "__init_or_module __head __iomem_init __section_init".split()
)
# ``__u32`` / ``__le16`` / ``__be64`` / ``__poll_t`` / ``__wsum`` are types.
_ATTR_TYPE_LIKE = re.compile(r"^__(?:[us]\d+|[lb]e\d+|\w+_t|wsum|sum\d*|int\d+|uint\d+)$")
_HEADER_START = re.compile(rb"(?m)^(?=[A-Za-z_])([^\n;{}()#=]*?)\b([A-Za-z_]\w*)[ \t]*\(")
_PRIMITIVE_OR_TYPE = re.compile(
    r"\b(?:void|char|short|int|long|float|double|bool|_Bool|unsigned|signed|"
    r"size_t|ssize_t|struct|union|enum|[a-z]\w*_t|u8|u16|u32|u64|s8|s16|s32|s64)\b"
)


def _is_attr_word(word: str) -> bool:
    if word in _ATTR_WORDS:
        return True
    return word.startswith("__") and not word.startswith("__attribute") and not _ATTR_TYPE_LIKE.match(word) and word not in (
        "__inline", "__inline__", "__forceinline", "__restrict", "__restrict__", "__extension__",
        "__cdecl", "__stdcall", "__fastcall", "__thiscall", "__vectorcall", "__declspec",
        "__thread", "__const", "__volatile__", "__signed__", "__asm__", "__asm", "__user",
        "__iomem", "__percpu", "__rcu", "__force", "__bitwise", "__nocast",
    )


def _blank_header_attributes(data: bytes) -> bytes:
    """Blank attribute-like words in column-0 function headers (same length,
    newlines kept).  A word is only blanked when the header still has a type
    without it and the word is not the function name."""
    out = bytearray(data)
    for m in _HEADER_START.finditer(data):
        prefix = m.group(1).decode("utf-8", errors="replace")
        if not prefix.strip():
            continue
        words = list(re.finditer(r"[A-Za-z_]\w*", prefix))
        attrs = [w for w in words if _is_attr_word(w.group(0))]
        if not attrs:
            continue
        rest = prefix
        for w in reversed(attrs):
            rest = rest[: w.start()] + " " * (w.end() - w.start()) + rest[w.end() :]
        others = [w for w in re.finditer(r"[A-Za-z_]\w*", rest) if w.group(0) not in ("static", "extern", "inline", "const", "volatile")]
        if not others and not _PRIMITIVE_OR_TYPE.search(rest):
            continue
        base = m.start(1)
        for w in attrs:
            # prefix is ASCII in practice; skip when byte offsets would differ
            a = base + len(prefix[: w.start()].encode("utf-8"))
            b = a + len(w.group(0).encode("utf-8"))
            if data[a:b].decode("utf-8", errors="replace") != w.group(0):
                continue
            out[a:b] = b" " * (b - a)
    return bytes(out)


def _error_bytes(tree) -> int:
    """Bytes covered by ERROR / missing nodes (outermost only)."""
    total = 0
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type == "ERROR" or node.is_missing:
            total += max(node.end_byte - node.start_byte, 1)
            continue
        if node.has_error:
            stack.extend(node.children)
    return total


_DEFINITION_TYPES = {
    "function_definition",
    "struct_specifier",
    "union_specifier",
    "class_specifier",
    "enum_specifier",
    "preproc_def",
    "preproc_function_def",
}


def _definition_count(tree) -> int:
    """Definitions the walker can turn into chunks (bodies only)."""
    count = 0
    stack = [tree.root_node]
    while stack:
        node = stack.pop()
        if node.type in _DEFINITION_TYPES:
            if node.type in ("function_definition", "preproc_def", "preproc_function_def") or any(
                c.type in ("field_declaration_list", "enumerator_list") for c in node.children
            ):
                count += 1
        stack.extend(node.children)
    return count


def _parse_best(primary, secondary, data: bytes):
    """Parse with ``primary``; when the tree has errors and a ``secondary``
    grammar is given (``.h`` files are C or C++), also try it and keep the
    tree with more recognisable definitions (ties: fewer error bytes)."""
    tree = primary.parse(data)
    if not tree.root_node.has_error or secondary is None:
        return tree, primary
    alt = secondary.parse(data)
    a, b = _definition_count(alt), _definition_count(tree)
    if a > b or (a == b and _error_bytes(alt) < _error_bytes(tree)):
        return alt, secondary
    return tree, primary


def _strip_log_comments(text: str) -> str:
    """Remove block comments that carry a CVS ``$Log:`` history."""

    def _repl(match: re.Match[str]) -> str:
        if "$Log:" in match.group(0):
            return ""
        return match.group(0)

    return re.sub(r"/\*.*?\*/", _repl, text, flags=re.DOTALL)


def _is_log_comment(node: Node, content_bytes: bytes) -> bool:
    if node.type != "comment":
        return False
    return "$Log:" in _node_text(node, content_bytes)


def _has_field_body(node: Node) -> bool:
    return any(child.type == "field_declaration_list" for child in node.children)


def _find_first(node: Node, types: set[str]) -> Optional[Node]:
    """Depth-first search for the first descendant whose type is in ``types``."""
    if node.type in types:
        return node
    for child in node.children:
        found = _find_first(child, types)
        if found is not None:
            return found
    return None


def _type_name(node: Node, content_bytes: bytes) -> Optional[str]:
    for child in node.children:
        if child.type in ("type_identifier", "identifier", "template_type"):
            return _node_text(child, content_bytes).strip()
    return None


def _type_kind(node: Node, content_bytes: bytes) -> str:
    for child in node.children:
        if child.type in ("class", "struct", "union"):
            return child.type
        text = _node_text(child, content_bytes).strip()
        if text in ("class", "struct", "union"):
            return text
    if node.type == "struct_specifier":
        return "struct"
    if node.type == "union_specifier":
        return "union"
    return "class"


def _base_classes(node: Node, content_bytes: bytes) -> List[str]:
    bases: List[str] = []
    for child in node.children:
        if child.type != "base_class_clause":
            continue
        for sub in child.children:
            if sub.type in (
                "type_identifier",
                "qualified_identifier",
                "template_type",
            ):
                bases.append(_collapse(_node_text(sub, content_bytes)))
    return bases


def _class_header(node: Node, content_bytes: bytes) -> str:
    span = _span_node(node)
    end = span.end_byte
    for child in node.children:
        if child.type == "field_declaration_list":
            end = child.start_byte
            break
    header = content_bytes[span.start_byte : end].decode("utf-8", errors="replace")
    return _collapse(header)


def _split_qualified(node: Node, content_bytes: bytes) -> tuple[Optional[str], str]:
    """Return ``(scope, name)`` from a qualified_identifier or plain name."""
    if node.type == "qualified_identifier":
        scope: Optional[str] = None
        name = ""
        for child in node.children:
            if child.type in _SCOPE_TYPES:
                scope = _collapse(_node_text(child, content_bytes))
            elif child.type in _NAME_TYPES:
                name = _collapse(_node_text(child, content_bytes))
        if not name:
            name = _collapse(_node_text(node, content_bytes))
        return scope, name
    if node.type in _NAME_TYPES:
        return None, _collapse(_node_text(node, content_bytes))
    for child in node.children:
        if child.type in ("qualified_identifier",) or child.type in _NAME_TYPES:
            return _split_qualified(child, content_bytes)
        if child.type in (
            "pointer_declarator",
            "reference_declarator",
            "parenthesized_declarator",
            "abstract_pointer_declarator",
            "function_declarator",
        ):
            return _split_qualified(child, content_bytes)
    return None, ""


def _function_declarator(node: Node) -> Optional[Node]:
    return _find_first(node, {"function_declarator"})


def _signature(node: Node, content_bytes: bytes) -> str:
    end = node.end_byte
    body = _find_first(node, {"compound_statement"})
    if body is not None:
        end = body.start_byte
    text = content_bytes[node.start_byte : end].decode("utf-8", errors="replace")
    return _collapse(text).rstrip(";").strip()


def _namespace_name(node: Node, content_bytes: bytes) -> Optional[str]:
    parts: List[str] = []
    for child in node.children:
        if child.type in (
            "namespace_identifier",
            "identifier",
            "nested_namespace_specifier",
        ):
            parts.append(_node_text(child, content_bytes).strip())
    if not parts:
        return None
    return "::".join(parts)


def _access_label(lines: List[str], node: Node) -> Optional[str]:
    """Read public/slots/signals from the original line. The parser saw a rewrite."""
    if node.start_point[0] >= len(lines):
        return None
    line = lines[node.start_point[0]]
    has_slots = re.search(r"\bslots\b|\bQ_SLOTS\b", line) is not None
    has_signals = re.search(r"\bsignals\b|\bQ_SIGNALS\b", line) is not None
    access_match = re.search(r"\b(public|protected|private)\b", line)
    access = access_match.group(1) if access_match else None
    if has_signals:
        return "signals"
    if has_slots and access:
        return f"{access} slots"
    if has_slots:
        return "slots"
    if access:
        return access
    return None


def _context_prefix(
    file_name: str,
    namespace: tuple[str, ...],
    class_header: Optional[str] = None,
    class_name: Optional[str] = None,
) -> str:
    parts = [f"// File: {file_name}"]
    shown = [part for part in namespace if part and part != "(anonymous)"]
    if shown:
        parts.append("// Namespace: " + "::".join(shown))
    if class_header:
        parts.append(f"// Class: {class_header}")
    elif class_name:
        parts.append(f"// Class: {class_name}")
    return "\n".join(parts)


def _is_include_guard(node: Node, content_bytes: bytes) -> bool:
    if node.type != "preproc_def":
        return False
    for child in node.children:
        if child.type == "preproc_arg" and _node_text(child, content_bytes).strip():
            return False
    return True


# Linux system call definitions: ``SYSCALL_DEFINE3(read, ...)`` defines
# ``sys_read``; ``COMPAT_SYSCALL_DEFINE`` defines ``compat_sys_<name>``.
_SYSCALL_ALIAS = (
    (re.compile(r"^COMPAT_SYSCALL_DEFINE\d*$"), "compat_sys_"),
    (re.compile(r"^SYSCALL_DEFINE\d*$"), "sys_"),
)


def _macro_aliases(macro: str, name: str) -> List[str]:
    """Extra symbol names a function-defining macro creates."""
    for pattern, prefix in _SYSCALL_ALIAS:
        if pattern.match(macro or ""):
            return [prefix + name]
    return []


# A function whose signature is wrapped in preprocessor branches parses as a
# conditional of declarations (the semicolon is missing) plus a compound
# statement that is no longer attached to the declarator.  The body used to
# be dropped.  These helpers recognise that shape and only that shape.
_PREPROC_OPEN = {"preproc_ifdef", "preproc_ifndef", "preproc_if"}
_ALT_TYPES = {"preproc_else", "preproc_elif", "preproc_elifdef", "preproc_elifndef"}
_DIRECTIVE_TYPES = {
    "#ifdef",
    "#ifndef",
    "#if",
    "#else",
    "#elif",
    "#elifdef",
    "#elifndef",
    "#endif",
}
_CONTENT_START = {
    "declaration",
    "field_declaration",
    "function_definition",
    "comment",
    "ERROR",
    "compound_statement",
    "preproc_include",
    "preproc_def",
    "preproc_function_def",
    "preproc_ifdef",
    "preproc_ifndef",
    "preproc_if",
    "class_specifier",
    "struct_specifier",
    "union_specifier",
    "enum_specifier",
    "expression_statement",
    "template_declaration",
    "namespace_definition",
    "linkage_specification",
    "using_declaration",
    "alias_declaration",
    "type_definition",
    "declaration_list",
}
_TYPE_WORDS = {
    "const",
    "volatile",
    "mutable",
    "static",
    "extern",
    "inline",
    "virtual",
    "explicit",
    "constexpr",
    "unsigned",
    "signed",
    "long",
    "short",
    "int",
    "char",
    "bool",
    "void",
    "float",
    "double",
    "auto",
    "wchar_t",
    "char16_t",
    "char32_t",
    "char8_t",
    "size_t",
    "std",
}
_PREPROC_DIRECTIVE = re.compile(
    r"#[ \t]*(?:if|ifdef|ifndef|else|elif|elifdef|elifndef|endif|define|undef|pragma|include)\b[^\n]*"
)
_CV_TRAILER = re.compile(
    r"(?:const|volatile|override|final|noexcept|mutable|&|&&|\*)"
    r"(?:\s+(?:const|volatile|override|final|noexcept|mutable|&|&&|\*))*"
)


def _header_end(node: Node) -> int:
    """Index of the first child that is conditional content, not the directive."""
    children = node.children
    if not children:
        return 0
    index = 1 if str(children[0].type).startswith("#") else 0
    if node.type in ("preproc_ifdef", "preproc_ifndef"):
        if index < len(children) and children[index].type == "identifier":
            index += 1
        return index
    if node.type == "preproc_else":
        return index
    while index < len(children):
        child = children[index]
        if child.type == "\n":
            return index + 1
        if child.type in _CONTENT_START or child.type in _ALT_TYPES:
            return index
        index += 1
    return index


def _content_branches(node: Node) -> List[List[Node]]:
    """Content nodes of each ``#if`` / ``#else`` / ``#elif`` alternative."""
    branches: List[List[Node]] = []
    current: List[Node] = []
    for child in node.children[_header_end(node) :]:
        if child.type in _ALT_TYPES:
            branches.append(current)
            current = []
            branches.extend(_content_branches(child))
            continue
        if child.type in _DIRECTIVE_TYPES or child.type == "\n":
            continue
        if not child.is_named and child.type != "ERROR":
            continue
        current.append(child)
    branches.append(current)
    return branches


def _real_endif(node: Node) -> Optional[Node]:
    """A real ``#endif`` token, not the empty one the grammar inserts."""
    for child in node.children:
        if child.type == "#endif" and not child.is_missing and child.end_byte > child.start_byte:
            return child
        if child.type in _ALT_TYPES:
            found = _real_endif(child)
            if found is not None:
                return found
    return None


def _real_semi(node: Node) -> bool:
    for child in node.children:
        if child.type == ";" and not child.is_missing and child.end_byte > child.start_byte:
            return True
    return False


def _direct_body(node: Node) -> Optional[Node]:
    if node.type == "function_definition":
        body = node.child_by_field_name("body")
        if body is not None and body.type == "compound_statement":
            return body
    for child in node.children:
        if child.type == "compound_statement":
            return child
    return None


def _bare_signature_error(node: Node) -> bool:
    """An ``ERROR`` that is only a function declarator with no body and no ``;``.

    A constructor (no return type) split by ``#if`` is parsed this way: each
    branch is an ``ERROR`` around a ``function_declarator``, and the ``{ }``
    follows the conditional.
    """
    if node.type != "ERROR":
        return False
    if _direct_body(node) is not None or _real_semi(node):
        return False
    if _function_declarator(node) is None:
        return False
    blocked = {
        "class_specifier",
        "struct_specifier",
        "union_specifier",
        "enum_specifier",
        "preproc_include",
        "preproc_def",
        "preproc_ifdef",
        "preproc_if",
        "preproc_ifndef",
        "preproc_else",
        "preproc_elif",
        "namespace_definition",
        "compound_statement",
    }
    return _find_first(node, blocked) is None


def _functionish(node: Node) -> bool:
    """True when ``node`` declares a function, including ``name()`` read as a call."""
    target = node
    if node.type == "template_declaration" and node.named_children:
        target = node.named_children[-1]
    if _bare_signature_error(target) or target.type == "function_declarator":
        return True
    if target.type not in ("declaration", "field_declaration", "function_definition"):
        return False
    if _function_declarator(target) is not None:
        return True
    for child in target.children:
        if child.type != "init_declarator":
            continue
        kinds = [item.type for item in child.children]
        if "argument_list" in kinds and "=" not in kinds and "initializer_list" not in kinds:
            return True
    return False


def _is_open_signature_decl(node: Node, owner: Node) -> bool:
    """A function declarator that does not yet have its body inside a closed ``#if``."""
    if not _functionish(node) or _real_semi(node):
        return False
    body = _direct_body(node)
    if body is None:
        return True
    endif = _real_endif(owner)
    if endif is not None and body.end_byte <= endif.start_byte:
        return False
    return True


def _is_directive_error(node: Node, content_bytes: bytes) -> bool:
    if node.type != "ERROR":
        return False
    return _node_text(node, content_bytes).strip().startswith("#")


def _branch_role(
    nodes: List[Node],
    content_bytes: bytes,
    owner: Node,
    ignore_after: Optional[int],
) -> str:
    saw = False
    for child in nodes:
        if ignore_after is not None and child.start_byte >= ignore_after:
            continue
        if child.type == "comment" or _is_directive_error(child, content_bytes):
            continue
        if child.type in _PREPROC_OPEN and _is_signature_header(child, content_bytes, None):
            saw = True
            continue
        if _is_open_signature_decl(child, owner):
            saw = True
            continue
        return "other"
    return "sig" if saw else "empty"


def _is_signature_header(node: Node, content_bytes: bytes, ignore_after: Optional[int]) -> bool:
    """Every branch is an unfinished function signature, a nested one, or empty."""
    if node.type not in _PREPROC_OPEN:
        return False
    saw = False
    for branch in _content_branches(node):
        role = _branch_role(branch, content_bytes, node, ignore_after)
        if role == "other":
            return False
        if role == "sig":
            saw = True
    return saw


def _collect_signature_decls(node: Node, owner: Node, ignore_after: Optional[int]) -> List[Node]:
    found: List[Node] = []
    if node.type not in _PREPROC_OPEN and node.type not in _ALT_TYPES:
        return found
    for branch in _content_branches(node):
        for child in branch:
            if ignore_after is not None and child.start_byte >= ignore_after:
                continue
            if child.type in _PREPROC_OPEN or child.type in _ALT_TYPES:
                found.extend(_collect_signature_decls(child, owner, ignore_after))
            elif _is_open_signature_decl(child, owner):
                found.append(child)
    return found


def _decl_name(node: Node, content_bytes: bytes) -> tuple[Optional[str], str]:
    target = node
    if node.type == "template_declaration" and node.named_children:
        target = node.named_children[-1]
    declarator = _function_declarator(target)
    if declarator is not None:
        return _split_qualified(declarator, content_bytes)
    for child in target.children:
        if child.type != "init_declarator":
            continue
        qualified = _find_first(child, {"qualified_identifier"})
        if qualified is not None:
            return _split_qualified(qualified, content_bytes)
        for sub in child.children:
            if sub.type in _NAME_TYPES:
                return None, _collapse(_node_text(sub, content_bytes))
            if sub.type == "argument_list":
                break
    return None, ""


def _is_type_fragment(text: str) -> bool:
    """A return type standing alone between preprocessor branches."""
    if any(char in text for char in "();{}="):
        return False
    parts = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text)
    if not parts:
        return False
    for part in parts:
        if part in _TYPE_WORDS or part.endswith("_t") or part[:1].isupper():
            continue
        return False
    return True


def _is_type_only_header(node: Node, content_bytes: bytes) -> bool:
    if node.type not in _PREPROC_OPEN or _collect_signature_decls(node, node, None):
        return False
    saw = False
    for branch in _content_branches(node):
        for child in branch:
            if child.type == "comment" or _is_directive_error(child, content_bytes):
                continue
            if child.type in _PREPROC_OPEN or child.type in _ALT_TYPES:
                return False
            text = _node_text(child, content_bytes).strip()
            if not text:
                continue
            if not _is_type_fragment(text):
                return False
            saw = True
    return saw


def _summary_signature(node: Node, content_bytes: bytes) -> str:
    end = node.end_byte
    body = _direct_body(node)
    if body is not None:
        end = body.start_byte
    raw = content_bytes[node.start_byte : end].decode("utf-8", errors="replace")
    raw = _PREPROC_DIRECTIVE.sub(" ", raw)
    return _collapse(raw).strip().rstrip(";").strip()


def _swallowed_body(preproc: Node) -> Optional[Node]:
    """Body parsed inside the conditional because ``#endif`` was not a real token."""
    endif = _real_endif(preproc)
    best: Optional[Node] = None
    stack: List[Node] = list(preproc.children)
    while stack:
        current = stack.pop()
        if current.type == "compound_statement":
            if endif is not None and current.end_byte <= endif.start_byte:
                continue
            if best is None or current.start_byte < best.start_byte:
                best = current
            continue
        stack.extend(current.children)
    return best


def _gap_is_signature_body(content: bytes, start: int, end: int) -> bool:
    if end < start:
        return False
    gap = content[start:end].decode("utf-8", errors="replace")
    if gap.count("\n") > 3:
        return False
    gap = re.sub(r"/\*.*?\*/", "", gap, flags=re.S)
    gap = re.sub(r"//[^\n]*", "", gap)
    gap = re.sub(r"\b(?:const|volatile|override|final|noexcept|mutable)\b", "", gap)
    gap = gap.replace("&", "").replace("*", "")
    return gap.strip() == ""


def _is_cv_trailer(node: Node, content_bytes: bytes) -> bool:
    if node.type == "compound_statement":
        return False
    text = _collapse(_node_text(node, content_bytes))
    return _CV_TRAILER.fullmatch(text) is not None


def _take_sibling_body(
    preproc: Node, following: List[Node], content_bytes: bytes
) -> tuple[Optional[Node], int]:
    consumed = 0
    for sib in following:
        blank = not sib.is_named and not _node_text(sib, content_bytes).strip()
        if sib.type in ("comment", "\n") or blank:
            consumed += 1
            continue
        if _is_cv_trailer(sib, content_bytes):
            consumed += 1
            continue
        if sib.type == "compound_statement" and sib.start_byte >= preproc.end_byte:
            if _gap_is_signature_body(content_bytes, preproc.end_byte, sib.start_byte):
                return sib, consumed + 1
        return None, 0
    return None, 0


def _take_following_function(
    preproc: Node, following: List[Node], content_bytes: bytes
) -> tuple[Optional[Node], int]:
    consumed = 0
    for sib in following:
        blank = not sib.is_named and not _node_text(sib, content_bytes).strip()
        if sib.type in ("comment", "\n") or blank:
            consumed += 1
            continue
        if sib.type != "function_definition" or sib.start_byte < preproc.end_byte:
            return None, 0
        gap = content_bytes[preproc.end_byte : sib.start_byte]
        if gap.strip() or gap.count(b"\n") > 1:
            return None, 0
        return sib, consumed + 1
    return None, 0


def _top_nodes_after(node: Node, pos: int) -> List[Node]:
    """Highest descendants that start at or after ``pos``."""
    found: List[Node] = []

    def walk(current: Node) -> None:
        if current.end_byte <= pos:
            return
        if current.start_byte >= pos and current.end_byte > current.start_byte:
            found.append(current)
            return
        for child in current.children:
            walk(child)

    for child in node.children:
        walk(child)
    found.sort(key=lambda item: item.start_byte)
    return found


class CppFileReader(BaseFileReader):
    """Semantic chunking for C and C++ source files."""

    MIN_CHUNK_SIZE = 20
    MAX_CHUNK_CHARS = 24000
    MAX_SUMMARY_CHARS = 6000
    TRIVIAL_METHOD_LINES = 6
    MIN_TRIVIAL_RUN = 3
    MAX_GROUP_CHARS = 8000
    LONG_MACRO_LINES = 8

    def __init__(self) -> None:
        super().__init__()
        self._text_splitter = TokenTextSplitter(chunk_size=1024, chunk_overlap=128)

    def load_data(
        self, file: Path, extra_info: Optional[dict] = None
    ) -> List[Document]:
        try:
            text, _ = read_file_with_encoding_and_bytes(file)
        except Exception as exc:
            log_warn(f"Failed to read {file}: {exc}")
            return []

        if not text.strip():
            return []

        normalized = _normalize_qt(text)
        if len(normalized) != len(text):
            normalized = text
        annotated = _blank_annotation_lines(normalized)
        if len(annotated) == len(normalized):
            normalized = annotated
        content_bytes = text.encode("utf-8")
        parse_bytes = normalized.encode("utf-8")
        if len(parse_bytes) != len(content_bytes):
            parse_bytes = content_bytes

        suffix = file.suffix.lower()
        parser = _C_PARSER if suffix == ".c" else _CPP_PARSER
        other = _C_PARSER if suffix == ".h" else None
        try:
            tree, used = _parse_best(parser, other, parse_bytes)
            if tree.root_node.has_error:
                blanked = _blank_header_attributes(parse_bytes)
                if blanked != parse_bytes and len(blanked) == len(parse_bytes):
                    alt, alt_used = _parse_best(parser, other, blanked)
                    a, b = _definition_count(alt), _definition_count(tree)
                    if a > b or (a == b and _error_bytes(alt) < _error_bytes(tree)):
                        tree, used, parse_bytes = alt, alt_used, blanked
        except Exception as exc:
            log_warn(f"Tree-sitter parse failed for {file}: {exc}")
            return self._full_file(file, text)

        file_datetime = get_file_datetime(file)
        collector = _ChunkCollector(
            file_name=file.name,
            file_path=str(file),
            unit_name=file.stem,
            content_bytes=content_bytes,
            lines=text.splitlines(),
            file_datetime=file_datetime,
            reader=self,
            parser=used,
            parse_bytes=parse_bytes,
        )
        collector.walk(tree.root_node, ())
        documents = collector.documents()
        if documents:
            return documents
        return self._full_file(file, text)

    def _full_file(self, file: Path, text: str) -> List[Document]:
        stripped = _strip_log_comments(text).strip()
        if not stripped:
            return []
        return [
            Document(
                text=stripped,
                metadata={
                    "file_path": str(file),
                    "node_type": "full_file",
                    "unit_name": file.stem,
                    **get_file_datetime(file),
                },
            )
        ]

    def make_documents(
        self,
        chunk_text: str,
        node_type: str,
        start_line: int,
        end_line: int,
        start_byte: int,
        end_byte: int,
        file_path: str,
        file_datetime: dict,
        extra: Optional[dict] = None,
        max_chars: Optional[int] = None,
        symbol_anchors: Optional[Dict[str, str]] = None,
    ) -> List[Document]:
        """Build one document, or split parts when the text is too long.

        ``symbol_anchors`` maps a derived symbol (a macro alias) to the name
        in the text it comes from; used only by ``SYMBOLS_PER_SPLIT_PART``.
        """
        if len(chunk_text.strip()) < self.MIN_CHUNK_SIZE:
            return []

        threshold = self.MAX_CHUNK_CHARS if max_chars is None else max_chars
        metadata = {
            "file_path": file_path,
            "node_type": node_type,
            "start_line": start_line,
            "end_line": end_line,
            "start_byte": start_byte,
            "end_byte": end_byte,
            **file_datetime,
        }
        if extra:
            metadata.update(extra)

        policy = get_symbol_policy()
        if len(chunk_text) <= threshold:
            meta_out = apply_symbol_policy(metadata, policy=policy)
            return [Document(text=chunk_text, metadata=meta_out)]

        prefix_lines: List[str] = []
        for line in chunk_text.split("\n"):
            if line.startswith("//"):
                prefix_lines.append(line)
            else:
                break
        prefix = "\n".join(prefix_lines)
        parts = self._text_splitter.split_text(chunk_text)
        matcher = None
        if policy.per_split_part and isinstance(metadata.get("symbols"), list):
            matcher = SymbolMatcher(metadata["symbols"], symbol_anchors)
        docs: List[Document] = []
        for index, part in enumerate(parts):
            if len(part.strip()) < self.MIN_CHUNK_SIZE:
                continue
            piece = part
            if prefix and not part.startswith("//"):
                piece = f"{prefix}\n{part}"
            part_meta = {
                **metadata,
                "node_type": f"{node_type}_split",
                "split_part": index,
                "split_total": len(parts),
            }
            docs.append(
                Document(
                    text=piece,
                    metadata=apply_symbol_policy(
                        part_meta, part_text=part, policy=policy, matcher=matcher
                    ),
                )
            )
        return docs


class _ChunkCollector:
    """Walk one translation unit and record chunks in source order."""

    def __init__(
        self,
        file_name: str,
        file_path: str,
        unit_name: str,
        content_bytes: bytes,
        lines: List[str],
        file_datetime: dict,
        reader: CppFileReader,
        parser=None,
        parse_bytes: Optional[bytes] = None,
    ) -> None:
        self.parser = parser
        self.parse_bytes = parse_bytes if parse_bytes is not None else content_bytes
        self.file_name = file_name
        self.file_path = file_path
        self.unit_name = unit_name
        self.content_bytes = content_bytes
        self.lines = lines
        self.file_datetime = file_datetime
        self.reader = reader
        self.includes: List[str] = []
        self.events: List[dict] = []
        # Set only while collecting members of one class.  Nested classes
        # save and restore it.
        self._member: Optional[dict] = None

    def walk(self, node: Node, namespace: tuple[str, ...]) -> None:
        if _is_log_comment(node, self.content_bytes):
            return

        if node.type in _TYPE_SPECIFIERS and _has_field_body(node):
            self._emit_type(node, namespace)
            return

        if node.type == "enum_specifier":
            self._emit_enum(node, namespace)
            return

        if node.type == "function_definition":
            if self._split_swallowed(node, namespace):
                return
            self._emit_function(node, namespace)
            return

        if node.type == "namespace_definition":
            name = _namespace_name(node, self.content_bytes)
            next_ns = namespace + ((name,) if name else ("(anonymous)",))
            for child in node.children:
                if child.type == "declaration_list":
                    self.walk(child, next_ns)
            return

        if node.type == "declaration":
            self._emit_declaration(node, namespace)
            return

        if node.type == "preproc_include":
            self.includes.append(_collapse(_node_text(node, self.content_bytes)))
            return

        if node.type in ("preproc_def", "preproc_function_def"):
            if not _is_include_guard(node, self.content_bytes):
                self._add_macro(node, namespace)
            return

        if node.type == "comment":
            return

        if node.type == "ERROR" and self._recover_error_region(node, namespace):
            return

        if node.type in _RECURSE_TYPES:
            children = node.children
            index = 0
            while index < len(children):
                child = children[index]
                taken = self._try_split_signature(child, children[index + 1 :], namespace)
                if taken:
                    index += taken
                    continue
                nxt = children[index + 1] if index + 1 < len(children) else None
                if nxt is not None and self._emit_macro_definition(child, nxt, namespace):
                    index += 2
                    continue
                self.walk(child, namespace)
                index += 1

    # A region the grammar could not parse is re-parsed in pieces split at
    # lines that close a top-level block (``}`` / ``};`` in column 0), so one
    # unknown construct costs one definition instead of the rest of the file.
    MIN_RECOVERY_LINES = 30

    def _recover_error_region(self, node: Node, namespace: tuple[str, ...]) -> bool:
        if self.parser is None or getattr(self, "_in_recovery", False):
            return False
        if node.end_point[0] - node.start_point[0] + 1 < self.MIN_RECOVERY_LINES:
            return False
        data = self.parse_bytes
        start, end = node.start_byte, node.end_byte
        cuts = [start]
        for m in re.finditer(rb"\n\}[ \t]*;?[ \t]*(?=\n)", data[start:end]):
            cuts.append(start + m.end())
        cuts.append(end)
        if len(cuts) <= 2:
            return False
        for a, b in zip(cuts, cuts[1:]):
            self._reparse_segment(a, b, namespace, in_recovery=True)
        return True

    def _reparse_segment(self, a: int, b: int, namespace: tuple[str, ...], in_recovery: bool) -> bool:
        """Parse bytes ``a:b`` on their own and add their chunks."""
        data = self.parse_bytes
        if not data[a:b].strip():
            return False
        seg_line = data.count(b"\n", 0, a)
        # pad with newlines so rows match; bytes are shifted back below
        pad = seg_line
        buf = b"\n" * pad + data[a:b]
        try:
            tree = self.parser.parse(buf)
        except Exception:  # noqa: BLE001
            return False
        sub = _ChunkCollector(
            self.file_name, self.file_path, self.unit_name,
            b"\n" * pad + self.content_bytes[a:b], self.lines,
            self.file_datetime, self.reader, parser=self.parser, parse_bytes=buf,
        )
        sub._in_recovery = in_recovery or getattr(self, "_in_recovery", False)
        sub._split_depth = getattr(self, "_split_depth", 0) + 1
        sub.walk(tree.root_node, namespace)
        shift = a - pad
        for event in sub.events:
            for item in event.get("items", [event]):
                if "start_byte" in item:
                    item["start_byte"] += shift
                    item["end_byte"] += shift
            self.events.append(event)
        self.includes.extend(sub.includes)
        return True

    # A function body the grammar could not close (an unknown macro inside
    # it, e.g. ``switch (x) { N(A) N(B) }``) swallows every following
    # definition up to the end of the file.  Kernel/K&R style closes a
    # top-level body with ``}`` in column 0, so the body is cut there and
    # the rest is parsed again on its own.
    _COLUMN0_CLOSE = re.compile(rb"\n\}[ \t\r]*;?[ \t\r]*(?=\n|\Z)")
    MAX_SPLIT_DEPTH = 200

    def _split_swallowed(self, node: Node, namespace: tuple[str, ...]) -> bool:
        if self.parser is None or not node.has_error:
            return False
        if getattr(self, "_split_depth", 0) >= self.MAX_SPLIT_DEPTH:
            return False
        if node.start_point[1] != 0 and (node.parent is None or node.parent.type != "template_declaration"):
            return False
        body = node.child_by_field_name("body")
        if body is None or body.type != "compound_statement":
            return False
        data = self.parse_bytes
        m = self._COLUMN0_CLOSE.search(data, body.start_byte, node.end_byte)
        if m is None:
            return False
        cut = m.end()
        rest = data[cut : node.end_byte]
        # nothing but the closing brace / whitespace after it: not swallowed
        if len(rest.strip()) < 2 or rest.count(b"\n") < 2:
            return False
        declarator = _function_declarator(node)
        scope, func_name = (
            _split_qualified(declarator, self.content_bytes) if declarator is not None else (None, "")
        )
        span = _span_node(node)
        start = self._blanked_lead(span.start_byte)
        end_row = data.count(b"\n", 0, cut - 1)
        event = {
            "kind": "func",
            "namespace": namespace,
            "class_name": scope or "",
            "class_header": None,
            "func_name": func_name,
            "text": self.content_bytes[start : cut].decode("utf-8", errors="replace").strip(),
            "lines": end_row - span.start_point[0] + 1,
            "start_line": span.start_point[0] + 1,
            "end_line": end_row + 1,
            "start_byte": start,
            "end_byte": cut,
        }
        if not func_name:
            self._name_macro_function(node, event)
        self._attach_comment(event, span)
        self.events.append(event)
        self._reparse_segment(cut, node.end_byte, namespace, in_recovery=False)
        return True

    def _emit_macro_definition(self, head: Node, body: Node, namespace: tuple[str, ...]) -> bool:
        """``NAME(args) { ... }`` at file scope: a function defined through a
        macro (``SYSCALL_DEFINE2(name, ...)``, ``TEST(Suite, Case)``).  The
        grammar sees a call statement without ``;`` followed by a block."""
        if body.type != "compound_statement" or head.type != "expression_statement":
            return False
        call = head.named_children[0] if head.named_children else None
        if call is None or call.type != "call_expression" or len(head.named_children) != 1:
            return False
        semi = [c for c in head.children if c.type == ";"]
        if semi and not semi[0].is_missing and semi[0].end_byte > semi[0].start_byte:
            return False
        if body.start_point[0] - call.end_point[0] > 1:
            return False
        func = call.child_by_field_name("function")
        args = call.child_by_field_name("arguments")
        if func is None or func.type != "identifier" or args is None:
            return False
        macro = _node_text(func, self.content_bytes)
        first = next((c for c in args.named_children), None)
        name = _node_text(first, self.content_bytes).strip() if first is not None and first.type == "identifier" else macro
        event = {
            "kind": "func",
            "namespace": namespace,
            "class_name": "",
            "class_header": None,
            "func_name": name,
            "text": self.content_bytes[head.start_byte : body.end_byte].decode("utf-8", errors="replace").strip(),
            "lines": body.end_point[0] - head.start_point[0] + 1,
            "start_line": head.start_point[0] + 1,
            "end_line": body.end_point[0] + 1,
            "start_byte": head.start_byte,
            "end_byte": body.end_byte,
            "macro": macro,
        }
        aliases = _macro_aliases(macro, name) if name != macro else []
        if aliases:
            event["aliases"] = aliases
        self._attach_comment(event, head)
        self.events.append(event)
        return True

    def _try_split_signature(self, node: Node, following: List[Node], namespace: tuple[str, ...]) -> int:
        """Emit one function when ``node`` is a conditional signature.  Return
        how many of ``[node, *following]`` were consumed, or 0."""
        if node.type not in _PREPROC_OPEN:
            return 0
        content = self.content_bytes
        swallowed = _swallowed_body(node)
        if swallowed is not None and _is_signature_header(node, content, swallowed.start_byte):
            self._emit_split_function(node, swallowed, namespace, node)
            self._replay_after(node, swallowed.end_byte, namespace)
            return 1
        if _is_signature_header(node, content, None):
            body, extra = _take_sibling_body(node, following, content)
            if body is not None:
                self._emit_split_function(node, body, namespace, node)
                return 1 + extra
        if _is_type_only_header(node, content):
            func, extra = _take_following_function(node, following, content)
            if func is not None:
                self._emit_split_function(node, func, namespace, func)
                return 1 + extra
        return 0

    def _emit_split_function(
        self,
        preproc: Node,
        end_node: Node,
        namespace: tuple[str, ...],
        name_node: Node,
    ) -> None:
        decls = _collect_signature_decls(preproc, preproc, end_node.start_byte)
        scope: Optional[str] = None
        func_name = ""
        for decl in decls:
            found_scope, found_name = _decl_name(decl, self.content_bytes)
            if found_name and not func_name:
                scope, func_name = found_scope, found_name
            elif found_scope and scope is None:
                scope = found_scope
        if not func_name:
            scope, func_name = _decl_name(name_node, self.content_bytes)
        origin = preproc
        prev = preproc.prev_sibling
        if prev is not None and prev.type == "ERROR":
            gap = self.content_bytes[prev.end_byte : preproc.start_byte]
            lead = _node_text(prev, self.content_bytes).lstrip()
            if lead.startswith("template") and not gap.strip():
                origin = prev
        member = self._member
        class_name = scope or (member["class_name"] if member is not None else "") or ""
        class_header = member["class_header"] if member is not None else None
        start = self._blanked_lead(origin.start_byte)
        event = {
            "kind": "func",
            "namespace": namespace,
            "class_name": class_name,
            "class_header": class_header,
            "func_name": func_name,
            "text": self.content_bytes[start : end_node.end_byte].decode("utf-8", errors="replace").strip(),
            "lines": end_node.end_point[0] - origin.start_point[0] + 1,
            "start_line": origin.start_point[0] + 1,
            "end_line": end_node.end_point[0] + 1,
            "start_byte": start,
            "end_byte": end_node.end_byte,
        }
        if not func_name:
            anchor = name_node if name_node.type == "function_definition" else preproc
            self._name_macro_function(anchor, event)
        self._attach_comment(event, origin)
        if member is None:
            self.events.append(event)
            return
        self._add_member_signatures(preproc, end_node, decls)
        member["functions"].append(event)

    def _add_member_signatures(self, preproc: Node, end_node: Node, decls: List[Node]) -> None:
        member = self._member
        if member is None:
            return
        added = False
        for decl in decls:
            signature = _summary_signature(decl, self.content_bytes)
            if signature and signature not in ("{", "}"):
                member["lines"].append(signature + ";")
                added = True
        if not added:
            body = _direct_body(end_node) or end_node
            raw = self.content_bytes[preproc.start_byte : body.start_byte].decode(
                "utf-8", errors="replace"
            )
            raw = _PREPROC_DIRECTIVE.sub(" ", raw)
            signature = _collapse(raw).strip().rstrip(";").strip()
            if signature and signature not in ("{", "}"):
                member["lines"].append(signature + ";")
        member["counts"]["methods"] += 1
        section = member.get("section") or ""
        if section == "signals":
            member["counts"]["signals"] += 1
        elif section.endswith("slots"):
            member["counts"]["slots"] += 1

    def _replay_after(self, preproc: Node, pos: int, namespace: tuple[str, ...]) -> None:
        """Walk nodes the grammar nested after the real function body."""
        extras = _top_nodes_after(preproc, pos)
        index = 0
        while index < len(extras):
            extra = extras[index]
            if extra.type in _DIRECTIVE_TYPES or extra.is_missing:
                index += 1
                continue
            taken = self._try_split_signature(extra, extras[index + 1 :], namespace)
            if taken:
                index += taken
                continue
            if self._member is not None:
                member = self._member
                member["section"] = self._one_member(
                    extra,
                    namespace,
                    member["class_name"],
                    member["class_header"],
                    member["lines"],
                    member["functions"],
                    member["counts"],
                    member["section"],
                )
            else:
                self.walk(extra, namespace)
            index += 1

    # Comments directly above a definition (doc comments, kernel-doc) become
    # part of its chunk.  License headers and CVS logs are left out.
    MAX_LEADING_COMMENT_CHARS = 2000

    def _leading_comment(self, node: Node) -> Optional[Node]:
        target = node
        while (
            target.prev_sibling is None or target.prev_sibling.type != "comment"
        ) and target.parent is not None and target.parent.type in (
            "declaration", "type_definition", "template_declaration", "field_declaration",
        ) and target.parent.start_byte == target.start_byte:
            target = target.parent
        first = None
        row = target.start_point[0]
        prev = target.prev_sibling
        while prev is not None and prev.type == "comment" and row - prev.end_point[0] <= 1:
            before = prev.prev_sibling
            if before is not None and before.end_point[0] == prev.start_point[0] and before.type != "comment":
                break  # trailing comment of the previous statement
            text = _node_text(prev, self.content_bytes)
            if "$Log:" in text or "SPDX-License-Identifier" in text or re.search(r"(?i)\bcopyright\b", text):
                break
            first = prev
            row = prev.start_point[0]
            prev = before
        return first

    def _attach_comment(self, event: dict, node: Node) -> None:
        first = self._leading_comment(node)
        if first is None:
            return
        start = first.start_byte
        comment = self.content_bytes[start : event["start_byte"]].decode("utf-8", errors="replace").strip()
        if not comment or len(comment) > self.MAX_LEADING_COMMENT_CHARS:
            if comment:
                comment = comment[-self.MAX_LEADING_COMMENT_CHARS :]
                nl = comment.find("\n")
                comment = comment[nl + 1 :] if nl >= 0 else comment
            if not comment:
                return
        event["text"] = comment + "\n" + event["text"]
        event["start_line"] = first.start_point[0] + 1
        event["start_byte"] = start
        if "lines" in event:
            event["lines"] = event["end_line"] - event["start_line"] + 1

    def _emit_declaration(self, node: Node, namespace: tuple[str, ...]) -> None:
        for child in node.children:
            if child.type in _TYPE_SPECIFIERS and _has_field_body(child):
                self._emit_type(child, namespace)
                return
            if child.type == "enum_specifier":
                self._emit_enum(child, namespace)
                return
        declarator = _function_declarator(node)
        if declarator is None:
            self._emit_initialized_data(node, namespace)
            return
        if _find_first(node, {"compound_statement"}) is not None:
            self._emit_function(node, namespace)
            return
        span = _span_node(node)
        self.events.append(
            {
                "kind": "proto",
                "namespace": namespace,
                "text": _signature(span, self.content_bytes) + ";",
                "start_line": span.start_point[0] + 1,
                "end_line": span.end_point[0] + 1,
                "start_byte": span.start_byte,
                "end_byte": span.end_byte,
            }
        )

    MIN_DATA_LINES = 3
    # Large tables (firmware blobs, register lists) are cut, not split.
    MAX_DATA_CHARS = 3000

    def _emit_initialized_data(self, node: Node, namespace: tuple[str, ...]) -> None:
        """File-scope variable with an aggregate initializer (an operations
        table, a lookup array): ``const struct ops x = { .open = f, ... };``."""
        if node.end_point[0] - node.start_point[0] + 1 < self.MIN_DATA_LINES:
            return
        init = next((c for c in node.children if c.type == "init_declarator"), None)
        if init is None:
            return
        value = init.child_by_field_name("value")
        if value is None or value.type != "initializer_list":
            return
        ident = _find_first(init.child_by_field_name("declarator") or init, {"identifier"})
        if ident is None:
            return
        name = _node_text(ident, self.content_bytes)
        prefix = _context_prefix(self.file_name, namespace)
        event = {
            "kind": "doc",
            "node_type": "variable_definition",
            "text": _node_text(node, self.content_bytes).strip(),
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "start_byte": node.start_byte,
            "end_byte": node.end_byte,
            "extra": {"unit_name": self.unit_name, "object_name": name},
            "max_chars": None,
        }
        self._attach_comment(event, node)
        text = event["text"]
        if len(text) > self.MAX_DATA_CHARS:
            cut = text.rfind("\n", 0, self.MAX_DATA_CHARS)
            text = text[: cut if cut > 0 else self.MAX_DATA_CHARS] + "\n\t/* ... */\n};"
        event["text"] = f"{prefix}\n{text}"
        self.events.append(event)

    def _emit_type(self, node: Node, namespace: tuple[str, ...]) -> None:
        name = _type_name(node, self.content_bytes)
        if not name:
            return
        span = _span_node(node)
        header = _class_header(node, self.content_bytes)
        kind = _type_kind(node, self.content_bytes)
        bases = _base_classes(node, self.content_bytes)
        prefix = _context_prefix(self.file_name, namespace, class_header=header)
        summary_lines, counts, functions = self._members(node, namespace, name, header)
        body = "\n".join(summary_lines)
        doc = {"text": "", "start_byte": span.start_byte, "end_line": span.end_point[0] + 1}
        self._attach_comment(doc, span)
        lead = doc["text"]
        summary_text = f"{prefix}\n{lead}{header} {{\n{body}\n}}"
        extra = {
            "class_name": name,
            "unit_name": self.unit_name,
            "object_name": name,
        }
        if len(summary_text) > self.reader.MAX_SUMMARY_CHARS:
            overview = self._overview(
                prefix, name, kind, bases, counts, summary_lines
            )
            self.events.append(
                {
                    "kind": "doc",
                    "node_type": "class_overview",
                    "text": overview,
                    "start_line": span.start_point[0] + 1,
                    "end_line": span.end_point[0] + 1,
                    "start_byte": span.start_byte,
                    "end_byte": span.end_byte,
                    "extra": extra,
                    "max_chars": None,
                }
            )
        self.events.append(
            {
                "kind": "doc",
                "node_type": "class_summary",
                "text": summary_text,
                "start_line": span.start_point[0] + 1,
                "end_line": span.end_point[0] + 1,
                "start_byte": span.start_byte,
                "end_byte": span.end_byte,
                "extra": extra,
                "max_chars": self.reader.MAX_SUMMARY_CHARS,
            }
        )
        self.events.extend(functions)

    def _members(
        self,
        type_node: Node,
        namespace: tuple[str, ...],
        class_name: str,
        class_header: str,
    ) -> tuple[List[str], dict, List[dict]]:
        lines: List[str] = []
        functions: List[dict] = []
        counts = {"methods": 0, "fields": 0, "slots": 0, "signals": 0}
        body = next(
            (
                child
                for child in type_node.children
                if child.type == "field_declaration_list"
            ),
            None,
        )
        if body is None:
            return lines, counts, functions

        class_bytes = self.content_bytes[type_node.start_byte : type_node.end_byte]
        if b"Q_OBJECT" in class_bytes:
            lines.append("Q_OBJECT")

        outer = self._member
        self._member = {
            "lines": lines,
            "functions": functions,
            "counts": counts,
            "class_name": class_name,
            "class_header": class_header,
            "section": "public",
            "namespace": namespace,
        }
        try:
            children = list(body.children)
            index = 0
            while index < len(children):
                child = children[index]
                taken = self._try_split_signature(child, children[index + 1 :], namespace)
                if taken:
                    index += taken
                    continue
                self._member["section"] = self._one_member(
                    child,
                    namespace,
                    class_name,
                    class_header,
                    lines,
                    functions,
                    counts,
                    self._member["section"],
                )
                index += 1
        finally:
            self._member = outer
        return lines, counts, functions

    def _one_member(
        self,
        node: Node,
        namespace: tuple[str, ...],
        class_name: str,
        class_header: str,
        lines: List[str],
        functions: List[dict],
        counts: dict,
        section: str,
    ) -> str:
        if _is_log_comment(node, self.content_bytes):
            return section
        if node.type == "access_specifier":
            label = _access_label(self.lines, node)
            if label:
                section = label
                lines.append(f"{label}:")
            return section
        if node.type == "comment":
            comment = _collapse(_node_text(node, self.content_bytes))
            if comment and "$Log:" not in comment:
                lines.append(comment)
            return section
        if node.type in _TYPE_SPECIFIERS and _has_field_body(node):
            nested = _type_name(node, self.content_bytes)
            if nested:
                lines.append(f"{_type_kind(node, self.content_bytes)} {nested};")
                self._emit_type(node, namespace)
            return section
        if node.type == "enum_specifier":
            lines.append(_signature(node, self.content_bytes) + ";")
            return section
        if node.type in ("preproc_ifdef", "preproc_if", "preproc_else", "preproc_elif", "ERROR"):
            children = list(node.children)
            index = 0
            while index < len(children):
                child = children[index]
                taken = self._try_split_signature(child, children[index + 1 :], namespace)
                if taken:
                    index += taken
                    continue
                section = self._one_member(
                    child,
                    namespace,
                    class_name,
                    class_header,
                    lines,
                    functions,
                    counts,
                    section,
                )
                index += 1
            if self._member is not None:
                self._member["section"] = section
            return section
        if node.type in ("field_declaration", "declaration", "function_definition"):
            self._member_decl(
                node, namespace, class_name, class_header, lines, functions, counts, section
            )
            return section
        return section

    def _member_decl(
        self,
        node: Node,
        namespace: tuple[str, ...],
        class_name: str,
        class_header: str,
        lines: List[str],
        functions: List[dict],
        counts: dict,
        section: str,
    ) -> None:
        declarator = _function_declarator(node)
        has_body = _find_first(node, {"compound_statement"}) is not None
        if declarator is None and not has_body:
            enum_node = _find_first(node, {"enum_specifier"})
            if enum_node is not None:
                lines.append(_signature(enum_node, self.content_bytes) + ";")
                return
            field = _signature(node, self.content_bytes)
            if field and field not in ("{", "}"):
                lines.append(field + ";")
                counts["fields"] += 1
            return

        sig = _signature(node, self.content_bytes)
        if sig:
            lines.append(sig + ";")
        counts["methods"] += 1
        if section == "signals":
            counts["signals"] += 1
        elif section.endswith("slots"):
            counts["slots"] += 1
        if has_body:
            scope, func_name = (
                _split_qualified(declarator, self.content_bytes)
                if declarator is not None
                else (None, "")
            )
            functions.append(
                self._function_event(
                    node,
                    namespace,
                    scope or class_name,
                    func_name,
                    class_header,
                )
            )

    def _emit_function(self, node: Node, namespace: tuple[str, ...]) -> None:
        declarator = _function_declarator(node)
        scope, func_name = (
            _split_qualified(declarator, self.content_bytes)
            if declarator is not None
            else (None, "")
        )
        event = self._function_event(node, namespace, scope, func_name, None)
        if not func_name:
            self._name_macro_function(node, event)
        self.events.append(event)

    def _name_macro_function(self, node: Node, event: dict) -> None:
        """``SYSCALL_DEFINE0(getpid) { ... }`` / ``DEFINE_IDTENTRY(exc_x) {``:
        the grammar reads the macro as a type and ``(name)`` as a
        parenthesized declarator.  The name is the identifier in the
        parentheses; a plain ``name(void) {`` without a return type is
        named after the "type"."""
        kids = node.children
        for i, child in enumerate(kids[:-1]):
            if child.type != "type_identifier" or kids[i + 1].type != "parenthesized_declarator":
                continue
            macro = _node_text(child, self.content_bytes).strip()
            inner = next((c for c in kids[i + 1].named_children if c.type == "identifier"), None)
            if re.fullmatch(r"[A-Z_][A-Z0-9_]*", macro) and inner is not None:
                name = _node_text(inner, self.content_bytes).strip()
                event["func_name"] = name
                event["macro"] = macro
                aliases = _macro_aliases(macro, name)
                if aliases:
                    event["aliases"] = aliases
            elif not re.fullmatch(r"[A-Z_][A-Z0-9_]*", macro):
                event["func_name"] = macro
            return

    def _blanked_lead(self, start_byte: int) -> int:
        """Start of the line when everything before ``start_byte`` on it was
        blanked for parsing only (attribute macros); else ``start_byte``."""
        data = self.parse_bytes
        line_start = data.rfind(b"\n", 0, start_byte) + 1
        if line_start >= start_byte or data[line_start:start_byte].strip():
            return start_byte
        if not self.content_bytes[line_start:start_byte].strip():
            return start_byte
        return line_start

    def _function_event(
        self,
        node: Node,
        namespace: tuple[str, ...],
        class_name: Optional[str],
        func_name: str,
        class_header: Optional[str],
    ) -> dict:
        span = _span_node(node)
        start = self._blanked_lead(span.start_byte)
        event = {
            "kind": "func",
            "namespace": namespace,
            "class_name": class_name or "",
            "class_header": class_header,
            "func_name": func_name,
            "text": self.content_bytes[start : span.end_byte].decode("utf-8", errors="replace").strip(),
            "lines": span.end_point[0] - span.start_point[0] + 1,
            "start_line": span.start_point[0] + 1,
            "end_line": span.end_point[0] + 1,
            "start_byte": start,
            "end_byte": span.end_byte,
        }
        self._attach_comment(event, span)
        return event

    def _emit_enum(self, node: Node, namespace: tuple[str, ...]) -> None:
        name = _type_name(node, self.content_bytes) or ""
        prefix = _context_prefix(self.file_name, namespace, class_name=name or None)
        doc = {"text": _node_text(node, self.content_bytes).strip(), "start_byte": node.start_byte,
               "end_line": node.end_point[0] + 1}
        self._attach_comment(doc, node)
        text = doc["text"]
        extra = {"unit_name": self.unit_name}
        if name:
            extra["class_name"] = name
            extra["object_name"] = name
        self.events.append(
            {
                "kind": "doc",
                "node_type": "enum_declaration",
                "text": f"{prefix}\n{text}",
                "start_line": node.start_point[0] + 1,
                "end_line": node.end_point[0] + 1,
                "start_byte": node.start_byte,
                "end_byte": node.end_byte,
                "extra": extra,
                "max_chars": None,
            }
        )

    def _add_macro(self, node: Node, namespace: tuple[str, ...]) -> None:
        text = _node_text(node, self.content_bytes).strip()
        line_count = node.end_point[0] - node.start_point[0] + 1
        name_node = node.child_by_field_name("name")
        event = {
            "kind": "macro",
            "namespace": namespace,
            "text": text,
            "lines": line_count,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "start_byte": node.start_byte,
            "end_byte": node.end_byte,
            "name": _node_text(name_node, self.content_bytes) if name_node is not None else "",
        }
        self._attach_comment(event, node)
        self.events.append(event)

    def _overview(
        self,
        prefix: str,
        name: str,
        kind: str,
        bases: List[str],
        counts: dict,
        summary_lines: List[str],
    ) -> str:
        inherits = ""
        if bases:
            inherits = " inheriting from " + ", ".join(bases)
        plain_methods = counts["methods"] - counts["signals"] - counts["slots"]
        parts: List[str] = []
        if plain_methods or not (counts["signals"] or counts["slots"]):
            parts.append(f"{plain_methods} methods")
        if counts["fields"]:
            parts.append(f"{counts['fields']} fields")
        if counts["signals"]:
            parts.append(f"{counts['signals']} signals")
        if counts["slots"]:
            parts.append(f"{counts['slots']} slots")
        sentence = (
            f"{name} is a C++ {kind}{inherits} with " + ", ".join(parts) + "."
        )
        kept: List[str] = []
        used = len(prefix) + len(sentence)
        for line in summary_lines:
            if used + len(line) > 2000:
                break
            kept.append(line)
            used += len(line) + 1
        listing = "\n".join(kept)
        return f"{prefix}\n{sentence}\n{listing}".rstrip()

    def documents(self) -> List[Document]:
        docs: List[Document] = []
        if self.includes:
            prefix = _context_prefix(self.file_name, ())
            text = prefix + "\n" + "\n".join(self.includes)
            docs.extend(
                self.reader.make_documents(
                    text,
                    "include_group",
                    1,
                    1,
                    0,
                    0,
                    self.file_path,
                    self.file_datetime,
                    extra={"unit_name": self.unit_name},
                )
            )

        grouped = self._group_events(self.events)
        for event in grouped:
            if event["kind"] == "doc":
                docs.extend(
                    self.reader.make_documents(
                        event["text"],
                        event["node_type"],
                        event["start_line"],
                        event["end_line"],
                        event["start_byte"],
                        event["end_byte"],
                        self.file_path,
                        self.file_datetime,
                        extra=event.get("extra"),
                        max_chars=event.get("max_chars"),
                    )
                )
            elif event["kind"] == "func":
                docs.extend(self._function_docs([event], "cpp_function"))
            elif event["kind"] == "func_group":
                docs.extend(self._function_docs(event["items"], "method_group"))
            elif event["kind"] == "proto_group":
                docs.extend(self._text_group_docs(event, "declaration_group"))
            elif event["kind"] == "macro_group":
                node_type = (
                    "macro_definition"
                    if len(event["items"]) == 1
                    and event["items"][0]["lines"] > self.reader.LONG_MACRO_LINES
                    else "macro_group"
                )
                docs.extend(self._text_group_docs(event, node_type))
        return docs

    def _group_events(self, events: List[dict]) -> List[dict]:
        grouped: List[dict] = []
        index = 0
        while index < len(events):
            event = events[index]
            if event["kind"] == "func":
                run = [event]
                nxt = index + 1
                while (
                    nxt < len(events)
                    and events[nxt]["kind"] == "func"
                    and events[nxt]["class_name"] == event["class_name"]
                    and events[nxt]["namespace"] == event["namespace"]
                    and events[nxt]["lines"] <= self.reader.TRIVIAL_METHOD_LINES
                    and event["lines"] <= self.reader.TRIVIAL_METHOD_LINES
                ):
                    run.append(events[nxt])
                    nxt += 1
                if (
                    len(run) >= self.reader.MIN_TRIVIAL_RUN
                    and event["lines"] <= self.reader.TRIVIAL_METHOD_LINES
                ):
                    grouped.append({"kind": "func_group", "items": run})
                    index = nxt
                    continue
                grouped.append(event)
                index += 1
                continue
            if event["kind"] in ("proto", "macro"):
                run = [event]
                nxt = index + 1
                while (
                    nxt < len(events)
                    and events[nxt]["kind"] == event["kind"]
                    and events[nxt]["namespace"] == event["namespace"]
                ):
                    run.append(events[nxt])
                    nxt += 1
                kind = "proto_group" if event["kind"] == "proto" else "macro_group"
                grouped.append({"kind": kind, "items": run, "namespace": event["namespace"]})
                index = nxt
                continue
            grouped.append(event)
            index += 1
        return grouped

    def _function_docs(self, items: List[dict], node_type: str) -> List[Document]:
        first = items[0]
        class_name = first["class_name"]
        header = first.get("class_header")
        prefix = _context_prefix(
            self.file_name,
            first["namespace"],
            class_header=header if node_type != "cpp_function" else None,
            class_name=class_name or None,
        )
        if node_type == "cpp_function" and class_name and not header:
            prefix = _context_prefix(
                self.file_name, first["namespace"], class_name=class_name
            )
        body = "\n\n".join(item["text"] for item in items)
        if len(body) > self.reader.MAX_GROUP_CHARS and node_type == "method_group":
            docs: List[Document] = []
            for item in items:
                docs.extend(self._function_docs([item], "cpp_function"))
            return docs
        extra = {"unit_name": self.unit_name}
        if class_name:
            extra["class_name"] = class_name
        names = [item["func_name"] for item in items if item.get("func_name")]
        aliases = [a for item in items for a in item.get("aliases", ())]
        if names:
            extra["object_name"] = ", ".join(names)
            if len(names) > 1 or aliases:
                extra["symbols"] = names + aliases
        # a macro alias (sys_read) is present wherever its name (read) is
        anchors = {
            alias: item["func_name"]
            for item in items
            if item.get("func_name")
            for alias in item.get("aliases", ())
        }
        return self.reader.make_documents(
            f"{prefix}\n{body}",
            node_type,
            first["start_line"],
            items[-1]["end_line"],
            first["start_byte"],
            items[-1]["end_byte"],
            self.file_path,
            self.file_datetime,
            extra=extra,
            symbol_anchors=anchors or None,
        )

    def _text_group_docs(self, event: dict, node_type: str) -> List[Document]:
        items = event["items"]
        prefix = _context_prefix(self.file_name, event["namespace"])
        text = prefix + "\n" + "\n".join(item["text"] for item in items)
        extra = {"unit_name": self.unit_name}
        names = [item["name"] for item in items if item.get("name")]
        if names:
            # every defined name, for the exact symbol lookup and the reranker
            extra["symbols"] = names
            if len(names) == 1:
                extra["object_name"] = names[0]
        return self.reader.make_documents(
            text,
            node_type,
            items[0]["start_line"],
            items[-1]["end_line"],
            items[0]["start_byte"],
            items[-1]["end_byte"],
            self.file_path,
            self.file_datetime,
            extra=extra,
        )


# ────────────────────────────────────────────────
# Rerank profile (query-time ranking knowledge, see shared/rerank_profile.py)
# ────────────────────────────────────────────────

_CPP_HEADER = re.compile(r"\.(?:h|hh|hpp|hxx|h\+\+|inl)$", re.IGNORECASE)


def _is_cpp_declaration_chunk(node_type: str, file_path: str) -> bool:
    """Prototype lists and the split parts of header class bodies hold
    declarations only; the definition lives elsewhere."""
    if node_type in ("declaration_group", "declaration_group_split"):
        return True
    return node_type == "class_summary_split" and bool(_CPP_HEADER.search(file_path or ""))


_CPP_TYPE_SUMMARY_TYPES = frozenset({"class_summary", "class_summary_split", "class_overview"})


def _is_cpp_type_summary(node_type: str, file_path: str) -> bool:
    """struct / class / union bodies (member lists, no function bodies)."""
    return node_type in _CPP_TYPE_SUMMARY_TYPES


RERANK_PROFILE = RerankProfile(
    name="cpp",
    target_patterns=compile_all(
        [r"\b([A-Za-z][A-Za-z0-9_]*)\.(?:cpp|cc|cxx|hpp|hh|hxx|h|c|ino)\b"]
    ),
    overview_types=frozenset({"enum_declaration"}),
    detail_types=frozenset(
        {"cpp_function", "cpp_function_split", "declaration_group", "macro_group", "macro_definition"}
    ),
    import_types=frozenset({"include_group"}),
    # foo_test.cc, foo_unittest.cpp, test/ and testing/ folders
    test_path_patterns=compile_all(
        [
            r"_(?:unit)?tests?\.(?:cc|cpp|cxx|c|h|hpp)$",
            r"(?:^|/)test_[^/]*\.(?:cc|cpp|cxx|c)$",
            r"(?:^|/)(?:test|testing|testutil|test_util)/",
        ]
    ),
    # Thin glue layers: JNI bindings, C API wrappers, FFI / binding folders.
    binding_path_patterns=compile_all(
        [
            r"(?:^|/)[^/]*jni[^/]*/",
            r"(?:^|/)(?:bindings?|ffi)/",
            r"(?:^|/)c_api[^/]*/",
            r"(?:^|/)(?:c|c_api|capi)\.(?:cc|cpp|cxx|c|h)$",
            r"(?:^|/)[^/]*_c_api\.[^/]+$",
        ]
    ),
    binding_text_patterns=compile_all([r"\bJNIEnv\b", r"\bJNIEXPORT\b"], 0),
    is_declaration_chunk=_is_cpp_declaration_chunk,
    # A call site of the named function is not its definition.
    mention_penalty=0.10,
    # "... types / states / modes enumeration" -> enum; "... flags / bits" -> enum or #define.
    type_intent_rules=(
        (
            re.compile(
                r"\b(?:enums?|enumerat\w*|types|kinds|states|modes|codes|levels|"
                r"flags?|bits|bit\s?masks?|constants)\b",
                re.IGNORECASE,
            ),
            frozenset({"enum_declaration"}),
            0.15,
        ),
        (
            re.compile(r"\b(?:flags?|bits|bit\s?masks?|constants)\b", re.IGNORECASE),
            frozenset({"macro_group", "macro_definition"}),
            0.08,
        ),
    ),
    # C reserved names: __schedule, __alloc_pages_slowpath, __dev_queue_xmit
    # (dunder names such as __init__ / __LINE__ are not matched).
    query_identifier_patterns=compile_all(
        [r"(?<![\w$])(__[A-Za-z][A-Za-z0-9_]*[A-Za-z0-9])(?![\w$])"], 0
    ),
    # "handle a page fault for a vma": the function body, not struct vm_fault.
    summary_yield=0.15,
    is_type_summary=_is_cpp_type_summary,
    body_types=frozenset({"cpp_function", "cpp_function_split", "method_group"}),
    structure_query_patterns=compile_all(
        [
            r"\b(?:struct(?:ures?|s)?|class(?:es)?|unions?|enum\w*|typedefs?|types?|kinds|"
            r"fields?|members?|layouts?|records?|descriptors?|"
            r"states|modes|codes|levels|flags?|bits|bit\s?masks?|"
            r"constants?|macros?|defines?|definitions?|declar\w*|headers?|prototypes?|"
            r"interfaces?|operations?\s+tables?|ops|vtables?|"
            r"what\s+is|what\s+are|represent\w*|information|info|tracked|in-memory|metadata)\b",
            r"\.(?:h|hh|hpp|hxx)\b",
        ]
    ),
)

CppFileReader.rerank_profile = RERANK_PROFILE
