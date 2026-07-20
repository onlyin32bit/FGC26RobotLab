"""Standard plots for drivetrain notebooks."""

from collections.abc import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def set_plot_style() -> None:
    """Apply a shared plotting style."""

    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.figsize": (11, 5),
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.frameon": True,
        }
    )


def _require_columns(data: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = sorted(set(columns) - set(data.columns))
    if missing:
        raise ValueError(f"Thiếu cột để vẽ biểu đồ: {', '.join(missing)}")


def plot_velocity(data: pd.DataFrame, title: str = "Theo dõi vận tốc drivetrain"):
    """Plot target and actual velocity for both sides."""

    _require_columns(
        data,
        ["time_s", "left_target_tps", "left_actual_tps", "right_target_tps", "right_actual_tps"],
    )
    figure, axis = plt.subplots()
    axis.plot(data["time_s"], data["left_target_tps"], "--", label="Trái mục tiêu")
    axis.plot(data["time_s"], data["left_actual_tps"], label="Trái thực tế")
    axis.plot(data["time_s"], data["right_target_tps"], "--", label="Phải mục tiêu")
    axis.plot(data["time_s"], data["right_actual_tps"], label="Phải thực tế")
    axis.set(title=title, xlabel="Thời gian (s)", ylabel="Vận tốc encoder (tick/s)")
    axis.legend(ncol=2)
    figure.tight_layout()
    return figure, axis


def plot_heading(data: pd.DataFrame, title: str = "Heading và sai số"):
    """Plot heading and heading error."""

    _require_columns(data, ["time_s", "heading_deg", "heading_error_deg"])
    figure, (heading_axis, error_axis) = plt.subplots(2, 1, sharex=True, figsize=(11, 7))
    heading_axis.plot(data["time_s"], data["heading_deg"], label="Heading thực tế")
    if "target_heading_deg" in data:
        heading_axis.plot(
            data["time_s"],
            data["target_heading_deg"],
            "--",
            label="Heading mục tiêu",
        )
    heading_axis.set(title=title, ylabel="Góc (độ)")
    heading_axis.legend()
    error_axis.plot(
        data["time_s"],
        data["heading_error_deg"],
        color="tab:red",
        label="Sai số heading",
    )
    error_axis.axhline(0, color="black", linewidth=0.8)
    error_axis.set(xlabel="Thời gian (s)", ylabel="Sai số (độ)")
    error_axis.legend()
    figure.tight_layout()
    return figure, (heading_axis, error_axis)


def plot_pid(data: pd.DataFrame, title: str = "Các thành phần hiệu chỉnh heading"):
    """Plot PID components."""

    columns = ["time_s", "heading_p", "heading_i", "heading_d", "heading_total"]
    _require_columns(data, columns)
    figure, axis = plt.subplots()
    labels = {"heading_p": "P", "heading_i": "I", "heading_d": "D", "heading_total": "Tổng"}
    for column, label in labels.items():
        axis.plot(data["time_s"], data[column], label=label)
    axis.set(title=title, xlabel="Thời gian (s)", ylabel="Hiệu chỉnh chuẩn hóa")
    axis.legend(ncol=4)
    figure.tight_layout()
    return figure, axis


def plot_power(data: pd.DataFrame, title: str = "Dòng điện và điện áp"):
    """Plot motor current and battery voltage."""

    _require_columns(data, ["time_s", "battery_v"])
    figure, current_axis = plt.subplots()
    if "left_current_a" in data:
        current_axis.plot(data["time_s"], data["left_current_a"], label="Dòng trái")
    if "right_current_a" in data:
        current_axis.plot(data["time_s"], data["right_current_a"], label="Dòng phải")
    current_axis.set(title=title, xlabel="Thời gian (s)", ylabel="Dòng điện (A)")
    voltage_axis = current_axis.twinx()
    voltage_axis.plot(
        data["time_s"],
        data["battery_v"],
        color="tab:green",
        alpha=0.75,
        label="Điện áp",
    )
    voltage_axis.set_ylabel("Điện áp (V)")
    lines = current_axis.lines + voltage_axis.lines
    current_axis.legend(lines, [line.get_label() for line in lines], loc="best")
    figure.tight_layout()
    return figure, (current_axis, voltage_axis)
