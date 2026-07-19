"""Biểu đồ chuẩn có nhãn và đơn vị tiếng Việt."""

from collections.abc import Iterable

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def cai_dat_giao_dien() -> None:
    """Áp dụng giao diện thống nhất cho mọi notebook."""

    sns.set_theme(style="whitegrid", context="notebook")
    plt.rcParams.update(
        {
            "figure.figsize": (11, 5),
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.frameon": True,
        }
    )


def _kiem_tra_cot(du_lieu: pd.DataFrame, cac_cot: Iterable[str]) -> None:
    cot_thieu = sorted(set(cac_cot) - set(du_lieu.columns))
    if cot_thieu:
        raise ValueError(f"Thiếu cột để vẽ biểu đồ: {', '.join(cot_thieu)}")


def ve_van_toc(du_lieu: pd.DataFrame, tieu_de: str = "Theo dõi vận tốc drivetrain"):
    """Vẽ vận tốc mục tiêu và thực tế của hai bên."""

    cac_cot = [
        "time_s",
        "left_target_tps",
        "left_actual_tps",
        "right_target_tps",
        "right_actual_tps",
    ]
    _kiem_tra_cot(du_lieu, cac_cot)
    hinh, truc = plt.subplots()
    truc.plot(du_lieu["time_s"], du_lieu["left_target_tps"], "--", label="Trái mục tiêu")
    truc.plot(du_lieu["time_s"], du_lieu["left_actual_tps"], label="Trái thực tế")
    truc.plot(du_lieu["time_s"], du_lieu["right_target_tps"], "--", label="Phải mục tiêu")
    truc.plot(du_lieu["time_s"], du_lieu["right_actual_tps"], label="Phải thực tế")
    truc.set(title=tieu_de, xlabel="Thời gian (s)", ylabel="Vận tốc encoder (tick/s)")
    truc.legend(ncol=2)
    hinh.tight_layout()
    return hinh, truc


def ve_heading(du_lieu: pd.DataFrame, tieu_de: str = "Heading và sai số"):
    """Vẽ heading, heading mục tiêu và sai số."""

    _kiem_tra_cot(du_lieu, ["time_s", "heading_deg", "heading_error_deg"])
    hinh, (truc_heading, truc_sai_so) = plt.subplots(2, 1, sharex=True, figsize=(11, 7))
    truc_heading.plot(du_lieu["time_s"], du_lieu["heading_deg"], label="Heading thực tế")
    if "target_heading_deg" in du_lieu:
        truc_heading.plot(
            du_lieu["time_s"],
            du_lieu["target_heading_deg"],
            "--",
            label="Heading mục tiêu",
        )
    truc_heading.set(title=tieu_de, ylabel="Góc (độ)")
    truc_heading.legend()
    truc_sai_so.plot(
        du_lieu["time_s"],
        du_lieu["heading_error_deg"],
        color="tab:red",
        label="Sai số heading",
    )
    truc_sai_so.axhline(0, color="black", linewidth=0.8)
    truc_sai_so.set(xlabel="Thời gian (s)", ylabel="Sai số (độ)")
    truc_sai_so.legend()
    hinh.tight_layout()
    return hinh, (truc_heading, truc_sai_so)


def ve_pid(du_lieu: pd.DataFrame, tieu_de: str = "Các thành phần hiệu chỉnh heading"):
    """Vẽ riêng P, I, D và tổng hiệu chỉnh."""

    cac_cot = ["time_s", "heading_p", "heading_i", "heading_d", "heading_total"]
    _kiem_tra_cot(du_lieu, cac_cot)
    hinh, truc = plt.subplots()
    nhan = {
        "heading_p": "P",
        "heading_i": "I",
        "heading_d": "D",
        "heading_total": "Tổng",
    }
    for cot, ten in nhan.items():
        truc.plot(du_lieu["time_s"], du_lieu[cot], label=ten)
    truc.set(
        title=tieu_de,
        xlabel="Thời gian (s)",
        ylabel="Hiệu chỉnh chuẩn hóa",
    )
    truc.legend(ncol=4)
    hinh.tight_layout()
    return hinh, truc


def ve_dien(du_lieu: pd.DataFrame, tieu_de: str = "Dòng điện và điện áp"):
    """Vẽ dòng hai động cơ và điện áp pin trên hai trục."""

    _kiem_tra_cot(du_lieu, ["time_s", "battery_v"])
    hinh, truc_dong = plt.subplots()
    if "left_current_a" in du_lieu:
        truc_dong.plot(du_lieu["time_s"], du_lieu["left_current_a"], label="Dòng trái")
    if "right_current_a" in du_lieu:
        truc_dong.plot(du_lieu["time_s"], du_lieu["right_current_a"], label="Dòng phải")
    truc_dong.set(title=tieu_de, xlabel="Thời gian (s)", ylabel="Dòng điện (A)")

    truc_ap = truc_dong.twinx()
    truc_ap.plot(
        du_lieu["time_s"],
        du_lieu["battery_v"],
        color="tab:green",
        alpha=0.75,
        label="Điện áp",
    )
    truc_ap.set_ylabel("Điện áp (V)")

    duong = truc_dong.lines + truc_ap.lines
    truc_dong.legend(duong, [dong.get_label() for dong in duong], loc="best")
    hinh.tight_layout()
    return hinh, (truc_dong, truc_ap)
