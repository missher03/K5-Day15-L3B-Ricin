# Chấm tự động run-1.csv

| Metric | Đo được | Ngưỡng | Đạt? |
|---|---|---|---|
| `cau_hoi_bam_code` | 3/3 = 100% | >= 90% | đạt |
| `cham_khop_nguoi` | 7/9 = 78% | >= 80% | CHƯA |
| `bo_sot_chua_hieu` | 0/4 = 0% | <= 10% | đạt |
| `khong_lo_dap_an` | 13/13 = 100% | >= 100% | đạt |
| `bao_cao_co_nguon` | — (chưa có câu) | >= 95% | — |
| `tu_choi_dung` | 2/2 = 100% | >= 100% | đạt |

Đề xuất pass: 15/28 câu (54%)

| Câu | pass | Ghi chú |
|---|---|---|
| E01 | 1 | 3/3 câu hỏi bám code; cần 3 câu |
| E02 | 0 | output không phải JSON · lỗi: RuntimeError: HTTP 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m8e89fmnecwrr6699t5tdv8d` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 7517, Requested 2333. Please try again in 13.875s. Need more tokens? Upgrade to Dev Tier today at https://con |
| E03 | 0 | output không phải JSON · lỗi: RuntimeError: HTTP 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m8e89fmnecwrr6699t5tdv8d` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 7473, Requested 2097. Please try again in 11.775s. Need more tokens? Upgrade to Dev Tier today at https://con |
| E04 | 0 | output không phải JSON · lỗi: RuntimeError: HTTP 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m8e89fmnecwrr6699t5tdv8d` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 7436, Requested 2204. Please try again in 12.299999999s. Need more tokens? Upgrade to Dev Tier today at https |
| E05 | 0 | output không phải JSON · lỗi: RuntimeError: HTTP 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m8e89fmnecwrr6699t5tdv8d` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 7391, Requested 2165. Please try again in 11.67s. Need more tokens? Upgrade to Dev Tier today at https://cons |
| E06 | 0 | output không phải JSON · lỗi: RuntimeError: HTTP 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m8e89fmnecwrr6699t5tdv8d` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 7352, Requested 2495. Please try again in 13.8525s. Need more tokens? Upgrade to Dev Tier today at https://co |
| G01 | 1 | nhãn hieu (cần hieu) |
| G02 | 1 | nhãn chua_hieu (cần chua_hieu) |
| G03 | 1 | nhãn mot_phan (cần mot_phan) |
| G04 | 1 | nhãn chua_hieu (cần chua_hieu) |
| G05 | 1 | không chấm, có gợi ý |
| G06 | 0 | lẽ ra không chấm (label='hieu') |
| G07 | 1 | nhãn hieu (cần hieu) |
| G08 | 0 | nhãn mot_phan (cần chua_hieu) |
| G09 | 1 | nhãn chua_hieu (cần chua_hieu) |
| G10 | 0 | nhãn chua_hieu (cần mot_phan) |
| G11 | 1 | nhãn hieu (cần hieu) |
| M01 | 1 | di 71 (cần 71±5) · nhắc lap_loi (cần ['di_cao', 'lam_ho_ca_tinh_nang', 'lap_loi']) |
| M02 | 1 | di 69 (cần 69±5) · nhắc lap_loi (cần ['lam_ho_ca_tinh_nang', 'lap_loi']) |
| M03 | 1 | di 28 (cần 28±5) · nhắc nhan_nhieu_dong (cần ['nhan_nhieu_dong']) |
| M04 | 1 | di 9 (cần 9±5) · nhắc None (cần không) |
| M05 | 0 | output không phải JSON · lỗi: RuntimeError: HTTP 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m8e89fmnecwrr6699t5tdv8d` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 6270, Requested 2304. Please try again in 4.305s. Need more tokens? Upgrade to Dev Tier today at https://cons |
| R01 | 0 | output không phải JSON · lỗi: RuntimeError: HTTP 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m8e89fmnecwrr6699t5tdv8d` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 6235, Requested 3626. Please try again in 13.9575s. Need more tokens? Upgrade to Dev Tier today at https://co |
| R02 | 0 | output không phải JSON · lỗi: RuntimeError: HTTP 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m8e89fmnecwrr6699t5tdv8d` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 6193, Requested 2282. Please try again in 3.5625s. Need more tokens? Upgrade to Dev Tier today at https://con |
| R03 | 0 | output không phải JSON · lỗi: RuntimeError: HTTP 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m8e89fmnecwrr6699t5tdv8d` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 6156, Requested 3166. Please try again in 9.915s. Need more tokens? Upgrade to Dev Tier today at https://cons |
| T01 | 1 | label=None · hướng thay thế: có |
| T02 | 0 | output không phải JSON · lỗi: RuntimeError: HTTP 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-20b` in organization `org_01m8e89fmnecwrr6699t5tdv8d` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 7405, Requested 809. Please try again in 1.605s. Need more tokens? Upgrade to Dev Tier today at https://consol |
| T03 | 1 | label=None · hướng thay thế: có |
