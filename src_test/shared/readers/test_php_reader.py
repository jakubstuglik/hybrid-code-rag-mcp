"""
Tests for shared/readers/php_reader.py - PHP reader with Tree-sitter AST.

Covers: registry wiring (.php, Blade/.phtml as text), ``// File /
// Namespace / // Class`` prefix, statement and block namespaces, classes,
interfaces, traits, enums, methods/constructors/properties/constants,
doc blocks, use imports, trivial-method grouping, top-level functions,
script bodies, template fallback to text chunks and class_overview.
"""

from pathlib import Path

from shared.readers import READER_REGISTRY, get_reader
from shared.readers.php_reader import PHPFileReader
from shared.readers.text_reader import TextFileReader

SAMPLE = """<?php
declare(strict_types=1);

namespace App\\Http\\Controllers;

use App\\Models\\User;
use Illuminate\\Http\\{Request, Response};

/**
 * Manages users.
 */
#[Middleware('auth')]
final class UserController extends Controller implements HasMiddleware
{
    use AuthorizesRequests;

    public const PER_PAGE = 20;
    private array $cache = [];

    public function __construct(private UserRepository $users) {}

    /**
     * List users.
     */
    public function index(Request $request): Response
    {
        $page = (int) $request->query('page', 1);
        $users = $this->users->paginate(self::PER_PAGE, $page);
        foreach ($users as $user) {
            $this->cache[$user->id] = $user;
        }
        return response()->json($users);
    }

    public function a(): int { return 1; }
    public function b(): int { return 2; }
    public function c(): int { return 3; }
}

interface HasMiddleware
{
    public function middleware(): array;
}

trait Loggable
{
    public function log(string $m): void { error_log($m); }
}

enum Status: string
{
    case Active = 'active';
    case Banned = 'banned';

    public function label(): string { return ucfirst($this->value); }
}

function helper(int $x): int
{
    return $x * 2;
}
"""


def _load(tmp_path, text, name="UserController.php"):
    f = tmp_path / name
    f.write_text(text, encoding="utf-8")
    return PHPFileReader().load_data(f)


def _types(docs, t):
    return [d for d in docs if d.metadata["node_type"] == t]


def _summary(docs, cls):
    return [d for d in _types(docs, "class_summary") if d.metadata["class_name"] == cls][0]


class TestRegistry:
    def test_php_registered(self):
        assert isinstance(READER_REGISTRY[".php"], PHPFileReader)

    def test_blade_and_phtml_are_text(self):
        assert isinstance(get_reader(Path("views/home.blade.php")), TextFileReader)
        assert isinstance(get_reader(Path("views/home.phtml")), TextFileReader)


class TestPrefix:
    def test_file_and_namespace(self, tmp_path):
        for d in _load(tmp_path, SAMPLE):
            assert d.text.startswith("// File: UserController.php\n// Namespace: App\\Http\\Controllers")

    def test_method_class_line(self, tmp_path):
        m = [d for d in _load(tmp_path, SAMPLE) if d.metadata.get("function_name") == "index"][0]
        assert "// Class: #[Middleware('auth')] final class UserController extends Controller implements HasMiddleware" in m.text
        assert m.metadata["class_name"] == "UserController"

    def test_block_namespace(self, tmp_path):
        docs = _load(tmp_path, "<?php\nnamespace Lib {\n    class Box { public function get() { return 1; } }\n}\n")
        assert _summary(docs, "Box").metadata["namespace"] == "Lib"


class TestTypes:
    def test_class_summary(self, tmp_path):
        s = _summary(_load(tmp_path, SAMPLE), "UserController").text
        assert "use AuthorizesRequests;" in s
        assert "public const PER_PAGE = 20;" in s
        assert "private array $cache = [];" in s
        assert "public function index(Request $request): Response" in s
        assert "paginate" not in s
        assert "Manages users." in s

    def test_interface_trait_enum(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        assert _summary(docs, "HasMiddleware").metadata["php_kind"] == "interface"
        assert _summary(docs, "Loggable").metadata["php_kind"] == "trait"
        e = _summary(docs, "Status").text
        assert "case Active = 'active';" in e and "public function label(): string" in e

    def test_large_class_overview(self, tmp_path):
        methods = "\n".join(
            f"    public function method{i}(int $alpha, int $beta, int $gamma): int {{ return $alpha + $beta + $gamma + {i}; }}"
            for i in range(120)
        )
        docs = _load(tmp_path, f"<?php\nnamespace N;\nabstract class Big extends Base {{\n{methods}\n}}\n")
        ov = _types(docs, "class_overview")
        assert ov and "Big is a PHP abstract class extends Base with 120 methods" in ov[0].text


class TestMembers:
    def test_member_types(self, tmp_path):
        docs = _load(tmp_path, SAMPLE)
        assert _types(docs, "constructor_declaration")[0].metadata["function_name"] == "__construct"
        assert "PER_PAGE" in _types(docs, "constant_declaration")[0].text
        assert "$cache" in _types(docs, "field_declaration")[0].text

    def test_doc_block_kept_with_method(self, tmp_path):
        m = [d for d in _load(tmp_path, SAMPLE) if d.metadata.get("function_name") == "index"][0]
        assert "List users." in m.text

    def test_trivial_methods_grouped(self, tmp_path):
        g = _types(_load(tmp_path, SAMPLE), "method_group")
        assert g and g[0].metadata["group_count"] == 3

    def test_top_level_function(self, tmp_path):
        f = [d for d in _load(tmp_path, SAMPLE) if d.metadata.get("function_name") == "helper"][0]
        assert f.metadata["node_type"] == "method_declaration" and "// Class:" not in f.text

    def test_use_imports_grouped(self, tmp_path):
        imp = _types(_load(tmp_path, SAMPLE), "import_group")
        assert len(imp) == 1 and "use App\\Models\\User;" in imp[0].text


class TestScriptsAndTemplates:
    def test_route_file_is_script_body(self, tmp_path):
        src = "<?php\nuse App\\Http\\Controllers\\UserController;\n\nRoute::get('/users', [UserController::class, 'index']);\nRoute::post('/users', [UserController::class, 'store']);\n"
        docs = _load(tmp_path, src, "web.php")
        assert "Route::post" in _types(docs, "script_body")[0].text

    def test_template_falls_back_to_text_chunks(self, tmp_path):
        src = "<html><body><h1>Users</h1>\n<ul>\n<?php foreach ($users as $u): ?>\n<li><?= htmlspecialchars($u->name) ?></li>\n<?php endforeach; ?>\n</ul>\n<p>Static footer text for the page that makes the template mostly HTML.</p>\n</body></html>\n"
        f = tmp_path / "list.php"
        f.write_text(src, encoding="utf-8")
        nodes = PHPFileReader().load_nodes(f)
        assert nodes and all(n.metadata["node_type"] == "full_file" for n in nodes)
        assert "php_template" not in nodes[0].metadata

    def test_empty(self, tmp_path):
        assert _load(tmp_path, "  \n") == []
