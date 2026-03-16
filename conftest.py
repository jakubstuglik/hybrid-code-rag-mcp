# conftest.py — project root
# Ensures both the project root (for bare `import config`) and src/ (for
# `import shared`, `import qdrant`, `import config_loader`, etc.) are on
# sys.path for every pytest run and for direct `python src/...` invocations.

import sys
from pathlib import Path

_root = Path(__file__).parent.resolve()
_src = _root / "src"

for _p in (_root, _src):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)
