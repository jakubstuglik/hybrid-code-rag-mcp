# conftest.py — project root
# Ensures both the project root (for bare `import config`) and src/ (for
# `import shared`, `import qdrant`, `import config_loader`, etc.) are on
# sys.path for every pytest run and for direct `python src/...` invocations.

import sys
import types
from pathlib import Path

_root = Path(__file__).parent.resolve()
_src = _root / "src"

for _p in (_root, _src):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

# Reader tests import shared, which imports the HuggingFace embedding class.
# The class is not installed in a core-only environment. A stub keeps those
# tests collectable. A full environment already has the real module.
try:
    import llama_index.embeddings.huggingface  # noqa: F401
except ModuleNotFoundError:
    _hf = types.ModuleType("llama_index.embeddings.huggingface")

    class HuggingFaceEmbedding:  # pragma: no cover
        pass

    _hf.HuggingFaceEmbedding = HuggingFaceEmbedding
    sys.modules["llama_index.embeddings.huggingface"] = _hf
