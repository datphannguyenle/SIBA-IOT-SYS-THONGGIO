# VENT-006 — Rollback

## Phạm vi được phép

Chỉ xóa hai object do CHÍNH lần thực thi VENT-006 tạo ra và đã ghi trong
`deploy/thingsboard/vent006_manifest.json`. Không bao giờ xóa object có sẵn từ trước.

## Thứ tự

1. Đọc lại dashboard theo ID trong manifest; tiêu đề phải đúng `DB-30-VEN-DETAIL-V1-DEMO`.
2. `DELETE /api/dashboard/{id}`.
3. Quét mọi dashboard của tenant: không còn widget nào có `typeFullFqn` bắt đầu bằng
   `tenant.siba_vent_demo.`.
4. Đọc lại widget type theo ID; fqn phải đúng `siba_vent_demo.vent_demo_view`.
5. `DELETE /api/widgetType/{id}`.

ID/tiêu đề/fqn không khớp manifest -> DỪNG, không xóa.

## Lệnh

```bash
cd deploy/thingsboard
python3 rollback_vent_demo.py                    # chạy thử: chỉ GET, in kế hoạch
python3 rollback_vent_demo.py --confirm-delete   # thực thi, ghi evidence/vent006_rollback_log.json
python3 deploy_vent_demo.py regression           # xác nhận object được bảo vệ vẫn nguyên vẹn
```

Rào chắn `GuardedTB` chỉ cho `DELETE` với đúng các ID trong manifest; mọi đường dẫn khác bị
chặn trước khi gửi.

## Rollback tự động trong lúc thực thi

Nếu xác minh widget type ngay sau khi tạo thất bại, `deploy_vent_demo.py execute` tự xóa
đúng widget type vừa tạo rồi dừng. Lỗi xác minh dashboard không tự rollback: script dừng
và báo, người vận hành chạy lệnh trên sau khi xem lại.

## Trạng thái

Chưa thực hiện rollback nào.
