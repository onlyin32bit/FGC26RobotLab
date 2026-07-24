# FGC26 Robot Lab

Không gian phân tích dữ liệu và lập hồ sơ kỹ thuật cho Robot 01 của Đội tuyển
Việt Nam tại FIRST Global Challenge 2026.

Project này nhận các tệp CSV từ Control Hub, kiểm tra chất lượng dữ liệu, tính
chỉ số hiệu năng, tạo biểu đồ và lưu kết luận có thể tái lập cho sổ tay kỹ thuật.
Dữ liệu thô là bằng chứng gốc và không được chỉnh sửa bằng tay.

## Bắt đầu nhanh

Yêu cầu:

- Python 3.12
- `uv`

Cài môi trường:

```bash
uv sync
```

Mở JupyterLab:

```bash
uv run jupyter lab
```

Chạy kiểm thử thư viện phân tích:

```bash
uv run pytest
```

Kiểm tra chất lượng mã:

```bash
uv run ruff check .
```

## Cấu trúc

```text
FGC26RobotLab/
├── data/
│   ├── raw/              # CSV gốc từ robot, không chỉnh sửa
│   └── processed/        # Bảng được sinh từ phân tích
├── figures/              # Biểu đồ xuất từ notebook
├── schema/                # Master schema cho mọi CSV và summary
├── notebooks/
│   ├── TEMPLATE.ipynb    # Mẫu cho kịch bản mới
│   ├── DT01.ipynb        # Hiệu chuẩn encoder và quãng đường
│   ├── DT02.ipynb        # Chạy thẳng 2 m
│   ├── DT03.ipynb        # Chạy chậm
│   └── DT04.ipynb        # Tăng tốc 0 → 75%
├── reports/              # Báo cáo HTML/PDF đã đóng băng
├── scripts/
│   └── tao_notebook_mau.py
├── src/analysis/         # Hàm phân tích dùng chung
└── tests/                # Kiểm thử công thức
```

## Quy ước làm việc

### Một lần chạy

Mỗi lần robot thực hiện một phép thử tạo một CSV riêng:

```text
YYYYMMDD_TESTID_Txx_CAUHINH.csv
```

Ví dụ:

```text
20260719_DT02_T03_PID03.csv
```

### Một notebook

Mỗi kịch bản hoặc câu hỏi kỹ thuật có một notebook. Notebook đó đọc nhiều lần
chạy, so sánh các cấu hình và kết luận dựa trên toàn bộ bằng chứng. Không tạo
một notebook riêng cho từng lần chạy.

### Một báo cáo đóng băng

Khi đã ra quyết định, xuất notebook thành HTML:

```bash
uv run jupyter nbconvert \
  --to html \
  --execute notebooks/DT02.ipynb \
  --output-dir reports
```

Tên báo cáo nên chứa ngày, mã thử nghiệm và mã cấu hình. Báo cáo đã dùng trong
sổ tay kỹ thuật không được ghi đè; nếu phân tích thay đổi, xuất một phiên bản mới.

## Luồng dữ liệu

```text
CSV từ Control Hub
        ↓
data/raw/<MÃ_THỬ>/
        ↓
Notebook theo kịch bản
        ↓
Kiểm tra dữ liệu + chỉ số + biểu đồ
        ↓
Kết luận kỹ thuật
        ↓
reports/ và sổ tay kỹ thuật
```

## Master schema

Mọi kịch bản dùng [master experiment schema](schema/SCHEMA.md).
Time-series CSV luôn có cùng envelope `fgc-ts-v1`; cột riêng của scenario chỉ
được thêm sau envelope với tiền tố `scenario_`. `data/run_summary.csv` dùng
`fgc-summary-v1`, một hàng cho mỗi metric, nên không có header tóm tắt riêng
theo scenario.

## Thêm một kịch bản

1. Sao chép `notebooks/TEMPLATE.ipynb`.
2. Đổi tên theo mã thử nghiệm, ví dụ `DT05.ipynb`.
3. Cập nhật ô tham số và câu hỏi kỹ thuật.
4. Đặt CSV vào `data/raw/DT05/`.
5. Chọn **Khởi động lại kernel và chạy tất cả**.
6. Kiểm tra cảnh báo dữ liệu trước khi dùng kết quả.
7. Xuất báo cáo sau khi nhóm chốt quyết định.

## Nguyên tắc tái lập

- Không sửa CSV trong `data/raw/`.
- Không nhập tay kết quả đã tính vào notebook.
- Mọi biểu đồ phải có đơn vị, mã lần chạy và mã cấu hình.
- Mọi lần chạy bị loại vẫn phải được lưu cùng lý do.
- Các công thức dùng chung phải đặt trong `src/analysis/`.
- Notebook phải chạy được từ đầu sau khi khởi động lại kernel.
- Luôn ghi phiên bản phần mềm và cấu hình phần cứng.
