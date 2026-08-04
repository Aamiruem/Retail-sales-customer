"""Execute controlled pure-Python notebook cells without an external Jupyter dependency."""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import traceback
from pathlib import Path


def execute(notebook_path: Path) -> None:
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__"}
    execution_count = 0
    original_cwd = Path.cwd()
    project_root = notebook_path.resolve().parents[1]
    os.chdir(project_root)
    try:
        for cell_index, cell in enumerate(notebook["cells"]):
            if cell.get("cell_type") != "code":
                continue
            execution_count += 1
            source = "".join(cell.get("source", []))
            stdout = io.StringIO()
            stderr = io.StringIO()
            outputs = []
            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exec(compile(source, f"{notebook_path.name}:cell_{cell_index}", "exec"), namespace)
            except Exception as exc:
                outputs.append(
                    {
                        "output_type": "error",
                        "ename": type(exc).__name__,
                        "evalue": str(exc),
                        "traceback": traceback.format_exc().splitlines(),
                    }
                )
                cell["outputs"] = outputs
                cell["execution_count"] = execution_count
                notebook_path.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
                raise
            if stdout.getvalue():
                outputs.append({"output_type": "stream", "name": "stdout", "text": stdout.getvalue().splitlines(keepends=True)})
            if stderr.getvalue():
                outputs.append({"output_type": "stream", "name": "stderr", "text": stderr.getvalue().splitlines(keepends=True)})
            cell["outputs"] = outputs
            cell["execution_count"] = execution_count
    finally:
        os.chdir(original_cwd)
    notebook_path.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(f"Executed {execution_count} code cells successfully: {notebook_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/execute_notebook.py path/to/notebook.ipynb")
    execute(Path(sys.argv[1]))

