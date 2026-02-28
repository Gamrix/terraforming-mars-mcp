from __future__ import annotations

import sys
from pathlib import Path

# Make terraforming_mars_mcp importable without installing the package.
# pyproject.toml sets [tool.uv] package = false, so the package is not
# installed into the venv.  Inserting the repo root here lets every test
# file use plain `import terraforming_mars_mcp.*` statements.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
