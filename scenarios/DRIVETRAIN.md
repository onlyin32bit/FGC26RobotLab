# Kế hoạch thử nghiệm Drivetrain

Tài liệu này quy định các thử nghiệm drivetrain có thể lặp lại và tạo bằng
chứng cho quyết định cơ khí/điều khiển. Mỗi run vật lý tạo một CSV gốc, video,
và một dòng tóm tắt trong `data/run_summary.csv`.

## Dữ liệu dùng chung

Mọi kịch bản drivetrain dùng [master schema](../schema/EXPERIMENT_SCHEMA.md),
không tự định nghĩa lại các cột thời gian, lệnh, vận tốc, dòng, điện áp, heading,
phase hay event. Một kịch bản chỉ được thêm cột sau phần global với tiền tố
`scenario_`. Kết quả tóm tắt được ghi dạng long-form trong `data/run_summary.csv`:
mỗi metric là một hàng, không phải một header riêng cho từng scenario.

## Nguyên tắc thiết kế thí nghiệm

Mục tiêu là chọn cấu hình có khả năng tăng tốc, giữ hướng, quay, phanh và kéo
tải tốt nhất trong giới hạn dòng điện, điện áp, nhiệt độ và an toàn cơ khí.

Chỉ thay đổi **một biến độc lập trong mỗi phép so sánh trực tiếp**. Mọi biến
khác phải được khóa và ghi lại, không chỉ giả định là giống nhau. Một thay đổi
cơ khí hoặc phần mềm dù nhỏ tạo một `configuration_id` mới.

| Nhóm       | Biến                    | Xử lý trong đợt đầu                                            | Bắt buộc ghi lại                              |
| ---------- | ----------------------- | -------------------------------------------------------------- | --------------------------------------------- |
| Cơ khí     | Gear ratio              | Khảo sát 10:1 và 13:1.                                         | Tỉ số truyền và mã hộp số.                    |
| Cơ khí     | Wheel diameter          | Khóa cùng đường kính/mức mòn; khảo sát ở đợt riêng.            | Đường kính đo thực tế, vị trí bánh.           |
| Cơ khí     | Wheel material/layout   | Khảo sát traction và omni mix.                                 | Loại, vật liệu, vị trí từng bánh.             |
| Cơ khí     | Number of driven wheels | Khóa ở đợt đầu; khảo sát riêng.                                | Số bánh chủ động và motor được cấp điện.      |
| Cơ khí     | Center of mass          | Khóa bố trí pin, cơ cấu và tải; khảo sát riêng.                | Mã bố trí CG hoặc tọa độ CG ước lượng.        |
| Cơ khí     | Robot mass              | Khảo sát 40 kg và 50 kg.                                       | Khối lượng robot và tải thực tế.              |
| Điều khiển | Current limit           | Khóa 30 A ở ma trận đầu.                                       | Phạm vi áp dụng và giá trị thực.              |
| Điều khiển | Slew-rate               | So sánh off và 0.5 s trước khi đổi gear ratio.                 | Slew-rate, deadband, profile lệnh.            |
| Điều khiển | Brake/coast             | Khóa một mode trong cả đợt; khảo sát riêng.                    | Mode của từng motor.                          |
| Điều khiển | Closed/open loop        | Khóa một mode trong cả đợt; khảo sát riêng.                    | Mode, PID/FF, heading hold, software version. |
| Điều kiện  | Battery state           | Không là biến khảo sát: cân bằng hoặc phân nhóm khi phân tích. | Mã pin, điện áp nghỉ/đầu/thấp nhất/cuối.      |
| Điều kiện  | Surface condition       | Khóa mặt sân, làn và hướng chạy; khảo sát riêng.               | Mã mặt sân, tình trạng và vệ sinh sân.        |

## Điều kiện kiểm soát và an toàn

- Trước mỗi block, kiểm tra xích/đai, ốc liên kết, bánh, encoder, IMU, giới hạn
  dòng, brake/coast và phiên bản phần mềm. Chụp ảnh bố trí tải/bánh của mỗi config.
- Dùng cùng mặt sân đã làm sạch, cùng làn, vạch xuất phát và khoảng cách thử cho
  các configuration được so sánh. Cân robot gồm pin/tải trước từng block.
- Dùng cùng loại pin hoặc luân phiên pin công bằng giữa các config. Chỉ so sánh
  trực tiếp run trong dải điện áp đầu đã chốt; nếu không cân bằng được, ghi đủ
  điện áp và phân nhóm/điều chỉnh khi phân tích.
