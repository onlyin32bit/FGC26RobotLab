"""Đọc dữ liệu mà không thay đổi tệp CSV gốc."""

from pathlib import Path

import pandas as pd


def tai_cac_lan_chay(
    thu_muc: str | Path,
    mau_tep: str = "*.csv",
) -> pd.DataFrame:
    """Đọc và ghép mọi CSV trong một thư mục thử nghiệm.

    Nếu tệp chưa có ``run_id``, tên tệp sẽ được dùng làm mã lần chạy.
    Hàm trả về DataFrame rỗng khi chưa có dữ liệu để notebook vẫn mở được.
    """

    duong_dan = Path(thu_muc)
    cac_tep = sorted(duong_dan.glob(mau_tep))
    if not cac_tep:
        return pd.DataFrame()

    cac_bang: list[pd.DataFrame] = []
    for tep in cac_tep:
        bang = pd.read_csv(tep)
        if "run_id" not in bang.columns:
            bang.insert(0, "run_id", tep.stem)
        bang["source_file"] = tep.name
        cac_bang.append(bang)

    return pd.concat(cac_bang, ignore_index=True, sort=False)


def tai_tom_tat(tep: str | Path) -> pd.DataFrame:
    """Đọc bảng tóm tắt bên ngoài nếu tệp tồn tại."""

    duong_dan = Path(tep)
    if not duong_dan.exists():
        return pd.DataFrame()
    return pd.read_csv(duong_dan)
