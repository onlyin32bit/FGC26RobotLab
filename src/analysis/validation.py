"""Validate time-series data before plotting or calculating metrics."""

from collections.abc import Iterable

import pandas as pd

REQUIRED_COLUMNS = {
    "run_id",
    "time_s",
    "forward_requested",
    "forward_limited",
    "heading_deg",
    "heading_error_deg",
    "left_target_tps",
    "left_actual_tps",
    "right_target_tps",
    "right_actual_tps",
    "battery_v",
}


def _add_issue(issues: list[dict[str, str]], level: str, message: str) -> None:
    issues.append({"muc_do": level, "noi_dung": message})


def validate_data(
    data: pd.DataFrame,
    required_columns: Iterable[str] = REQUIRED_COLUMNS,
) -> pd.DataFrame:
    """Return data-quality findings in Vietnamese for notebook display."""

    issues: list[dict[str, str]] = []
    if data.empty:
        _add_issue(issues, "THÔNG TIN", "Chưa tìm thấy CSV cho kịch bản này.")
        return pd.DataFrame(issues)

    missing = sorted(set(required_columns) - set(data.columns))
    if missing:
        _add_issue(issues, "LỖI", f"Thiếu cột bắt buộc: {', '.join(missing)}")
    if data.isna().all(axis=0).any():
        empty_columns = ", ".join(data.columns[data.isna().all(axis=0)])
        _add_issue(issues, "CẢNH BÁO", f"Các cột hoàn toàn rỗng: {empty_columns}")
    if {"run_id", "sample"}.issubset(data.columns):
        duplicates = int(data.duplicated(["run_id", "sample"]).sum())
        if duplicates:
            _add_issue(issues, "LỖI", f"Có {duplicates} mẫu trùng run_id và sample.")
    if {"run_id", "time_s"}.issubset(data.columns):
        for run_id, run in data.groupby("run_id", sort=False):
            time = pd.to_numeric(run["time_s"], errors="coerce")
            if time.isna().any():
                _add_issue(issues, "LỖI", f"{run_id}: time_s có giá trị không phải số.")
            elif (time.diff().dropna() <= 0).any():
                _add_issue(issues, "LỖI", f"{run_id}: time_s không tăng nghiêm ngặt.")
    if "battery_v" in data:
        voltage = pd.to_numeric(data["battery_v"], errors="coerce")
        outside_range = voltage.notna() & ~voltage.between(6.0, 16.0)
        if outside_range.any():
            _add_issue(
                issues,
                "CẢNH BÁO",
                f"Có {int(outside_range.sum())} mẫu điện áp ngoài miền 6–16 V.",
            )
    if "loop_dt_ms" in data:
        loop_time = pd.to_numeric(data["loop_dt_ms"], errors="coerce")
        if (loop_time < 0).any():
            _add_issue(issues, "LỖI", "loop_dt_ms có giá trị âm.")
        if (loop_time > 100).any():
            _add_issue(
                issues,
                "CẢNH BÁO",
                f"Có {int((loop_time > 100).sum())} vòng lặp dài hơn 100 ms.",
            )
    if "event" in data:
        events = set(data["event"].dropna().astype(str))
        if "RUN_START" not in events:
            _add_issue(issues, "CẢNH BÁO", "Không tìm thấy mốc RUN_START.")
        if "RUN_END" not in events:
            _add_issue(issues, "CẢNH BÁO", "Không tìm thấy mốc RUN_END.")
    if not issues:
        _add_issue(issues, "ĐẠT", "Chưa phát hiện lỗi theo các quy tắc hiện tại.")
    return pd.DataFrame(issues)