- Ghi đồng thời CSV robot và video toàn bộ vùng thử nghiệm. Datalog phải có các
  marker phù hợp: `RUN_START`, `COMMAND_START`, `BRAKE_START`, `IMPACT`, `RUN_END`.
- Dừng khi mất kiểm soát, vượt ngưỡng an toàn đã duyệt, có tiếng động bất thường
  hoặc cơ khí lỏng. Không xóa dữ liệu: ghi `invalid_reason` và `anomaly_notes`.

## Ma trận cấu hình ban đầu

Các ô không có trong bảng được giữ cố định: wheel diameter, số bánh chủ động,
CG, brake/coast, control mode, PID/FF, heading hold, mặt sân và profile bài thử.

| Config | So sánh chính       | Gear ratio | Wheel layout |  Mass | Current limit | Slew-rate |
| ------ | ------------------- | ---------- | ------------ | ----: | ------------: | --------- |
| A      | Baseline            | 10:1       | traction     | 40 kg |          30 A | off       |
| B      | Slew-rate: A → B    | 10:1       | traction     | 40 kg |          30 A | 0.5 s     |
| C      | Gear ratio: B → C   | 13:1       | traction     | 40 kg |          30 A | 0.5 s     |
| D      | Wheel layout: C → D | 13:1       | omni mix     | 40 kg |          30 A | 0.5 s     |
| E      | Mass: C → E         | 13:1       | traction     | 50 kg |          30 A | 0.5 s     |

Đây là chuỗi so sánh có kiểm soát, không phải mọi cặp đều cùng một biến. Chỉ
kết luận ảnh hưởng một biến từ A–B, B–C, C–D và C–E. Không dùng A–C, B–D hay
D–E để quy cho một nguyên nhân. Nếu `omni mix` cũng đổi số bánh chủ động, tạo
một configuration bổ sung để tách wheel layout và driven wheels.

### Ma trận đợt tiếp theo

Sau khi chọn baseline từ đợt đầu, khảo sát từng biến còn lại trong block riêng:

| Block | Biến thay đổi    | Mức đề xuất                          | Giữ cố định                      |
| ----- | ---------------- | ------------------------------------ | -------------------------------- |
| M1    | Wheel diameter   | hiện tại, nhỏ hơn, lớn hơn           | ratio, bánh, mass, control mode  |
| M2    | Driven wheels    | hiện tại và phương án ít/nhiều hơn   | bánh, CG, mass, current limit    |
| M3    | Center of mass   | thấp/trung tâm, cao hoặc lệch        | mass tổng, bánh, ratio           |
| M4    | Current limit    | baseline, thấp hơn, cao hơn đã duyệt | pin, mass, slew-rate, mode       |
| M5    | Brake/coast      | brake, coast                         | cơ khí và profile phanh          |
| M6    | Closed/open loop | closed-loop, open-loop               | cơ khí, slew-rate, current limit |
| M7    | Surface          | chuẩn, ma sát thấp, gờ thấp          | baseline cơ khí/điều khiển       |

## Gói thử cho mỗi configuration

Mỗi configuration có 17 run: 5 chạy thẳng, 5 quay, 3 tăng tốc/phanh, 3 kéo tải
và 1 độ bền. Ma trận A–E vì thế có **85 run**. Endurance là kiểm tra suy giảm;
nó không thay thế số lần lặp thống kê của bài ngắn.

| Loại           | Mã kịch bản | Run/config | Mục tiêu                                     |
| -------------- | ----------- | ---------: | -------------------------------------------- |
| Chạy thẳng     | DT01        |          5 | Quãng đường, lệch ngang, giữ hướng, vận tốc. |
| Quay           | SC-DRV-03   |          5 | Sai số góc, overshoot, ổn định.              |
| Tăng tốc/phanh | SC-DRV-02   |          3 | Rise time, trượt, sụt áp, dừng.              |
| Kéo tải        | SC-DRV-06   |          3 | Lực kéo, dòng, khả năng khởi hành.           |
| Độ bền         | SC-DRV-05   |          1 | Suy giảm theo nhiệt, pin, chu kỳ.            |

Đặt tên CSV theo quy ước, ví dụ `20260719_DT01_T03_CFG-C.csv`. `trial` là lần
lặp của chính scenario/config; ghi thêm `run_order` để nhận biết ảnh hưởng pin
và nhiệt độ trong ngày.

