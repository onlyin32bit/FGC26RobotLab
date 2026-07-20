"""Shared numerical metrics for drivetrain experiments."""

from collections.abc import Iterable

import numpy as np
import pandas as pd


def _finite(values: Iterable[float]) -> np.ndarray:
    array = np.asarray(list(values), dtype=float)
    return array[np.isfinite(array)]


def rmse(values: Iterable[float]) -> float:
    """Return the root mean square of finite values."""

    array = _finite(values)
    return float("nan") if array.size == 0 else float(np.sqrt(np.mean(np.square(array))))


def error_rmse(actual: Iterable[float], target: Iterable[float]) -> float:
    """Return the RMSE between actual and target values."""

    actual_array = np.asarray(list(actual), dtype=float)
    target_array = np.asarray(list(target), dtype=float)
    valid = np.isfinite(actual_array) & np.isfinite(target_array)
    return float("nan") if not valid.any() else rmse(actual_array[valid] - target_array[valid])


def lateral_error_mm_per_m(lateral_mm: float, distance_mm: float) -> float:
    """Normalize lateral offset by travelled distance."""

    return float("nan") if distance_mm == 0 else abs(lateral_mm) / abs(distance_mm) * 1_000.0


def voltage_sag(voltage: Iterable[float]) -> float:
    """Return the initial-to-minimum voltage drop."""

    array = _finite(voltage)
    return float("nan") if array.size == 0 else float(array[0] - np.min(array))


def rise_time_10_90(
    time_s: Iterable[float],
    signal: Iterable[float],
    final_value: float | None = None,
) -> float:
    """Measure the first 10-to-90 percent rise time."""

    time = np.asarray(list(time_s), dtype=float)
    values = np.abs(np.asarray(list(signal), dtype=float))
    valid = np.isfinite(time) & np.isfinite(values)
    time, values = time[valid], values[valid]
    if time.size < 2:
        return float("nan")

    final = abs(final_value) if final_value is not None else float(np.median(values[-5:]))
    if final <= 0:
        return float("nan")

    first_10 = np.flatnonzero(values >= 0.1 * final)
    first_90 = np.flatnonzero(values >= 0.9 * final)
    if first_10.size == 0 or first_90.size == 0:
        return float("nan")

    start = int(first_10[0])
    candidates = first_90[first_90 >= start]
    return float("nan") if candidates.size == 0 else float(time[int(candidates[0])] - time[start])


def settling_time(
    time_s: Iterable[float],
    error: Iterable[float],
    tolerance: float,
    hold_s: float = 0.5,
) -> float:
    """Return the first time error stays within tolerance long enough."""

    time = np.asarray(list(time_s), dtype=float)
    values = np.abs(np.asarray(list(error), dtype=float))
    valid = np.isfinite(time) & np.isfinite(values)
    time, values = time[valid], values[valid]
    if time.size < 2:
        return float("nan")

    within = values <= abs(tolerance)
    for start in np.flatnonzero(within):
        stop = np.searchsorted(time, time[start] + hold_s, side="left")
        if stop < time.size and within[start : stop + 1].all():
            return float(time[start] - time[0])
    return float("nan")


def summarize_runs(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate common metrics for every run in a time-series table."""

    if data.empty or "run_id" not in data:
        return pd.DataFrame()

    rows: list[dict[str, float | str]] = []
    for run_id, run in data.groupby("run_id", sort=False):
        row: dict[str, float | str] = {"run_id": str(run_id)}
        if "heading_error_deg" in run:
            error = pd.to_numeric(run["heading_error_deg"], errors="coerce")
            row["heading_rmse_deg"] = rmse(error)
            row["heading_max_abs_deg"] = float(error.abs().max())
        for actual, target, name in (
            ("left_actual_tps", "left_target_tps", "left_velocity_rmse_tps"),
            ("right_actual_tps", "right_target_tps", "right_velocity_rmse_tps"),
        ):
            if {actual, target}.issubset(run.columns):
                row[name] = error_rmse(run[actual], run[target])
        if "battery_v" in run:
            voltage = pd.to_numeric(run["battery_v"], errors="coerce")
            row["battery_min_v"] = float(voltage.min())
            row["battery_sag_v"] = voltage_sag(voltage)
        if "loop_dt_ms" in run:
            loop_time = pd.to_numeric(run["loop_dt_ms"], errors="coerce")
            row["loop_p95_ms"] = float(loop_time.quantile(0.95))
            row["loop_max_ms"] = float(loop_time.max())
        rows.append(row)
    return pd.DataFrame(rows)
