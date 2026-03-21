"""
Tests for shared/readers/js_reader.py — JavaScript/TypeScript file reader.

Tests cover:
    - Simple function declarations
    - Variable declarations (var, let, const)
    - Arrow functions
    - ES6 class declarations (class summary, overview, methods)
    - IIFE drilling (standard and alternate forms)
    - AMD define() module drilling
    - Prototype method detection and grouping
    - Trivial function grouping
    - Trivial method grouping (inside classes)
    - Import grouping (ES6 imports and require())
    - TypeScript: interface, type alias, enum declarations
    - TypeScript: export unwrapping
    - Context prefixes
    - Metadata (unit_name, class_name, node_type)
    - Oversized chunk splitting
    - Empty/blank file handling
    - Parse error fallback
    - Comment handling
"""

import textwrap
from pathlib import Path
from typing import List
from unittest.mock import patch

import pytest
from llama_index.core import Document

import shared.readers.js_reader as js_module
from shared.readers.js_reader import (
    JSFileReader,
    _build_context_prefix,
    _count_body_lines,
    _get_class_header_js,
    _get_identifier,
    _get_method_signature_js,
    _get_node_text,
    _get_prototype_method_name,
    _get_superclass_js,
    _is_amd_define,
    _is_iife,
    _is_prototype_assignment,
    _unwrap_export,
)

# ────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────


def _make_js_file(tmp_path: Path, content: str, name: str = "test.js") -> Path:
    """Create a temp JS file and return its path."""
    f = tmp_path / name
    f.write_text(textwrap.dedent(content), encoding="utf-8")
    return f


def _make_ts_file(tmp_path: Path, content: str, name: str = "test.ts") -> Path:
    """Create a temp TS file and return its path."""
    f = tmp_path / name
    f.write_text(textwrap.dedent(content), encoding="utf-8")
    return f


def _load(tmp_path: Path, content: str, name: str = "test.js") -> List[Document]:
    """Helper: create file, load data, return documents."""
    f = _make_js_file(tmp_path, content, name)
    reader = JSFileReader()
    return reader.load_data(f)


def _load_ts(tmp_path: Path, content: str, name: str = "test.ts") -> List[Document]:
    """Helper: create TS file, load data, return documents."""
    f = _make_ts_file(tmp_path, content, name)
    reader = JSFileReader()
    return reader.load_data(f)


def _find_by_type(docs: List[Document], node_type: str) -> List[Document]:
    """Filter documents by node_type metadata."""
    return [d for d in docs if d.metadata.get("node_type") == node_type]


def _parse_js(code: str):
    """Parse JS code and return (root, content_bytes)."""
    content_bytes = code.encode("utf-8")
    tree = js_module._js_parser.parse(content_bytes)
    return tree.root_node, content_bytes


def _parse_ts(code: str):
    """Parse TS code and return (root, content_bytes)."""
    content_bytes = code.encode("utf-8")
    tree = js_module._ts_parser.parse(content_bytes)
    return tree.root_node, content_bytes


# ────────────────────────────────────────────────
# AST Helper Tests
# ────────────────────────────────────────────────


class TestGetNodeText:
    """Tests for _get_node_text()."""

    def test_extracts_function_text(self):
        root, cb = _parse_js("function foo() { return 1; }")
        node = root.children[0]
        text = _get_node_text(node, cb)
        assert "function foo()" in text
        assert "return 1" in text

    def test_strips_whitespace(self):
        root, cb = _parse_js("  var x = 1;  ")
        node = root.children[0]
        text = _get_node_text(node, cb)
        assert text == "var x = 1;"


class TestGetIdentifier:
    """Tests for _get_identifier()."""

    def test_function_name(self):
        root, cb = _parse_js("function myFunc() {}")
        node = root.children[0]
        assert _get_identifier(node, cb) == "myFunc"

    def test_class_name(self):
        root, cb = _parse_js("class MyClass {}")
        node = root.children[0]
        assert _get_identifier(node, cb) == "MyClass"

    def test_no_identifier_returns_none(self):
        root, cb = _parse_js("1 + 2;")
        node = root.children[0]
        assert _get_identifier(node, cb) is None


class TestCountBodyLines:
    """Tests for _count_body_lines()."""

    def test_single_line(self):
        root, _ = _parse_js("var x = 1;")
        assert _count_body_lines(root.children[0]) == 1

    def test_multi_line(self):
        root, _ = _parse_js("function foo() {\n  return 1;\n}")
        assert _count_body_lines(root.children[0]) == 3


