"""Validate time-series data before plotting or calculating metrics."""

from collections.abc import Iterable

import pandas as pd

from .schema import EVENT_NAMES, GLOBAL_TIME_SERIES_COLUMNS, TIME_SERIES_SCHEMA_VERSION

REQUIRED_COLUMNS = set(GLOBAL_TIME_SERIES_COLUMNS)


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
    if "schema_version" in data:
        versions = set(data["schema_version"].dropna().astype(str))
        if versions != {TIME_SERIES_SCHEMA_VERSION}:
            _add_issue(
                issues,
                "LỖI",
                "schema_version phải là "
                f"{TIME_SERIES_SCHEMA_VERSION}; nhận được {sorted(versions)}.",
            )
    extra_columns = set(data.columns) - set(GLOBAL_TIME_SERIES_COLUMNS) - {
        "source_file"
    }
    invalid_extensions = sorted(
        column for column in extra_columns if not column.startswith("scenario_")
    )
    if invalid_extensions:
        _add_issue(
            issues,
            "LỖI",
            "Cột mở rộng phải bắt đầu bằng scenario_: " + ", ".join(invalid_extensions),
        )
    expected_prefix = list(GLOBAL_TIME_SERIES_COLUMNS)
    if list(data.columns[: len(expected_prefix)]) != expected_prefix:
        _add_issue(
            issues,
            "LỖI",
            "Các cột global phải đứng đầu và theo đúng thứ tự master schema.",
        )
    if data.isna().all(axis=0).any():
        empty_columns = ", ".join(data.columns[data.isna().all(axis=0)])
        _add_issue(issues, "CẢNH BÁO", f"Các cột hoàn toàn rỗng: {empty_columns}")
    if {"run_id", "sample_index"}.issubset(data.columns):
        duplicates = int(data.duplicated(["run_id", "sample_index"]).sum())
        if duplicates:
            _add_issue(issues, "LỖI", f"Có {duplicates} mẫu trùng run_id và sample_index.")
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
        events = {
            token
            for value in data["event"].dropna().astype(str)
            for token in value.split("|")
            if token
        }
        unknown_events = sorted(events - EVENT_NAMES)
        if unknown_events:
            _add_issue(issues, "LỖI", "Event không thuộc master schema: " + ", ".join(unknown_events))
        if "LOG_START" not in events:
            _add_issue(issues, "LỖI", "Không tìm thấy event LOG_START.")
        terminal_events = events & {"END", "ABORT", "FAULT"}
        if len(terminal_events) != 1:
            _add_issue(issues, "LỖI", "Run phải có đúng một terminal event: END, ABORT hoặc FAULT.")
    if not issues:
        _add_issue(issues, "ĐẠT", "Chưa phát hiện lỗi theo các quy tắc hiện tại.")
    return pd.DataFrame(issues)
