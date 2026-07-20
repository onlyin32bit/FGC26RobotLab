"""Small notebook-facing helpers that keep experiment notebooks readable."""

import sys
from pathlib import Path

import pandas as pd
from IPython.display import Markdown, display

from .io import load_runs
from .plots import set_plot_style


def setup_notebook() -> Path:
    """Find the project root and configure imports and plotting."""

    root = Path.cwd().resolve()
    if root.name == "notebooks":
        root = root.parent
    src_path = str(root / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    set_plot_style()
    pd.set_option("display.max_columns", 100)
    return root


def load_test_data(root: Path, test_id: str, run_ids: list[str] | None = None) -> pd.DataFrame:
    """Load one test folder and optionally keep selected run IDs."""

    data = load_runs(root / "data" / "raw" / test_id)
    if run_ids and not data.empty:
        data = data[data["run_id"].isin(run_ids)].copy()
    return data


def show_full_data(data: pd.DataFrame) -> None:
    """Display the unmodified loaded data in a dedicated notebook section."""

    display(Markdown("## Dữ liệu đầy đủ"))
    if data.empty:
        display(Markdown("Chưa có CSV để hiển thị."))
    else:
        display(data)