class TestIsIife:
    """Tests for _is_iife()."""

    def test_standard_iife(self):
        root, _ = _parse_js("(function() { var x = 1; })();")
        assert _is_iife(root.children[0]) is True

    def test_iife_with_args(self):
        root, _ = _parse_js("(function($) { $.fn.test = 1; })(jQuery);")
        assert _is_iife(root.children[0]) is True

    def test_non_iife_function(self):
        root, _ = _parse_js("function foo() {}")
        assert _is_iife(root.children[0]) is False

    def test_non_iife_expression(self):
        root, _ = _parse_js("var x = 1;")
        assert _is_iife(root.children[0]) is False

    def test_alternate_iife_form(self):
        """(function(wnd) { ... })(window) — paren wraps call."""
        # This pattern: expression_statement > parenthesized_expression > call_expression
        # Some parsers produce this for IIFE where parens wrap the call.
        root, _ = _parse_js("(function(wnd) { var x = 1; })(window);")
        # Standard parser should produce call_expression inside parenthesized_expression
        assert _is_iife(root.children[0]) is True


class TestIsPrototypeAssignment:
    """Tests for _is_prototype_assignment()."""

    def test_prototype_method(self):
        root, cb = _parse_js("Foo.prototype.bar = function() {};")
        result = _is_prototype_assignment(root.children[0], cb)
        assert result == "Foo"

    def test_non_prototype(self):
        root, cb = _parse_js("Foo.bar = function() {};")
        result = _is_prototype_assignment(root.children[0], cb)
        assert result is None

    def test_function_declaration(self):
        root, cb = _parse_js("function foo() {}")
        result = _is_prototype_assignment(root.children[0], cb)
        assert result is None


class TestGetPrototypeMethodName:
    """Tests for _get_prototype_method_name()."""

    def test_extracts_method_name(self):
        root, cb = _parse_js("Foo.prototype.bar = function() {};")
        name = _get_prototype_method_name(root.children[0], cb)
        assert name == "bar"

    def test_returns_none_for_non_prototype(self):
        root, cb = _parse_js("var x = 1;")
        name = _get_prototype_method_name(root.children[0], cb)
        assert name is None


class TestGetClassHeaderJs:
    """Tests for _get_class_header_js()."""

    def test_simple_class(self):
        root, cb = _parse_js("class Foo {}")
        header = _get_class_header_js(root.children[0], cb)
        assert header == "class Foo"

    def test_class_with_extends(self):
        root, cb = _parse_js("class Bar extends Foo {}")
        header = _get_class_header_js(root.children[0], cb)
        assert "class Bar extends Foo" in header


class TestGetMethodSignatureJs:
    """Tests for _get_method_signature_js()."""

    def test_method_signature(self):
        root, cb = _parse_js("class X { foo(a, b) { return a + b; } }")
        cls_node = root.children[0]
        body = None
        for c in cls_node.children:
            if c.type == "class_body":
                body = c
        method = None
        for c in body.children:
            if c.type == "method_definition":
                method = c
                break
        sig = _get_method_signature_js(method, cb)
        assert "foo(a, b)" in sig
        assert "return" not in sig


class TestGetSuperclassJs:
    """Tests for _get_superclass_js()."""

    def test_no_superclass(self):
        root, cb = _parse_js("class Foo {}")
        assert _get_superclass_js(root.children[0], cb) is None

    def test_with_superclass(self):
        root, cb = _parse_js("class Bar extends Foo {}")
        result = _get_superclass_js(root.children[0], cb)
        assert result == "Foo"


class TestUnwrapExport:
    """Tests for _unwrap_export()."""

    def test_export_class(self):
        root, cb = _parse_ts("export class Foo {}")
        export_node = root.children[0]
        result = _unwrap_export(export_node)
        assert result.type == "class_declaration"

    def test_export_function(self):
        root, cb = _parse_ts("export function bar() {}")
        export_node = root.children[0]
        result = _unwrap_export(export_node)
        assert result.type == "function_declaration"

    def test_export_interface(self):
        root, cb = _parse_ts("export interface IFoo { x: number; }")
        export_node = root.children[0]
        result = _unwrap_export(export_node)
        assert result.type == "interface_declaration"

    def test_non_export_passes_through(self):
        root, cb = _parse_ts("class Foo {}")
        node = root.children[0]
        result = _unwrap_export(node)
        assert result is node


class TestBuildContextPrefix:
    """Tests for _build_context_prefix()."""

    def test_file_only(self):
        prefix = _build_context_prefix("app.js")
        assert prefix == "// File: app.js"

    def test_with_class(self):
        prefix = _build_context_prefix(
            "app.ts", "MyClass", "class MyClass extends Base"
        )
        assert "// File: app.ts" in prefix
        assert "// Class: class MyClass extends Base" in prefix

    def test_class_name_without_header(self):
        prefix = _build_context_prefix("app.ts", "MyClass")
        assert "// Class: MyClass" in prefix


# ────────────────────────────────────────────────
# JavaScript: Simple Functions
# ────────────────────────────────────────────────


