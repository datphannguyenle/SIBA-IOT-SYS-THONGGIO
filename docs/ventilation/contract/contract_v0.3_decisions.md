# Contract v0.3 — quyết định dự án (chốt 18/09/2026)

Nguồn: Phê duyệt từ chủ dự án (ChatGPT Web / Project Owner) ngày 18/09/2026.
Data Contract v0.3 chính thức thay thế v0.2 làm GIAO DIỆN HIỆN HÀNH của hệ thống thông gió SIBA.
Bản v0.2 được bảo lưu nguyên vẹn làm bằng chứng lịch sử (historical evidence).

---

## A. Kiến trúc PLC và địa chỉ giao diện

| Hạng mục | Quyết định v0.3 | Ghi chú so với v0.2 |
|---|---|---|
| Kiến trúc PLC | **PLC RIÊNG** cho hệ thông gió | Độc lập hoàn toàn với PLC hệ khử mùi |
| Vùng mirror PLC | `D550–D959` (410 words) | Dịch chuyển `-450` từ `D1000–D1409` về dải chuẩn SIBA |
| Modbus Holding Registers | `4x-1 .. 4x-410` | **GIỮ NGUYÊN** không đổi |
| Số lượng biến | 265 biến (410 words) | **GIỮ NGUYÊN** số lượng, thứ tự, kiểu, độ rộng |
| Hãng/model PLC, IP, port, unit ID | `PLC_ENGINEER_TBD` | Không chặn tiến độ dashboard repo |
| Thứ tự word float32 | `PLC_ENGINEER_TBD` | Không giả định ABCD/CDAB trước khi kỹ sư PLC xác nhận |
| Gateway | Gateway Weintek riêng hoặc port riêng cho thông gió | Chu kỳ đọc/topology chốt khi đấu nối |

---

## B. Quan hệ với Data Contract v0.2

1. **Bảo lưu v0.2**:
   - `SIBA_Ventilation_Agent_DataContract_v0.2.json` (sha256 `f25cd7ab9608f1fa04560274a4ff5e39c7428b9ee6049f3335fc1392870c60db`) được giữ nguyên trong repo làm bằng chứng lịch sử.
   - Không sửa file v0.2 gốc.

2. **Thay đổi trong v0.3**:
   - Chỉ điều chỉnh địa chỉ mirror PLC: `plc_start` và `plc_end` dịch chuyển -450 (từ D1000-D1409 sang D550-D959).
   - Địa chỉ Modbus Holding Register 4x giữ nguyên hoàn toàn (4x-1 .. 4x-410).
   - 265 keys giữ nguyên.
   - Nhóm, vai trò, nhãn, kiểu dữ liệu logical/words giữ nguyên.
   - Ngữ nghĩa dashboard giữ nguyên hoàn toàn.

---

## C. Nguồn artifact hiện hành

- JSON hợp đồng: `docs/ventilation/contract/SIBA_Ventilation_Agent_DataContract_v0.3.json`
  (sha256 `a3cab3669962e988f42f94acee09260ec086deef4ee41210596483647ac23b68`).
- Bảng mẫu Excel cho kỹ sư PLC: `docs/ventilation/contract/SIBA_Ventilation_PLC_HMI_TB_Mapping_TEMPLATE_v0.3.xlsx` (sha256 `fbe8a1c8901afa29286e0e95c110c972d2d810fc1233f4de15c7f80411303ba5`).

---

## D. Enum & Quy tắc dữ liệu (kế thừa từ v0.2)

| Key | 0 | 1 | Giá trị khác / null |
|---|---|---|---|
| `operatingMode` | `MANUAL` | `AUTO` | `UNKNOWN` |
| `controlBasis` | `ACTUAL_TEMPERATURE` | `PERCEIVED_TEMPERATURE` | `UNKNOWN` |
| `fanControlMode` | `STEP` | `VFD` | `UNKNOWN` |
| `dehumidificationEnabled` | `DISABLED` | `ENABLED` | `UNKNOWN` |
| `fanXXRun`, `coolingPumpXXRun` | `STOPPED` | `RUNNING` | `UNKNOWN`; thiết bị N/A → `NOT_CONFIGURED` |

---

## E. Ranh giới an toàn V1 & Nghiệp vụ

- **stageCount**: Không có trong contract. Dashboard chỉ hiển thị `fanStage` (ví dụ `4`), không hiện tỉ lệ `x / y`.
- **Thiết bị**: Tối đa 6 quạt + 2 bơm. Thiết bị không có trong cấu hình trại → `NOT_CONFIGURED` (làm mờ có nhãn), không hiển thị `STOPPED` hay `FAULT`.
- **Cảnh báo lỗi thiết bị**: Bỏ các cờ lỗi per-fan (`fanXXFault`). Lỗi phần cứng hiển thị qua cờ hệ thống `equipmentFaultActive`.
- **vent_settings**: Trạng thái CHỈ ĐỌC (READ-ONLY). Không có nút ghi, không RPC, không sửa attribute ThingsBoard hay PLC register.
- **controllerOnline, dataQuality**: Là biến `PLATFORM_DERIVED`, không ánh xạ PLC D-register.
