# Starter · Sherlock Holmes + Chroma

Đây là pipeline đã hiện thực cho corpus Sherlock Holmes trong `../sherlock-master/`. Pipeline dùng Chroma persistent local và embedding local; không cần Docker hay API key. Các file PostgreSQL/pgvector còn trong starter là phương án hạ tầng khác, không được `src.run` sử dụng.

## Yêu cầu

- Python 3.11–3.14 (đã chạy với Python 3.13.15)
- Mạng ở lần đầu để cài package và tải model `all-MiniLM-L6-v2`
- Đủ dung lượng đĩa cho model và database Chroma

## Cài đặt trên Windows PowerShell

Chạy từ thư mục `starter/`:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Chroma `1.5.9` và các dependency được khóa trong `requirements.txt`. Chroma dùng `all-MiniLM-L6-v2` mặc định, chạy local, 384 chiều. Lần đầu có thể mất thời gian tải model.

## Corpus và manifest

Văn bản gốc nằm trong `../sherlock-master/stories/` và `../sherlock-master/novels/`; manifest là `data/corpus_manifest.json`. Mỗi tệp là một đơn vị văn bản không phân trang. Manifest ghi source ID, đường dẫn, số ký tự sau chuẩn hóa và thông tin nguồn/quyền. Không cần sao chép corpus vào `starter/data/`.

## Chạy pipeline

Từ `starter/`, với `.venv` đang bật:

```powershell
python -m src.run
```

Lệnh này đọc manifest và nạp ba collection vào `chroma_db/`:

- **A:** chunk cố định 1.000 ký tự, overlap 150.
- **B:** gom theo đoạn, tối đa 1.000 ký tự; đoạn dài được chia nhỏ.
- **C:** cùng chunk với B; khi câu benchmark có filter, tìm kiếm C áp dụng `document_type` (`story` hoặc `novel`).

Chạy lại sẽ upsert theo ID ổn định và loại chunk cũ của các tài liệu được nạp lại. `chroma_db/` nằm trong `.gitignore`.
Thời gian tổng mỗi lần ingest được in ra console và append vào `results/ingest_runs.csv`.

## Benchmark

Benchmark đã kiểm tra nằm tại `data/benchmark_questions.csv` (20 câu: 15 dev / 5 test). Trace đầy đủ và metric được ghi dưới `results/`.

Chạy dev trước:

```powershell
python -m src.evaluate --split dev
```

Xem `results/dev_retrieval_metrics.csv` và khóa tiêu chí/cấu hình trước khi xem test. Chỉ sau đó chạy test một lần:

```powershell
python -m src.evaluate --split test
```

Các file kết quả chính:

- `results/dev_traces.jsonl`, `results/test_traces.jsonl`: top-3 gồm text, score, metadata và nhãn match tự động theo gold source/evidence.
- `results/dev_retrieval_metrics.csv`, `results/test_retrieval_metrics.csv`: Hit@1, Evidence Hit@3 và filter compliance của C.
- `results/test_grounding_review.csv`, `results/test_metadata_review.csv`: audit thủ công test.
- `results/chunk_coherence_review.csv`: mẫu 10 vị trí nguồn chung cho A/B/C.

Metric match evidence tự động không thay thế nhãn grounding/chunk coherence thủ công. Ghi nhận lỗi, giả thuyết, thời gian, chi phí và giới hạn trong báo cáo; không tinh chỉnh theo test rồi coi test là holdout độc lập.

## Tạo lại bảng coherence

Sau khi ingest, có thể tạo lại mẫu 10 vị trí cố định bằng:

```powershell
python scripts/prepare_coherence_review.py
```

Lệnh này tạo lại `results/chunk_coherence_review.csv`; hãy lưu nhãn thủ công trước khi chạy lại.