## Thứ tự thực hiện không thiên vị

Không chạy hết 17 run của A rồi mới đến B. Với mỗi loại bài thử, xen kẽ config
theo hoán vị cân bằng và ghi `randomization_seed`. Một lịch xoay dễ tái lập:

| Lần lặp | Thứ tự configuration |
| ------- | -------------------- |
| 1       | A → B → C → D → E    |
| 2       | B → C → D → E → A    |
| 3       | C → D → E → A → B    |
| 4       | D → E → A → B → C    |
| 5       | E → A → B → C → D    |

Dùng đủ 5 hàng cho chạy thẳng/quay; dùng 3 hàng đầu cho phanh/kéo, hoặc bốc
thăm hoán vị cân bằng và lưu seed. Endurance thực hiện sau bài ngắn, theo thứ tự
bốc thăm hoặc xoay giữa các ngày. Nếu buộc đổi lịch vì pin, nhiệt độ hay sân,
ghi lý do thay vì âm thầm chạy lại. Giữa các run, kiểm tra nhanh cơ khí và nghỉ
theo tiêu chí nhiệt cố định của đội; ghi thời gian nghỉ và nhiệt độ đầu run.

## Chi tiết kịch bản

### DT00: Chạy không tải

Mục tiêu: đo ma sát, quán tính và độ trễ không tải. Đây là chẩn đoán trước/sau
đợt thử, không thuộc 17 run so sánh chính.

1. Nâng robot an toàn để bánh chủ động quay tự do, không thể chạm người/vật.
2. Giữ lệnh 0 trong 1 s, áp lệnh chuẩn, giữ đến khi RPM ổn định, rồi trả về 0.
3. Lặp chiều tiến/lùi nếu phần cứng cho phép.
4. Đo RPM, dòng không tải, chênh RPM/dòng giữa motor, thời gian đáp ứng và
   vibration RMS.

Không dùng bài này để suy ra lực kéo trên sân. Nếu rung hoặc chênh motor tăng
đột biến so với baseline, kiểm tra cơ khí trước khi chạy bài có tải.

### DT01: Chạy thẳng

Mục tiêu: đo sai số quãng đường, lệch ngang, giữ hướng và độ lặp lại.

1. Đặt robot ở vạch 0, cùng hướng/làn; giữ đứng yên tối thiểu 1 s.
2. Chạy profile chuẩn 2 m. Control mode và heading hold phải giống nhau cho mọi
   config; đánh giá heading hold là một block riêng, không trộn vào ma trận này.
3. Khi dừng ổn định, đo vị trí thật bằng AprilTag hoặc dụng cụ đã hiệu chuẩn.
4. Chạy 5 lần/config theo thứ tự xen kẽ. Phân bố hướng tiến/lùi hoặc mức lệnh
   phải được chốt trước và giống nhau giữa các config.

Đo: quãng đường thật/sai số, lệch ngang, sai số heading cuối, heading RMSE/max,
vận tốc mục tiêu/thực tế mỗi bên, dòng cực đại, điện áp thấp nhất, settling time.

### SC-DRV-02 — Tăng tốc 0 → 75% và phanh

Mục tiêu: đo rise time, trượt bánh, sụt áp và khoảng cách dừng.

1. Từ đứng yên, giữ lệnh 0 trong 1 s.
2. Áp profile 0.00 → 0.75; slew-rate lấy từ configuration.
3. Giữ lệnh 0.75 ít nhất 1 s hoặc đến tiêu chí vận tốc ổn định đã chốt.
4. Ra marker `BRAKE_START`, đưa lệnh về 0 và chờ dừng hoàn toàn.
5. Chạy 3 lần/config ở cùng hướng và vùng an toàn.

Đo: rise time 10–90%, gia tốc/tốc độ cực đại, dao động vận tốc, trượt, dòng đỉnh,
sụt áp, khoảng cách dừng, sai số heading và thời gian dừng. Không đổi brake/coast
giữa các config.

### SC-DRV-03 — Quay chính xác

Mục tiêu: đánh giá sai số góc, overshoot và thời gian ổn định khi quay.

1. Đặt robot ở tâm vùng quay, giữ đứng yên 1 s.
2. Dùng cùng tập mục tiêu cho mọi config. Phân bố 5 run đề xuất: `+90°`, `-90°`,
   `+180°`, `-180°` và một lần lặp 90° theo hướng đã chốt trước.