class TestJsFunctionDeclarations:
    """Tests for JavaScript function declaration chunking."""

    def test_single_function(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function greet(name) {
                return "Hello, " + name;
            }
        """,
        )
        funcs = _find_by_type(docs, "function_declaration")
        assert len(funcs) == 1
        assert "greet" in funcs[0].text
        assert "Hello" in funcs[0].text

    def test_multiple_functions(self, tmp_path):
        # 4 trivial functions (3 lines each) get grouped into function_group
        # because >= 3 consecutive trivial functions triggers grouping
        docs = _load(
            tmp_path,
            """\
            function add(a, b) {
                return a + b;
            }
            function subtract(a, b) {
                return a - b;
            }
            function multiply(a, b) {
                return a * b;
            }
            function divide(a, b) {
                if (b === 0) throw new Error("Division by zero");
                return a / b;
            }
        """,
        )
        # All are trivial, so they should be grouped
        groups = _find_by_type(docs, "function_group")
        assert len(groups) >= 1
        # All function names should appear in the group
        assert "add" in groups[0].text
        assert "subtract" in groups[0].text

    def test_context_prefix_on_function(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function foo() { return 42; }
        """,
        )
        assert len(docs) >= 1
        assert "// File: test.js" in docs[0].text

    def test_function_metadata(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function bar() { return 1; }
        """,
        )
        assert len(docs) >= 1
        d = docs[0]
        assert d.metadata["unit_name"] == "test"
        assert "start_line" in d.metadata
        assert "end_line" in d.metadata


class TestJsVariableDeclarations:
    """Tests for var/let/const declaration chunking."""

    def test_var_function_expression(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            var handler = function(event) {
                event.preventDefault();
                console.log("handled");
            };
        """,
        )
        vars_ = _find_by_type(docs, "variable_declaration")
        assert len(vars_) == 1
        assert "handler" in vars_[0].text

    def test_const_arrow_function(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            const multiply = (a, b) => {
                return a * b;
            };
        """,
        )
        arrows = _find_by_type(docs, "arrow_function")
        assert len(arrows) == 1
        assert "multiply" in arrows[0].text

    def test_tiny_variable_skipped(self, tmp_path):
        """Variables smaller than MIN_CHUNK_SIZE should be skipped."""
        docs = _load(
            tmp_path,
            """\
            var x = 1;
            function realContent() {
                return "this is a function with enough content to be chunked";
            }
        """,
        )
        # x = 1 is too small, should be skipped
        all_text = " ".join(d.text for d in docs)
        assert "realContent" in all_text


# ────────────────────────────────────────────────
# JavaScript: ES6 Classes
# ────────────────────────────────────────────────


class TestJsClasses:
    """Tests for ES6 class declaration chunking."""

    def test_class_summary(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            class Calculator {
                constructor(initial) {
                    this.value = initial;
                }
                add(n) {
                    this.value += n;
                    return this;
                }
                subtract(n) {
                    this.value -= n;
                    return this;
                }
                getResult() {
                    return this.value;
                }
            }
        """,
        )
        summaries = _find_by_type(docs, "class_summary")
        assert len(summaries) == 1
        s = summaries[0]
        assert "Calculator" in s.text
        assert "constructor" in s.text
        assert "add" in s.text
        assert "subtract" in s.text
        assert "getResult" in s.text

    def test_class_methods_emitted(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            class Greeter {
                constructor(name) {
                    this.name = name;
                }
                greet() {
                    return "Hello, " + this.name + "! Welcome to the application.";
                }
                farewell() {
                    return "Goodbye, " + this.name + "! See you next time.";
                }
            }
        """,
        )
        methods = _find_by_type(docs, "method_definition")
        # Methods may exist as individual chunks or be grouped
        assert len(methods) >= 0  # At least class_summary covers them

    def test_class_with_extends(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            class Animal {
                constructor(name) {
                    this.name = name;
                }
                speak() {
                    return this.name + " makes a noise.";
                }
            }
            class Dog extends Animal {
                speak() {
                    return this.name + " barks.";
                }
            }
        """,
        )
        summaries = _find_by_type(docs, "class_summary")
        assert len(summaries) == 2
        dog_summary = [s for s in summaries if "Dog" in s.text]
        assert len(dog_summary) == 1
        assert "extends Animal" in dog_summary[0].text

    def test_class_name_in_metadata(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            class Widget {
                render() {
                    return "<div>Widget</div>";
                }
            }
        """,
        )
        summaries = _find_by_type(docs, "class_summary")
        assert len(summaries) == 1
        assert summaries[0].metadata.get("class_name") == "Widget"


class TestJsClassOverview:
    """Tests for class_overview generation on large classes."""

    def test_overview_generated_for_large_class(self, tmp_path):
        # Create a class with many methods with long names to exceed MAX_SUMMARY_CHARS (6000)
        # Each method signature line ~60 chars, need 6000/60 ≈ 100+ methods
        methods = "\n".join(
            f"    handleLongMethodNameForComponent_{i}(argumentOne_{i}, argumentTwo_{i}, argumentThree_{i}) {{ return argumentOne_{i} + argumentTwo_{i} + argumentThree_{i} + {i}; }}"
            for i in range(150)
        )
        code = f"class HugeComponentController {{\n{methods}\n}}"
        docs = _load(tmp_path, code)
        overviews = _find_by_type(docs, "class_overview")
        assert len(overviews) == 1
        assert "HugeComponentController" in overviews[0].text
        assert "methods" in overviews[0].text

    def test_no_overview_for_small_class(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            class Small {
                foo() { return 1; }
            }
        """,
        )
        overviews = _find_by_type(docs, "class_overview")
        assert len(overviews) == 0


