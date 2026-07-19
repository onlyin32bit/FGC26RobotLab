"""Các chỉ số dùng chung cho thử nghiệm drivetrain."""

from collections.abc import Iterable

import numpy as np
import pandas as pd


def _mang_so(gia_tri: Iterable[float]) -> np.ndarray:
    mang = np.asarray(list(gia_tri), dtype=float)
    return mang[np.isfinite(mang)]


def rmse(gia_tri: Iterable[float]) -> float:
    """Căn bậc hai của trung bình bình phương."""

    mang = _mang_so(gia_tri)
    if mang.size == 0:
        return float("nan")
    return float(np.sqrt(np.mean(np.square(mang))))


def sai_so_rmse(thuc_te: Iterable[float], muc_tieu: Iterable[float]) -> float:
    """RMSE giữa tín hiệu thực tế và mục tiêu."""

    thuc_te_arr = np.asarray(list(thuc_te), dtype=float)
    muc_tieu_arr = np.asarray(list(muc_tieu), dtype=float)
    hop_le = np.isfinite(thuc_te_arr) & np.isfinite(muc_tieu_arr)
    if not hop_le.any():
        return float("nan")
    return rmse(thuc_te_arr[hop_le] - muc_tieu_arr[hop_le])


def do_lech_mm_m(do_lech_ngang_mm: float, quang_duong_mm: float) -> float:
    """Độ lệch ngang chuẩn hóa theo mỗi mét di chuyển."""

    if quang_duong_mm == 0:
        return float("nan")
    return abs(do_lech_ngang_mm) / abs(quang_duong_mm) * 1_000.0


def do_sut_ap(dien_ap: Iterable[float]) -> float:
    """Hiệu giữa điện áp ban đầu và điện áp nhỏ nhất."""

    mang = _mang_so(dien_ap)
    if mang.size == 0:
        return float("nan")
    return float(mang[0] - np.min(mang))


def thoi_gian_tang_10_90(
    thoi_gian_s: Iterable[float],
    tin_hieu: Iterable[float],
    gia_tri_cuoi: float | None = None,
) -> float:
    """Thời gian để tín hiệu đi từ 10% lên 90% giá trị cuối."""

    t = np.asarray(list(thoi_gian_s), dtype=float)
    y = np.abs(np.asarray(list(tin_hieu), dtype=float))
    hop_le = np.isfinite(t) & np.isfinite(y)
    t, y = t[hop_le], y[hop_le]
    if t.size < 2:
        return float("nan")

    muc_cuoi = abs(gia_tri_cuoi) if gia_tri_cuoi is not None else float(np.median(y[-5:]))
    if muc_cuoi <= 0:
        return float("nan")

    chi_so_10 = np.flatnonzero(y >= 0.1 * muc_cuoi)
    chi_so_90 = np.flatnonzero(y >= 0.9 * muc_cuoi)
    if chi_so_10.size == 0 or chi_so_90.size == 0:
        return float("nan")

    i10 = int(chi_so_10[0])
    i90_hop_le = chi_so_90[chi_so_90 >= i10]
    if i90_hop_le.size == 0:
        return float("nan")
    return float(t[int(i90_hop_le[0])] - t[i10])


def thoi_gian_on_dinh(
    thoi_gian_s: Iterable[float],
    sai_so: Iterable[float],
    dung_sai: float,
    thoi_gian_giu_s: float = 0.5,
) -> float:
    """Thời điểm đầu tiên sai số nằm trong dung sai đủ lâu."""

    t = np.asarray(list(thoi_gian_s), dtype=float)
    e = np.abs(np.asarray(list(sai_so), dtype=float))
    hop_le = np.isfinite(t) & np.isfinite(e)
    t, e = t[hop_le], e[hop_le]
    if t.size < 2:
        return float("nan")

    trong_mien = e <= abs(dung_sai)
    for bat_dau in np.flatnonzero(trong_mien):
        ket_thuc = np.searchsorted(t, t[bat_dau] + thoi_gian_giu_s, side="left")
        if ket_thuc < t.size and trong_mien[bat_dau : ket_thuc + 1].all():
            return float(t[bat_dau] - t[0])
    return float("nan")


def tong_hop_lan_chay(du_lieu: pd.DataFrame) -> pd.DataFrame:
    """Tính các chỉ số nền tảng cho từng ``run_id``."""

    if du_lieu.empty or "run_id" not in du_lieu:
        return pd.DataFrame()

    ket_qua: list[dict[str, float | str]] = []
    for run_id, nhom in du_lieu.groupby("run_id", sort=False):
        hang: dict[str, float | str] = {"run_id": str(run_id)}

        if "heading_error_deg" in nhom:
            sai_so_heading = pd.to_numeric(nhom["heading_error_deg"], errors="coerce")
            hang["heading_rmse_deg"] = rmse(sai_so_heading)
            hang["heading_max_abs_deg"] = float(sai_so_heading.abs().max())

        cap_van_toc = (
            ("left_actual_tps", "left_target_tps", "left_velocity_rmse_tps"),
            ("right_actual_tps", "right_target_tps", "right_velocity_rmse_tps"),
        )
        for cot_thuc, cot_muc_tieu, ten_ket_qua in cap_van_toc:
            if {cot_thuc, cot_muc_tieu}.issubset(nhom.columns):
                hang[ten_ket_qua] = sai_so_rmse(nhom[cot_thuc], nhom[cot_muc_tieu])

        if "battery_v" in nhom:
            hang["battery_min_v"] = float(pd.to_numeric(nhom["battery_v"]).min())
            hang["battery_sag_v"] = do_sut_ap(nhom["battery_v"])

        if "loop_dt_ms" in nhom:
            chu_ky = pd.to_numeric(nhom["loop_dt_ms"], errors="coerce")
            hang["loop_p95_ms"] = float(chu_ky.quantile(0.95))
            hang["loop_max_ms"] = float(chu_ky.max())

        ket_qua.append(hang)

    return pd.DataFrame(ket_qua)
