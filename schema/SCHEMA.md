# Schema gốc

`fgc-ts-v1` là layout time-series chung duy nhất cho mọi cơ cấu: drivetrain,
flywheel, intake, arm, vision hoặc bài thử toàn robot. Nó chỉ giữ thông tin mà
mọi lần chạy đều có. Dữ liệu riêng của cơ cấu được nối thêm bằng cột
`scenario_`. Thông số phần cứng như khối lượng robot, đường kính/số lượng/vật
liệu bánh, tâm khối lượng, mặt sân và mã pin nằm trong notebook hoặc hồ sơ cấu
hình, không lặp lại trên từng mẫu log.

File `dt00-v1` cũ chỉ là dữ liệu lưu trữ; không định nghĩa schema này.

## Cột time-series chung

| Cột                | Ý nghĩa                                        |
| ------------------ | ---------------------------------------------- | --- |
| `schema_version`   | Luôn là `fgc-ts-v1`.                           |
| `run_id`           | Mã bất biến của file/lần chạy.                 |
| `scenario_id`      | Mã bài thử, ví dụ `DT02` hoặc `FW01`.          |
| `configuration_id` | Mã cấu hình đã ghi trong hồ sơ thí nghiệm.     |
| `trial`            | Lần lặp dự kiến, bắt đầu từ 1.                 |
| `sample_index`     | Số thứ tự mẫu trong run, bắt đầu từ 0.         |
| `time_s`           | Giây đơn điệu kể từ lúc mở logger.             |
| `loop_dt_ms`       | Thời gian của vòng điều khiển.                 |
| `event`            | Một hoặc nhiều event cố định, cách nhau bằng ` | `.  |
| `battery_v`        | Điện áp pin đo được.                           |

Để trống nghĩa là không đo được; `0` là giá trị đã đo. Các cột chung luôn đứng
đầu, đúng thứ tự trên. Mỗi file chỉ có một `run_id`; `sample_index` tăng từng
đơn vị và `time_s` tăng nghiêm ngặt. Không có cột `phase` chung.

## Tên event cố định

Chỉ dùng các token sau trong `event`:

| Event            | Ý nghĩa                                            |
| ---------------- | -------------------------------------------------- |
| `LOG_START`      | Đã mở CSV logger.                                  |
| `START`          | Bắt đầu profile của bài thử.                       |
| `COMMAND_START`  | Bắt đầu lệnh tác động cơ cấu.                      |
| `TARGET_REACHED` | Lần đầu đạt tiêu chí mục tiêu.                     |
| `COMMAND_STOP`   | Kết thúc lệnh tác động.                            |
| `STOPPED`        | Cơ cấu/chuyển động đã dừng theo tiêu chí đo.       |
| `MARK`           | Mốc chủ đích, phải được giải thích trong notebook. |
| `END`            | Kết thúc bình thường.                              |
| `ABORT`          | Operator hoặc OpMode hủy run.                      |
| `FAULT`          | Lỗi logger, cảm biến hoặc an toàn kết thúc run.    |

`LOG_START` xuất hiện một lần. Mỗi run có đúng một event kết thúc: `END`,
`ABORT` hoặc `FAULT`.

## Phần mở rộng theo cơ cấu

Cột mở rộng nối sau các cột chung, bắt đầu bằng `scenario_`, và được liệt kê
trong notebook/tài liệu của chính scenario. Chỉ ghi cột cần để trả lời câu hỏi
của bài thử.

- Drivetrain: `scenario_drive_command`, `scenario_gear_reduction`,
  `scenario_left_actual_tps`, `scenario_right_actual_tps`,
  `scenario_left_current_a`, `scenario_right_current_a`,
  `scenario_heading_deg`, `scenario_yaw_rate_deg_s`.
- Flywheel: `scenario_gear_reduction`, `scenario_target_rpm`,
  `scenario_actual_rpm`, `scenario_motor_current_a`.
- Intake: `scenario_intake_command`, `scenario_intake_current_a`,
  `scenario_game_piece_detected`.

Drivetrain bắt đầu từ schema gốc rồi chọn các cột riêng cần thiết; DT00 thêm
RPM, ripple, rung và chiều chạy vì câu hỏi free-spin cần chúng. Các scenario
drivetrain khác không tự động mang theo những cột đó.

## Schema tóm tắt

`fgc-summary-v1` có một metric trên mỗi dòng.

| Cột                | Ý nghĩa                                        |
| ------------------ | ---------------------------------------------- |
| `schema_version`   | Luôn là `fgc-summary-v1`.                      |
| `run_id`           | Run nguồn.                                     |
| `scenario_id`      | Scenario nguồn.                                |
| `configuration_id` | Cấu hình nguồn.                                |
| `metric_id`        | Tên metric snake_case ổn định.                 |
| `metric_value`     | Giá trị số.                                    |
| `metric_unit`      | Đơn vị.                                        |
| `aggregation`      | Cách tính như `peak`, `mean`, `rmse`, `final`. |
| `source`           | `robot`, `video`, `manual`, `analysis`.        |
| `validity`         | `valid`, `invalid`, `suspect`.                 |
| `notes`            | Lý do hoặc ghi chú.                            |
