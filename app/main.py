"""Convenience entrypoint.

If you run this file directly (e.g. `python app/main.py`), Python sets the working
import root to `app/`, which can make `import app...` fail.

This entrypoint ensures the project root is on `sys.path` and then runs the
Streamlit UI module.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    runpy.run_module("app.ui.streamlit_app", run_name="__main__")


if __name__ == "__main__":
    main()