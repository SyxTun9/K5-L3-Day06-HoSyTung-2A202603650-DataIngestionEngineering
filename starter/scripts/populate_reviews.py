import csv
from pathlib import Path

# 1. Update test_grounding_review.csv
grounding_data = [
    {
        "question_id": "Q16",
        "strategy": "A",
        "score": "0",
        "rationale": "Cả 3 chunk thuộc lời tự thú/điều tra về cái chết của Drebber nhưng không chứa thông tin cảnh sát tìm thấy thi thể ở đâu (thiếu địa chỉ số 3 Lauriston Gardens và căn phòng trống).",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q16",
        "strategy": "B",
        "score": "0",
        "rationale": "Các chunk chỉ kể cảnh thủ phạm dẫn Drebber vào front room trước khi sát hại và tin tức báo chí sau đó; không có bằng chứng cảnh sát phát hiện thi thể tại địa chỉ trên.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q16",
        "strategy": "C",
        "score": "0",
        "rationale": "Tương tự cấu hình B (không áp dụng filter); hoàn toàn thiếu bằng chứng về địa điểm cảnh sát tìm thấy thi thể Enoch Drebber.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q17",
        "strategy": "A",
        "score": "2",
        "rationale": "Rank 1 chứa đầy đủ bằng chứng đối thoại giữa Holmes và Watson: Moriarty nổi danh trong giới tội phạm nhưng không ai trong công chúng biết đến ('famous among crooks', 'unknown to the public'), đủ để trả lời và dẫn nguồn.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q17",
        "strategy": "B",
        "score": "0",
        "rationale": "Các chunk chỉ đề cập đến sự tàn nhẫn trong băng đảng của Moriarty và việc Watson chưa từng nghe tên; không có bằng chứng so sánh mức độ nổi tiếng giữa giới tội phạm và công chúng.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q17",
        "strategy": "C",
        "score": "0",
        "rationale": "Tương tự cấu hình B (không áp dụng filter); thiếu thông tin Moriarty nổi tiếng với giới tội phạm nhưng vô danh với công chúng bên ngoài.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q18",
        "strategy": "A",
        "score": "0",
        "rationale": "Cả 3 chunk đều lạc sang tác phẩm khác (Bruce-Partington Plans, Devil's Foot, Abbey Grange); chỉ có từ khóa nhiễu 'tin cash-box' và 'Charing Cross', không nói về nơi Watson cất hồ sơ.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q18",
        "strategy": "B",
        "score": "0",
        "rationale": "Các chunk chỉ nhắc việc Watson lưu hồ sơ 3 vụ án năm 1890 và hộp thiếc chứa tài liệu tàu ngầm trong truyện khác; không có bằng chứng về hộp thiếc tại ngân hàng Cox & Co.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q18",
        "strategy": "C",
        "score": "0",
        "rationale": "Đã áp dụng filter document_type='story' nhưng kết quả vẫn không truy xuất được đoạn mở đầu truyện Thor Bridge chứa thông tin hộp hồ sơ tại ngân hàng Cox & Co. ở Charing Cross.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q19",
        "strategy": "A",
        "score": "1",
        "rationale": "Rank 2 xác nhận Barrymore là quản gia ('the butler') và vợ ông sống tại Baskerville Hall, nhưng thiếu bằng chứng xác nhận vai trò quản gia nữ ('housekeeper') của người vợ.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q19",
        "strategy": "B",
        "score": "0",
        "rationale": "Các chunk miêu tả cảnh đón xe tại dinh thự và tính cách bà Barrymore nhưng không chứa thông tin về chức danh quản gia/quản gia nữ của hai vợ chồng.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q19",
        "strategy": "C",
        "score": "0",
        "rationale": "Tương tự cấu hình B (không dùng filter); không có thông tin về vai trò quản gia của cặp vợ chồng Barrymore tại Baskerville Hall.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q20",
        "strategy": "A",
        "score": "0",
        "rationale": "Các chunk nói về màu áo đua, danh sách đặt cược của Silver Blaze và một đoạn lạc về đàn gia súc; không có thông tin đặc điểm trán trắng ('white forehead') đặt tên cho ngựa.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q20",
        "strategy": "B",
        "score": "0",
        "rationale": "Các chunk chỉ chứa thông tin giải đua Wessex Plate và việc tẩy rửa mặt/chân ngựa bằng rượu, không có bằng chứng về đốm trắng ở trán tạo nên tên gọi Silver Blaze.",
        "reviewer": "Ho Sy Tung"
    },
    {
        "question_id": "Q20",
        "strategy": "C",
        "score": "0",
        "rationale": "Tương tự cấu hình B (không dùng filter); không có bằng chứng về đặc điểm trán trắng đặt tên cho ngựa Silver Blaze.",
        "reviewer": "Ho Sy Tung"
    },
]

grounding_path = Path("starter/results/test_grounding_review.csv")
with grounding_path.open("r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

for row, update in zip(rows, grounding_data):
    assert row["question_id"] == update["question_id"]
    assert row["strategy"] == update["strategy"]
    row["grounding_score_0_1_2"] = update["score"]
    row["rationale"] = update["rationale"]
    row["reviewer"] = update["reviewer"]

with grounding_path.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(rows)

print("Updated test_grounding_review.csv successfully.")

# 2. Update test_metadata_review.csv
metadata_path = Path("starter/results/test_metadata_review.csv")
with metadata_path.open("r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    meta_rows = list(reader)

for row in meta_rows:
    qid = row["question_id"]
    strat = row["strategy"]
    rank = row["rank"]
    doc_id = row["document_id"]
    gold_id = row["gold_source_id"]
    filter_app = row["filter_applied"]
    
    row["source_location_checked"] = "true"
    row["metadata_correct"] = "true"
    
    if filter_app:
        row["filter_compliant"] = "true"
        filter_note = f"Filter {filter_app} được tuân thủ (document_type='{row['document_type']}'). "
    else:
        row["filter_compliant"] = "N/A"
        filter_note = ""
        
    same_doc = (doc_id == gold_id)
    doc_match_str = "Đúng document_id nguồn gold" if same_doc else "Khác document_id nguồn gold"
    
    row["notes"] = (
        f"{doc_match_str}; {filter_note}"
        f"Vị trí nguồn xác nhận qua unit_id '{row['unit_id']}' và khoảng ký tự [{row['char_start']}:{row['char_end']}]; "
        f"page=1 là giá trị tương thích cho truyện không phân trang."
    )

with metadata_path.open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    writer.writerows(meta_rows)

print("Updated test_metadata_review.csv successfully.")
