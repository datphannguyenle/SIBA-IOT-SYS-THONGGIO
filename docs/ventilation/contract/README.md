# Ventilation Data Contract

## 1. Hợp đồng hiện hành — Version 0.3 (Chốt 18/09/2026)

| File | Vai trò | Trạng thái |
|---|---|---|
| `SIBA_Ventilation_Agent_DataContract_v0.3.json` | Hợp đồng máy đọc cho agent/code (265 biến, mirror `D550–D959` ↔ `4x-1..4x-410`) | **HIỆN HÀNH**; sha256 `a3cab3669962e988f42f94acee09260ec086deef4ee41210596483647ac23b68` |
| `SIBA_Ventilation_PLC_HMI_TB_Mapping_TEMPLATE_v0.3.xlsx` | Bảng Excel mẫu ánh xạ PLC–HMI–ThingsBoard cho kỹ sư PLC | **HIỆN HÀNH**; đầy đủ 265 hàng biến; sha256 `fbe8a1c8901afa29286e0e95c110c972d2d810fc1233f4de15c7f80411303ba5` |
| `contract_v0.3_decisions.md` | Quyết định dự án v0.3: kiến trúc PLC riêng, dịch mirror -450 về D550–D959 | **HIỆN HÀNH**; chốt 18/09/2026 |
| `contract_v0.3_decisions.json` | Cấu hình máy đọc cho builder và bộ test | **HIỆN HÀNH** |

Phân loại: **APPROVED PROJECT INTERFACE TEMPLATE**, **chưa phải RUNTIME VERIFIED PLC MAPPING**
(mọi `plc_source` = null, chờ kỹ sư PLC điền khi đấu nối thực tế).

Hệ thống thông gió sử dụng PLC riêng, độc lập với hệ khử mùi. Dải mirror PLC bắt đầu từ `D550`
đến `D959` (410 words), tương ứng các thanh ghi Modbus Holding Register `4x-1 .. 4x-410`.

---

## 2. Bằng chứng lịch sử — Version 0.2 (17/09/2026)

| File | Vai trò | Ghi chú |
|---|---|---|
| `SIBA_Ventilation_Agent_DataContract_v0.2.json` | Hợp đồng v0.2 cũ (mirror `D1000–D1409` ↔ `4x-1..4x-410`) | Bằng chứng lịch sử, giữ nguyên vẹn; sha256 `f25cd7ab9608f1fa04560274a4ff5e39c7428b9ee6049f3335fc1392870c60db` |
| `contract_v0.2_decisions.md` | Quyết định dự án v0.2 | Lưu vết lịch sử |
| `contract_v0.2_decisions.json` | Quyết định máy đọc v0.2 | Lưu vết lịch sử |

---

## 3. Tài liệu đối chiếu

- `vent007_alignment_report.md`: Báo cáo đối chiếu chi tiết giữa dashboard ThingsBoard và Data Contract (v0.2/v0.3).

Lưu ý:
- `config/ventilation_data_contract.json` là bằng chứng VENT-002 (snake_case cũ), bảo lưu không sửa.
