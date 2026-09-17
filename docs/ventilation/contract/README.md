# Ventilation Data Contract v0.2

| File | Vai trò | Trạng thái |
|---|---|---|
| `SIBA_Ventilation_Agent_DataContract_v0.2.json` | Hợp đồng máy đọc cho agent/code (265 biến, mirror `D1000–D1409` ↔ `4x-1..4x-410`) | Bản gốc, chép nguyên văn; sha256 `f25cd7ab9608f1fa04560274a4ff5e39c7428b9ee6049f3335fc1392870c60db` |
| `SIBA_Ventilation_PLC_HMI_TB_Mapping_TEMPLATE_v0.2.xlsx` | Bảng Excel cho kỹ sư PLC (nguồn sinh ra JSON) | **CHƯA CÓ trong repo** — không tìm thấy trên máy ngày 17/09/2026; cần người dùng bổ sung |
| `contract_v0.2_decisions.md` | Quyết định dự án đã chốt (enum, TBD, nghiệp vụ) — KHÔNG sửa file gốc | Chốt 17/09/2026 |
| `vent007_alignment_report.md` | Đối chiếu dashboard hiện tại ↔ contract v0.2 | VENT-007 |

Phân loại: **APPROVED PROJECT INTERFACE TEMPLATE**, **chưa phải RUNTIME VERIFIED PLC MAPPING**
(mọi `plc_source` = null). VENT-002 vẫn NOT READY FOR REAL DATA.

Không đánh số lại mirror. Không sửa file JSON gốc; thay đổi hợp đồng phải thành phiên bản mới.
`config/ventilation_data_contract.json` là bằng chứng VENT-002 (snake_case), giữ nguyên.
