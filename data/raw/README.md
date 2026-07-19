# Dữ liệu thô

Đặt CSV tải từ Control Hub vào thư mục theo mã thử nghiệm:

```text
data/raw/DT02/
data/raw/DT03/
data/raw/DT04/
```

Không mở rồi lưu lại các tệp này bằng Excel hoặc Google Sheets. Nếu cần sửa tên
cột, lọc hàng hoặc bổ sung dữ liệu, hãy tạo kết quả mới trong `data/processed/`
bằng mã Python để thay đổi có thể được lặp lại và kiểm tra.

Mỗi CSV nên chứa:

- `run_id`, `test_id`, `trial`, `sample`, `time_s`, `loop_dt_ms`
- lệnh điều khiển
- heading và các thành phần PID
- vận tốc mục tiêu/thực tế của hai bên
- vị trí encoder
- dòng điện và điện áp
- các mốc `RUN_START`, `COMMAND_START`, `BRAKE_START`, `IMPACT`, `RUN_END`