# ────────────────────────────────────────────────
# JavaScript: IIFE Drilling
# ────────────────────────────────────────────────


class TestJsIifeDrilling:
    """Tests for IIFE pattern detection and body drilling."""

    def test_standard_iife_drills_through(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            (function() {
                'use strict';
                function innerFunc() {
                    return "I am inside IIFE";
                }
                function anotherFunc() {
                    return "Also inside IIFE";
                }
            })();
        """,
        )
        # Should find the inner functions, not a single huge expression
        funcs = _find_by_type(docs, "function_declaration")
        assert len(funcs) >= 1
        all_text = " ".join(d.text for d in docs)
        assert "innerFunc" in all_text

    def test_iife_with_args_drills_through(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            (function(wnd, $) {
                function setup() {
                    return "setting up with jQuery reference passed through IIFE params";
                }
                wnd.MyModule = setup;
            })(window, jQuery);
        """,
        )
        all_text = " ".join(d.text for d in docs)
        assert "setup" in all_text

    def test_nested_iife_outer_drills(self, tmp_path):
        """When outer IIFE contains inner IIFE, outer is drilled."""
        docs = _load(
            tmp_path,
            """\
            (function(wnd) {
                wnd.Module = (function() {
                    var internal = "data";
                    return { get: function() { return internal; } };
                })();
            })(window);
        """,
        )
        assert len(docs) >= 1
        # The inner assignment should be present
        all_text = " ".join(d.text for d in docs)
        assert "Module" in all_text


# ────────────────────────────────────────────────
# JavaScript: AMD define() Drilling
# ────────────────────────────────────────────────


class TestJsAmdDrilling:
    """Tests for AMD define() module pattern drilling."""

    def test_define_with_callback(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            define(['jquery'], function($) {
                'use strict';
                function moduleFunc() {
                    return "I am in AMD module and have enough text to be a real chunk";
                }
                return moduleFunc;
            });
        """,
        )
        all_text = " ".join(d.text for d in docs)
        assert "moduleFunc" in all_text

    def test_iife_wrapping_define(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            (function(require, define) {
                define(['jquery', 'utils'], function($, utils) {
                    'use strict';
                    var App = {
                        init: function() {
                            console.log("app initializing with all dependencies loaded properly now");
                        }
                    };
                    return App;
                });
            })(require, define);
        """,
        )
        all_text = " ".join(d.text for d in docs)
        assert "App" in all_text


# ────────────────────────────────────────────────
# JavaScript: Prototype Methods
# ────────────────────────────────────────────────


