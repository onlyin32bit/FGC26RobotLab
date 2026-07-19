"""Kiểm tra chất lượng trước khi tính toán và vẽ biểu đồ."""

from collections.abc import Iterable

import pandas as pd

COT_BAT_BUOC = {
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


def _them(loi: list[dict[str, str]], muc_do: str, noi_dung: str) -> None:
    loi.append({"muc_do": muc_do, "noi_dung": noi_dung})


def kiem_tra_du_lieu(
    du_lieu: pd.DataFrame,
    cot_bat_buoc: Iterable[str] = COT_BAT_BUOC,
) -> pd.DataFrame:
    """Trả về bảng cảnh báo/lỗi bằng tiếng Việt.

    Bảng rỗng nghĩa là chưa phát hiện vấn đề theo các quy tắc hiện tại.
    """

    loi: list[dict[str, str]] = []
    if du_lieu.empty:
        _them(loi, "THÔNG TIN", "Chưa tìm thấy CSV cho kịch bản này.")
        return pd.DataFrame(loi)

    cot_thieu = sorted(set(cot_bat_buoc) - set(du_lieu.columns))
    if cot_thieu:
        _them(loi, "LỖI", f"Thiếu cột bắt buộc: {', '.join(cot_thieu)}")

    if du_lieu.isna().all(axis=0).any():
        cot_rong = ", ".join(du_lieu.columns[du_lieu.isna().all(axis=0)])
        _them(loi, "CẢNH BÁO", f"Các cột hoàn toàn rỗng: {cot_rong}")

    if {"run_id", "sample"}.issubset(du_lieu.columns):
        so_trung = int(du_lieu.duplicated(["run_id", "sample"]).sum())
        if so_trung:
            _them(loi, "LỖI", f"Có {so_trung} mẫu trùng run_id và sample.")

    if {"run_id", "time_s"}.issubset(du_lieu.columns):
        for run_id, nhom in du_lieu.groupby("run_id", sort=False):
            thoi_gian = pd.to_numeric(nhom["time_s"], errors="coerce")
            if thoi_gian.isna().any():
                _them(loi, "LỖI", f"{run_id}: time_s có giá trị không phải số.")
            elif (thoi_gian.diff().dropna() <= 0).any():
                _them(loi, "LỖI", f"{run_id}: time_s không tăng nghiêm ngặt.")

    if "battery_v" in du_lieu:
        dien_ap = pd.to_numeric(du_lieu["battery_v"], errors="coerce")
        ngoai_mien = dien_ap.notna() & ~dien_ap.between(6.0, 16.0)
        if ngoai_mien.any():
            _them(
                loi,
                "CẢNH BÁO",
                f"Có {int(ngoai_mien.sum())} mẫu điện áp ngoài miền 6–16 V.",
            )

    if "loop_dt_ms" in du_lieu:
        chu_ky = pd.to_numeric(du_lieu["loop_dt_ms"], errors="coerce")
        if (chu_ky < 0).any():
            _them(loi, "LỖI", "loop_dt_ms có giá trị âm.")
        if (chu_ky > 100).any():
            _them(
                loi,
                "CẢNH BÁO",
                f"Có {int((chu_ky > 100).sum())} vòng lặp dài hơn 100 ms.",
            )

    if "event" in du_lieu:
        su_kien = set(du_lieu["event"].dropna().astype(str))
        if "RUN_START" not in su_kien:
            _them(loi, "CẢNH BÁO", "Không tìm thấy mốc RUN_START.")
        if "RUN_END" not in su_kien:
            _them(loi, "CẢNH BÁO", "Không tìm thấy mốc RUN_END.")

    if not loi:
        _them(loi, "ĐẠT", "Chưa phát hiện lỗi theo các quy tắc hiện tại.")
    return pd.DataFrame(loi)