3. Dừng khi đạt tiêu chí ổn định hoặc timeout an toàn.
4. Đối chiếu IMU với AprilTag hay phép đo quỹ đạo ngoài.

Đo: sai số góc cuối, overshoot, tốc độ góc cực đại, thời gian đạt mục tiêu/thời
gian ổn định, dòng/điện áp và chênh trái-phải. Ghi góc, chiều và tốc độ quay mục
tiêu trong `command_profile`.

### SC-DRV-06 — Kéo tải

Mục tiêu: đo lực kéo hữu ích khi chịu tải ngoài có kiểm soát.

1. Khóa điểm móc, dây/đai, chiều cao móc và hướng kéo. Dùng lực kế hoặc cảm biến
   lực đã hiệu chuẩn; không kéo người hoặc vật không cố định.
2. Dùng lực cản lặp lại được (ví dụ sled đã ghi khối lượng/ma sát), không kéo tay.
3. Áp cùng profile tăng lệnh/giữ lệnh, chạy 3 lần/config và kiểm tra móc/dây.
4. Dừng nếu dây, móc hoặc robot trở nên mất an toàn.

Đo: lực đỉnh/trung bình trong cửa sổ ổn định, tốc độ/quãng đường, thời gian khởi
hành, trượt, dòng, điện áp, nhiệt độ. Khi so sánh 40 kg với 50 kg, báo cáo lực
theo newton và lực chuẩn hóa theo khối lượng robot.

### SC-DRV-04 — Va chạm nhẹ và phục hồi quỹ đạo

Mục tiêu: kiểm tra phục hồi sau nhiễu thực tế. Chỉ chạy sau ma trận cơ bản đạt
an toàn; không dùng để chọn gear ratio ban đầu.

- Chạy thẳng ở lệnh đã chốt qua dải ma sát thấp/gờ thấp một bên, hoặc với nhiễu
  xoay nhẹ có đệm tại vị trí đã đánh dấu.
- Giữ loại, vị trí và cường độ nhiễu giống nhau cho các config so sánh.
- Đo sai số heading cực đại, lệch ngang, thời gian/quãng đường hồi phục và dòng.
- Không va chạm tốc độ cao hoặc va vào người.

### SC-DRV-05 — Độ bền và lặp lại chu trình

Mục tiêu: phát hiện suy giảm theo thời gian, lỗi nhiệt, lỏng cơ khí và ảnh hưởng
của pin. Mỗi config chạy một lần sau bài ngắn.

1. Chạy chu trình tiến, dừng, lùi, quay trái/phải trong 10 phút. Biên độ lệnh,
   thời lượng từng pha và dừng phải được version-control.
2. Ghi nhiệt độ vỏ motor bằng cùng dụng cụ ở mốc 0, 2, 5, 8, 10 phút (hoặc mốc
   đội đã chốt) mà không che thông gió.
3. Chạy DT01 chuẩn trước/sau endurance, lưu là `pre`/`post`, không gộp vào 5
   lần lặp DT01 của ma trận.
4. Kiểm tra cơ khí sau run và ghi tiếng động, mùi, độ rơ hoặc lỗi.

Đo: vận tốc, dòng, điện áp, sai số heading, nhiệt độ, lỗi điều khiển và chênh
lệch pre/post. Flywheel đồng thời là một configuration tải điện mới, không trộn
với baseline.

## Dữ liệu, tính hợp lệ và quyết định

Mỗi run phải thỏa master schema. Những thông tin ngoài robot như video, ảnh lắp
ráp, randomization seed, run order và ghi chú thao tác nằm trong manifest/báo
cáo của buổi thử, liên kết bằng `run_id`; không tạo cột time-series riêng cho
từng scenario.

Chỉ loại run khỏi phân tích chính khi có lý do ghi rõ: lỗi cảm biến/datalog, vật
cản ngoài ý muốn, sai profile, sai config, hoặc dừng an toàn. Run bị loại vẫn
lưu nguyên CSV/video; chạy lại chỉ để bù số lần lặp, không xóa run cũ.

Với từng cặp hợp lệ A–B, B–C, C–D, C–E, báo cáo toàn bộ run, trung vị, độ phân
tán và chênh lệch với config đối chứng. Kết luận notebook phải nêu biến duy nhất
đã đổi, số run hợp lệ/bị loại và lý do, ảnh hưởng cùng độ phân tán, rồi quyết
định giữ, sửa, hoàn tác hoặc chuyển sang ma trận tiếp theo.