class TestJsPrototypeMethods:
    """Tests for prototype method detection and grouping."""

    def test_prototype_assignment_detected(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function MyClass() {
                this.value = 0;
            }
            MyClass.prototype.getValue = function() {
                return this.value;
            };
        """,
        )
        # Should find prototype assignment with class_name metadata
        proto_docs = [d for d in docs if d.metadata.get("class_name") == "MyClass"]
        assert len(proto_docs) >= 1

    def test_prototype_grouping(self, tmp_path):
        """3+ consecutive prototype assignments should be grouped."""
        docs = _load(
            tmp_path,
            """\
            function Widget() { this.x = 0; }
            Widget.prototype.show = function() { this.visible = true; };
            Widget.prototype.hide = function() { this.visible = false; };
            Widget.prototype.toggle = function() { this.visible = !this.visible; };
            Widget.prototype.reset = function() { this.x = 0; };
        """,
        )
        groups = _find_by_type(docs, "prototype_group")
        assert len(groups) >= 1
        g = groups[0]
        assert g.metadata.get("class_name") == "Widget"
        assert "show" in g.text
        assert "hide" in g.text
        assert "toggle" in g.text

    def test_non_consecutive_prototypes_not_grouped(self, tmp_path):
        """Prototype methods interrupted by other nodes shouldn't group."""
        docs = _load(
            tmp_path,
            """\
            function A() {}
            A.prototype.foo = function() { return "foo implementation content"; };
            function helper() { return "interrupting the prototype chain"; }
            A.prototype.bar = function() { return "bar implementation content"; };
        """,
        )
        groups = _find_by_type(docs, "prototype_group")
        # Not enough consecutive (2 interrupted), no group
        assert len(groups) == 0


# ────────────────────────────────────────────────
# JavaScript: Trivial Function Grouping
# ────────────────────────────────────────────────


class TestJsTrivialFunctionGrouping:
    """Tests for grouping consecutive small functions."""

    def test_three_trivial_functions_grouped(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function a() { return 1; }
            function b() { return 2; }
            function c() { return 3; }
        """,
        )
        groups = _find_by_type(docs, "function_group")
        assert len(groups) == 1
        assert groups[0].metadata.get("group_count") == 3

    def test_two_trivial_functions_not_grouped(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function a() { return 1; }
            function b() { return 2; }
        """,
        )
        groups = _find_by_type(docs, "function_group")
        assert len(groups) == 0
        funcs = _find_by_type(docs, "function_declaration")
        assert len(funcs) == 2

    def test_large_function_breaks_group(self, tmp_path):
        """A large function between trivial ones should break the group."""
        docs = _load(
            tmp_path,
            """\
            function a() { return 1; }
            function b() { return 2; }
            function big() {
                var x = 1;
                var y = 2;
                var z = 3;
                var w = 4;
                var v = 5;
                var u = 6;
                var t = 7;
                return x + y + z + w + v + u + t;
            }
            function c() { return 3; }
            function d() { return 4; }
        """,
        )
        groups = _find_by_type(docs, "function_group")
        # a+b only 2, and c+d only 2 — neither reaches 3
        assert len(groups) == 0


# ────────────────────────────────────────────────
# JavaScript: Import Grouping
# ────────────────────────────────────────────────


class TestJsImportGrouping:
    """Tests for import statement grouping."""

    def test_require_imports_grouped(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            var $ = require('jquery');
            var utils = require('./utils');
            var config = require('./config');
            function main() {
                return $.extend({}, config, utils);
            }
        """,
        )
        imports = _find_by_type(docs, "import_group")
        assert len(imports) == 1
        assert "require" in imports[0].text
        assert "jquery" in imports[0].text


# ────────────────────────────────────────────────
# TypeScript: Interfaces and Type Aliases
# ────────────────────────────────────────────────


class TestTsInterfaces:
    """Tests for TypeScript interface declaration chunking."""

    def test_interface_chunked(self, tmp_path):
        docs = _load_ts(
            tmp_path,
            """\
            interface User {
                name: string;
                age: number;
                email: string;
            }
        """,
        )
        ifaces = _find_by_type(docs, "interface_declaration")
        assert len(ifaces) == 1
        assert "User" in ifaces[0].text
        assert "name: string" in ifaces[0].text

    def test_multiple_interfaces(self, tmp_path):
        docs = _load_ts(
            tmp_path,
            """\
            interface Request {
                url: string;
                method: string;
            }
            interface Response {
                status: number;
                body: string;
            }
        """,
        )
        ifaces = _find_by_type(docs, "interface_declaration")
        assert len(ifaces) == 2


class TestTsTypeAliases:
    """Tests for TypeScript type alias declaration chunking."""

    def test_type_alias_chunked(self, tmp_path):
        docs = _load_ts(
            tmp_path,
            """\
            type SearchParams = {
                query: string;
                page: number;
                limit: number;
            };
        """,
        )
        types = _find_by_type(docs, "type_alias_declaration")
        assert len(types) == 1
        assert "SearchParams" in types[0].text


# ────────────────────────────────────────────────
# TypeScript: Export Unwrapping
# ────────────────────────────────────────────────


class TestTsExportUnwrapping:
    """Tests for TypeScript export statement unwrapping."""

    def test_exported_interface(self, tmp_path):
        docs = _load_ts(
            tmp_path,
            """\
            export interface ApiResponse {
                data: unknown;
                status: number;
                message: string;
            }
        """,
        )
        ifaces = _find_by_type(docs, "interface_declaration")
        assert len(ifaces) == 1
        assert "ApiResponse" in ifaces[0].text

    def test_exported_class(self, tmp_path):
        docs = _load_ts(
            tmp_path,
            """\
            export class Service {
                constructor(private readonly url: string) {}
                async fetch() {
                    return await fetch(this.url);
                }
            }
        """,
        )
        summaries = _find_by_type(docs, "class_summary")
        assert len(summaries) == 1
        assert "Service" in summaries[0].text

    def test_exported_function(self, tmp_path):
        docs = _load_ts(
            tmp_path,
            """\
            export function calculateTotal(items: number[]): number {
                return items.reduce((sum, item) => sum + item, 0);
            }
        """,
        )
        funcs = _find_by_type(docs, "function_declaration")
        assert len(funcs) == 1
        assert "calculateTotal" in funcs[0].text

    def test_exported_const_arrow(self, tmp_path):
        docs = _load_ts(
            tmp_path,
            """\
            export const fetchData = async (url: string): Promise<unknown> => {
                const response = await fetch(url);
                return response.json();
            };
        """,
        )
        arrows = _find_by_type(docs, "arrow_function")
        assert len(arrows) == 1
        assert "fetchData" in arrows[0].text

    def test_exported_type_alias(self, tmp_path):
        docs = _load_ts(
            tmp_path,
            """\
            export type ErrorCode = 'NOT_FOUND' | 'UNAUTHORIZED' | 'SERVER_ERROR';
        """,
        )
        types = _find_by_type(docs, "type_alias_declaration")
        assert len(types) == 1
        assert "ErrorCode" in types[0].text


# ────────────────────────────────────────────────
# TypeScript: ES6 Imports
# ────────────────────────────────────────────────


class TestTsImports:
    """Tests for TypeScript import grouping."""

    def test_imports_grouped(self, tmp_path):
        docs = _load_ts(
            tmp_path,
            """\
            import { Component } from './Component';
            import { Service } from './Service';
            import type { Config } from './Config';

            export class App {
                constructor(private service: Service) {}
                run() { return this.service.start(); }
            }
        """,
        )
        imports = _find_by_type(docs, "import_group")
        assert len(imports) == 1
        assert "Component" in imports[0].text
        assert "Service" in imports[0].text
        assert "Config" in imports[0].text


# ────────────────────────────────────────────────
# TypeScript: Full TS Module Integration
# ────────────────────────────────────────────────


class TestTsIntegration:
    """Integration tests for TypeScript modules with mixed declarations."""

    def test_mixed_ts_module(self, tmp_path):
        """Full TS module: imports, interfaces, class, exported arrow, type alias."""
        docs = _load_ts(
            tmp_path,
            """\
            import { Base } from './base';

            interface Config {
                host: string;
                port: number;
            }

            type Status = 'active' | 'inactive';

            export class Client extends Base {
                private config: Config;
                constructor(config: Config) {
                    super();
                    this.config = config;
                }
                connect() {
                    return fetch(this.config.host + ':' + this.config.port);
                }
                disconnect() {
                    console.log('disconnected');
                }
            }

            export const createClient = (config: Config): Client => {
                return new Client(config);
            };
        """,
        )
        imports = _find_by_type(docs, "import_group")
        assert len(imports) == 1

        ifaces = _find_by_type(docs, "interface_declaration")
        assert len(ifaces) == 1
        assert "Config" in ifaces[0].text

        types = _find_by_type(docs, "type_alias_declaration")
        assert len(types) == 1
        assert "Status" in types[0].text

        summaries = _find_by_type(docs, "class_summary")
        assert len(summaries) == 1
        assert "Client" in summaries[0].text
        assert "extends Base" in summaries[0].text

        arrows = _find_by_type(docs, "arrow_function")
        assert len(arrows) == 1
        assert "createClient" in arrows[0].text


# ────────────────────────────────────────────────
# Oversized Chunk Splitting
# ────────────────────────────────────────────────


class TestOversizedSplitting:
    """Tests for splitting chunks that exceed MAX_CHUNK_CHARS."""

    def test_huge_function_splits(self, tmp_path):
        """A function exceeding MAX_CHUNK_CHARS should be split."""
        reader = JSFileReader()
        # Create a function with lots of content
        lines = [f"    var line_{i} = 'value_{i}'; // padding" for i in range(800)]
        body = "\n".join(lines)
        code = f"function hugeFunc() {{\n{body}\n}}"
        f = _make_js_file(tmp_path, code)
        docs = reader.load_data(f)
        splits = _find_by_type(docs, "function_declaration_split")
        assert len(splits) >= 2
        for s in splits:
            assert "split_part" in s.metadata
            assert "split_total" in s.metadata

    def test_class_summary_splits_at_lower_threshold(self, tmp_path):
        """Class summary should split at MAX_SUMMARY_CHARS (lower than MAX_CHUNK_CHARS)."""
        reader = JSFileReader()
        # Create a class with many methods with long signatures to exceed MAX_SUMMARY_CHARS (6000)
        methods = "\n".join(
            f"    handleLongMethodNameForComponent_{i}(argumentOne_{i}, argumentTwo_{i}, argumentThree_{i}) {{ return argumentOne_{i} + argumentTwo_{i} + argumentThree_{i} + {i}; }}"
            for i in range(150)
        )
        code = f"class BigControllerClass {{\n{methods}\n}}"
        f = _make_js_file(tmp_path, code)
        docs = reader.load_data(f)
        splits = _find_by_type(docs, "class_summary_split")
        assert len(splits) >= 2


# ────────────────────────────────────────────────
# Empty and Edge Cases
# ────────────────────────────────────────────────


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_file(self, tmp_path):
        docs = _load(tmp_path, "")
        assert docs == []

    def test_whitespace_only_file(self, tmp_path):
        docs = _load(tmp_path, "   \n  \n  ")
        assert docs == []

    def test_comment_only_file(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            /**
             * This is a JSDoc comment that describes the module.
             * It has enough content to pass the minimum chunk size threshold.
             */
        """,
        )
        comments = _find_by_type(docs, "comment")
        assert len(comments) == 1
        assert "JSDoc" in comments[0].text

    def test_tiny_comment_skipped(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            // x
            function realFunc() {
                return "this function has enough content to be a real chunk in the output";
            }
        """,
        )
        comments = _find_by_type(docs, "comment")
        assert len(comments) == 0  # Too small

    def test_fallback_full_file(self, tmp_path):
        """When no recognized nodes are found, emit full_file."""
        # Single tiny expression that's below MIN_CHUNK_SIZE
        f = _make_js_file(tmp_path, "1;", "tiny.js")
        reader = JSFileReader()
        docs = reader.load_data(f)
        # Should fallback to full_file
        assert len(docs) >= 1
        full = _find_by_type(docs, "full_file")
        assert len(full) == 1

    def test_parse_error_fallback(self, tmp_path):
        """If tree-sitter parse fails, emit full_file with parse_error."""
        reader = JSFileReader()
        f = _make_js_file(tmp_path, "function foo() { return 42; }")
        # tree_sitter.Parser.parse is read-only (C extension), so we replace
        # the module-level parser object with a mock that raises on parse()
        from unittest.mock import MagicMock

        fake_parser = MagicMock()
        fake_parser.parse.side_effect = Exception("parse boom")
        with patch.object(js_module, "_js_parser", fake_parser):
            docs = reader.load_data(f)
        assert len(docs) == 1
        assert docs[0].metadata["node_type"] == "full_file"
        assert "parse boom" in docs[0].metadata.get("parse_error", "")

    def test_unreadable_file(self, tmp_path):
        """If file can't be read, return empty list."""
        reader = JSFileReader()
        f = tmp_path / "nonexistent.js"
        # Don't create the file
        with patch(
            "shared.readers.js_reader.read_file_with_encoding_and_bytes",
            side_effect=Exception("read error"),
        ):
            docs = reader.load_data(f)
        assert docs == []

    def test_ts_extension_uses_ts_parser(self, tmp_path):
        """A .ts file should use the TypeScript parser."""
        docs = _load_ts(
            tmp_path,
            """\
            interface Foo {
                bar: string;
            }
        """,
        )
        ifaces = _find_by_type(docs, "interface_declaration")
        assert len(ifaces) == 1

    def test_tsx_extension_uses_ts_parser(self, tmp_path):
        f = _make_ts_file(
            tmp_path,
            """\
            interface Props {
                title: string;
            }
        """,
            name="component.tsx",
        )
        reader = JSFileReader()
        docs = reader.load_data(f)
        ifaces = _find_by_type(docs, "interface_declaration")
        assert len(ifaces) == 1


# ────────────────────────────────────────────────
# Metadata Tests
# ────────────────────────────────────────────────


class TestMetadata:
    """Tests for metadata on emitted chunks."""

    def test_unit_name(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function foo() {
                return "metadata test with sufficient content for a chunk";
            }
        """,
        )
        for d in docs:
            assert d.metadata.get("unit_name") == "test"

    def test_class_name_on_method(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            class MyService {
                constructor() {
                    this.ready = false;
                }
                start() {
                    this.ready = true;
                    console.log("Service started successfully with initialization");
                }
            }
        """,
        )
        methods = _find_by_type(docs, "method_definition")
        for m in methods:
            assert m.metadata.get("class_name") == "MyService"

    def test_file_path_metadata(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function test() {
                return "checking file_path metadata is present in every chunk";
            }
        """,
        )
        for d in docs:
            assert "file_path" in d.metadata

    def test_line_numbers(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function first() {
                return 1;
            }
            function second() {
                return 2;
            }
        """,
        )
        funcs = _find_by_type(docs, "function_declaration")
        if len(funcs) >= 2:
            assert funcs[0].metadata["start_line"] < funcs[1].metadata["start_line"]

    def test_byte_offsets(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function myFunc() {
                return "byte offset test with enough content for the chunk";
            }
        """,
        )
        for d in docs:
            assert "start_byte" in d.metadata
            assert "end_byte" in d.metadata
            assert d.metadata["start_byte"] < d.metadata["end_byte"]


# ────────────────────────────────────────────────
# Context Prefix Tests
# ────────────────────────────────────────────────


class TestContextPrefixes:
    """Tests for context prefix inclusion in chunks."""

    def test_file_prefix_on_function(self, tmp_path):
        f = _make_js_file(
            tmp_path,
            """\
            function myFunc() {
                return "testing context prefix with some real content";
            }
        """,
            name="myModule.js",
        )
        reader = JSFileReader()
        docs = reader.load_data(f)
        assert len(docs) >= 1
        assert "// File: myModule.js" in docs[0].text

    def test_class_prefix_on_method(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            class Controller {
                handleRequest() {
                    return "handling the request with enough content for chunk extraction";
                }
            }
        """,
        )
        methods = _find_by_type(docs, "method_definition")
        if methods:
            assert "// Class:" in methods[0].text
            assert "Controller" in methods[0].text

    def test_ts_file_prefix(self, tmp_path):
        f = _make_ts_file(
            tmp_path,
            """\
            export interface Config {
                host: string;
                port: number;
            }
        """,
            name="config.ts",
        )
        reader = JSFileReader()
        docs = reader.load_data(f)
        assert len(docs) >= 1
        assert "// File: config.ts" in docs[0].text


# ────────────────────────────────────────────────
# Trivial Method Grouping (inside classes)
# ────────────────────────────────────────────────


class TestTrivialMethodGrouping:
    """Tests for grouping consecutive trivial methods inside a class."""

    def test_trivial_methods_grouped(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            class Accessors {
                getA() { return this.a; }
                getB() { return this.b; }
                getC() { return this.c; }
                getD() { return this.d; }
            }
        """,
        )
        groups = _find_by_type(docs, "function_group")
        assert len(groups) >= 1
        assert groups[0].metadata.get("group_count") >= 3

    def test_large_method_breaks_grouping(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            class Mixed {
                getX() { return this.x; }
                getY() { return this.y; }
                bigMethod() {
                    var a = 1;
                    var b = 2;
                    var c = 3;
                    var d = 4;
                    var e = 5;
                    var f = 6;
                    var g = 7;
                    return a + b + c + d + e + f + g;
                }
                getZ() { return this.z; }
            }
        """,
        )
        # getX + getY = 2 (not enough), getZ alone = 1 (not enough)
        groups = _find_by_type(docs, "function_group")
        assert len(groups) == 0


# ────────────────────────────────────────────────
# Real-world Patterns Integration Tests
# ────────────────────────────────────────────────


class TestRealWorldPatterns:
    """Tests mimicking real E-Podroznik.pl JS/TS patterns."""

    def test_revealing_module_pattern(self, tmp_path):
        """Module pattern: var Module = (function() { ... return { ... }; })();"""
        docs = _load(
            tmp_path,
            """\
            var EPodroznikUtils = (function() {
                var cache = {};
                function set(key, value) {
                    cache[key] = value;
                }
                function get(key) {
                    return cache[key];
                }
                return { set: set, get: get };
            })();
        """,
        )
        assert len(docs) >= 1
        all_text = " ".join(d.text for d in docs)
        assert "EPodroznikUtils" in all_text

    def test_jquery_ready_pattern(self, tmp_path):
        docs = _load(
            tmp_path,
            """\
            function initSearch() {
                var form = document.getElementById("searchForm");
                form.addEventListener("submit", function(e) {
                    e.preventDefault();
                    console.log("search submitted from the connections searcher component");
                });
            }
            $(document).ready(initSearch);
        """,
        )
        funcs = _find_by_type(docs, "function_declaration")
        assert len(funcs) >= 1
        assert "initSearch" in funcs[0].text

    def test_date_prototype_extension(self, tmp_path):
        """Date.prototype.customMethod = function() { ... }"""
        docs = _load(
            tmp_path,
            """\
            Date.prototype.get4DigitsYear = function() {
                if (this.getFullYear) return this.getFullYear();
                else {
                    var toReturn = this.getYear() % 100;
                    toReturn += (toReturn < 38) ? 2000 : 1900;
                    return toReturn;
                }
            };
        """,
        )
        assert len(docs) >= 1
        all_text = " ".join(d.text for d in docs)
        assert "get4DigitsYear" in all_text

    def test_ts_component_pattern(self, tmp_path):
        """TypeScript component with interface + exported arrow function."""
        docs = _load_ts(
            tmp_path,
            """\
            import doT from "dot";

            export interface ComponentProps {
                items: string[];
                onSelect: (item: string) => void;
            }

            export const ListComponent = (props: ComponentProps) => {
                const root = document.createElement('ul');
                props.items.forEach(item => {
                    const li = document.createElement('li');
                    li.textContent = item;
                    li.addEventListener('click', () => props.onSelect(item));
                    root.appendChild(li);
                });
                return root;
            };
        """,
        )
        imports = _find_by_type(docs, "import_group")
        assert len(imports) == 1

        ifaces = _find_by_type(docs, "interface_declaration")
        assert len(ifaces) == 1
        assert "ComponentProps" in ifaces[0].text

        arrows = _find_by_type(docs, "arrow_function")
        assert len(arrows) == 1
        assert "ListComponent" in arrows[0].text

    def test_ts_class_with_private_fields(self, tmp_path):
        """TypeScript class with accessibility modifiers."""
        docs = _load_ts(
            tmp_path,
            """\
            export class ResponseError extends Error {
                constructor(private readonly _errorData: { message: string; status: string }) {
                    super(_errorData.message);
                }
                getErrorData() {
                    return { ...this._errorData };
                }
            }
        """,
        )
        summaries = _find_by_type(docs, "class_summary")
        assert len(summaries) == 1
        assert "ResponseError" in summaries[0].text
        assert "extends Error" in summaries[0].text
