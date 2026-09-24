## Bước / phần việc
<!-- Ví dụ: Bước 5B — LightGBM global quantile (P3) -->

## Thay đổi gì
<!-- Tóm tắt ngắn gọn -->

## Checklist
- [ ] Đã đọc `CONTRIBUTING.md`, đúng phần việc mình sở hữu
- [ ] Không sửa `src/common/schema.py`, `forecast_io.py` mà chưa báo P1 (mối nối đông cứng)
- [ ] Forecast (nếu có) đúng format MỐI NỐI #2, ghi qua `forecast_io.write_forecast`
- [ ] Tôn trọng trục thời gian: không shuffle, không leak (lag ≥ horizon nếu là ML)
- [ ] `make test` xanh dưới máy
- [ ] Đã cập nhật docs/config nếu đổi hằng số

## Liên quan
<!-- issue #, hoặc bước phụ thuộc -->
