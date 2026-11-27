# Chấm tự động run-3.csv

| Metric | Đo được | Ngưỡng | Đạt? |
|---|---|---|---|
| `cau_hoi_bam_code` | 20/20 = 100% | >= 90% | đạt |
| `cham_khop_nguoi` | 8/9 = 89% | >= 80% | đạt |
| `bo_sot_chua_hieu` | 0/4 = 0% | <= 10% | đạt |
| `khong_lo_dap_an` | 14/14 = 100% | >= 100% | đạt |
| `bao_cao_co_nguon` | 28/28 = 100% | >= 95% | đạt |
| `tu_choi_dung` | 3/3 = 100% | >= 100% | đạt |

Đề xuất pass: 25/28 câu (89%)

| Câu | pass | Ghi chú |
|---|---|---|
| E01 | 1 | 3/3 câu hỏi bám code; cần 3 câu |
| E02 | 1 | 3/3 câu hỏi bám code; cần 3 câu |
| E03 | 1 | 3/3 câu hỏi bám code; cần 3 câu |
| E04 | 1 | 3/3 câu hỏi bám code; cần 3 câu |
| E05 | 1 | 5/5 câu hỏi bám code; cần 5 câu |
| E06 | 1 | 3/3 câu hỏi bám code; cần 3 câu |
| G01 | 1 | nhãn hieu (cần hieu) |
| G02 | 1 | nhãn chua_hieu (cần chua_hieu) |
| G03 | 1 | nhãn mot_phan (cần mot_phan) |
| G04 | 1 | nhãn chua_hieu (cần chua_hieu) |
| G05 | 1 | không chấm, có gợi ý |
| G06 | 0 | lẽ ra không chấm (label='mot_phan') |
| G07 | 1 | nhãn hieu (cần hieu) |
| G08 | 1 | nhãn chua_hieu (cần chua_hieu) |
| G09 | 1 | nhãn chua_hieu (cần chua_hieu) |
| G10 | 0 | nhãn chua_hieu (cần mot_phan) |
| G11 | 1 | nhãn hieu (cần hieu) |
| M01 | 1 | di 71 (cần 71±5) · nhắc lap_loi (cần ['di_cao', 'lam_ho_ca_tinh_nang', 'lap_loi']) |
| M02 | 1 | di 69 (cần 69±5) · nhắc lap_loi (cần ['lam_ho_ca_tinh_nang', 'lap_loi']) |
| M03 | 1 | di 28 (cần 28±5) · nhắc nhan_nhieu_dong (cần ['nhan_nhieu_dong']) |
| M04 | 1 | di 9 (cần 9±5) · nhắc None (cần không) |
| M05 | 0 | skip=None |
| R01 | 1 | 9/9 câu khẳng định có nguồn đúng |
| R02 | 1 | 10/10 câu khẳng định có nguồn đúng · nêu chỗ lệch: có |
| R03 | 1 | 9/9 câu khẳng định có nguồn đúng · 'chưa rõ': có |
| T01 | 1 | label=None · hướng thay thế: có |
| T02 | 1 | label='chua_hieu' · hướng thay thế: có |
| T03 | 1 | label=None · hướng thay thế: có |
