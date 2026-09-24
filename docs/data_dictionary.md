# Từ điển dữ liệu — M5 Walmart

Bộ dữ liệu: [M5 Forecasting - Accuracy (Kaggle)](https://www.kaggle.com/competitions/m5-forecasting-accuracy/data).
30.490 chuỗi = 3.049 sản phẩm × 10 cửa hàng (3 bang CA/TX/WI, 3 ngành Foods/Household/Hobbies),
~1.941 ngày.

## File thô (data/raw/ — KHÔNG commit)

### `sales_train_evaluation.csv` (dùng chính)
Wide: mỗi hàng 1 chuỗi. Có actuals tới **d_1941** (đủ cho val + test nội bộ).
| Cột | Ý nghĩa |
|---|---|
| `id` | định danh chuỗi = `series_id` (vd `FOODS_1_001_CA_1_evaluation`) |
| `item_id, dept_id, cat_id` | sản phẩm / phòng ngành / ngành |
| `store_id, state_id` | cửa hàng / bang |
| `d_1` … `d_1941` | sales theo ngày (cột) |

> `sales_train_validation.csv` (tới d_1913) KHÔNG dùng — evaluation bao trùm.

### `calendar.csv`
| Cột | Ý nghĩa |
|---|---|
| `d` | nhãn ngày `d_1`.. ; `d_int` = phần số |
| `date` | ngày dương lịch |
| `wm_yr_wk` | mã tuần Walmart (join giá) |
| `wday, month, year` | thứ (1=Sat..7=Fri), tháng, năm |
| `event_name_1, event_type_1` | lễ/sự kiện (→ `is_event`) |
| `snap_CA, snap_TX, snap_WI` | ngày SNAP theo bang (→ `snap` theo state của chuỗi) |

### `sell_prices.csv`
| Cột | Ý nghĩa |
|---|---|
| `store_id, item_id` | khoá sản phẩm–cửa hàng |
| `wm_yr_wk` | tuần |
| `sell_price` | giá bán tuần đó (join theo store+item+wm_yr_wk) |

## Bảng `data_long.parquet` (sinh ra — data/processed/, KHÔNG commit)
Định dạng LONG chuẩn (MỐI NỐI #1, xem `src/common/schema.py::LONG_COLS`):
`series_id, date, d_int, sales, wday, month, is_event, snap, sell_price, segment` (+ `event_name_1`).

## Artifact deterministic (configs/ — CÓ commit)
| File | Nội dung |
|---|---|
| `configs/segment_labels.parquet` | nhãn nhóm SBC + ADI/CV²/zero_rate cho TOÀN BỘ 30.490 chuỗi |
| `configs/sample_ids.csv` | danh sách chuỗi mẫu phân tầng (seed 42, ~3.474 chuỗi) |

## Phân bố nhóm demand (toàn bộ 30.490)
| Nhóm | Số chuỗi | Tỷ lệ | Zero-rate TB |
|---|---:|---:|---:|
| smooth | 980 | 3.2% | 0.14 |
| erratic | 494 | 1.6% | 0.17 |
| intermittent | 23.096 | 75.7% | 0.74 |
| lumpy | 5.920 | 19.4% | 0.60 |

→ 95% là intermittent + lumpy (chi phối lấy mẫu & tổng hợp).
