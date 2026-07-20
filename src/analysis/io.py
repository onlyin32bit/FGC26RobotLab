"""Load CSV data without changing the original files."""

from pathlib import Path

import pandas as pd


def load_runs(directory: str | Path, pattern: str = "*.csv") -> pd.DataFrame:
    """Load and combine all run CSV files in one test directory."""

    path = Path(directory)
    files = sorted(path.glob(pattern))
    if not files:
        return pd.DataFrame()

    frames: list[pd.DataFrame] = []
    for file in files:
        frame = pd.read_csv(file)
        if "run_id" not in frame.columns:
            frame.insert(0, "run_id", file.stem)
        frame["source_file"] = file.name
        frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False)


def load_summary(file: str | Path) -> pd.DataFrame:
    """Load the optional run-summary CSV."""

    path = Path(file)
    return pd.read_csv(path) if path.exists() else pd.DataFrame()
