# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Nguyễn Thị Ngoc] - [2A202600405]
**Nhóm:** [67]
**Ngày:** [10/04/2026]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai vector có góc nhỏ giữa chúng, nghĩa là chúng cùng hướng và tương đồng về nội dung.

**Ví dụ HIGH similarity:**
- Sentence A: I love pizza.
- Sentence B: I adore pizza.
- Tại sao tương đồng: Cả hai đều thể hiện tình cảm tích cực với pizza, sử dụng từ đồng nghĩa.

**Ví dụ LOW similarity:**
- Sentence A: I love pizza.
- Sentence B: The weather is nice today.
- Tại sao khác: Hai câu nói về chủ đề hoàn toàn khác nhau, không liên quan.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity chỉ đo hướng của vector, không phụ thuộc vào độ dài, phù hợp cho text embeddings có độ dài khác nhau. Euclidean distance bị ảnh hưởng bởi magnitude, có thể không chính xác cho so sánh nội dung.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> num_chunks = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) ≈ ceil(22.11) = 23
> *Đáp án: 23 chunks*

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> num_chunks = ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks. Chunk count tăng vì overlap lớn hơn làm step nhỏ hơn. Muốn overlap nhiều hơn để duy trì ngữ cảnh liên tục giữa chunks, giảm mất thông tin ở biên.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Education Policy (Chính sách giáo dục - Quy định thi cử)

**Tại sao nhóm chọn domain này?**
> Domain này bao gồm các quy định về thi cử, phù hợp với retrieval trong giáo dục. Tài liệu có cấu trúc rõ ràng, dễ test chunking và retrieval strategies. Có sẵn 10 files .md chi tiết.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | 01_quy_dinh_chung.md | Local | 5689 | category: quy_dinh, topic: general_rules, source: local, language: vi |
| 2 | 02_ban_chi_dao_hoi_dong.md | Local | 13686 | category: quy_dinh, topic: governance, source: local, language: vi |
| 3 | 03_diem_thi_phong_thi.md | Local | 8420 | category: quy_dinh, topic: grading_policy, source: local, language: vi |
| 4 | 04_doi_tuong_dieu_kien.md | Local | 11514 | category: quy_dinh, topic: eligibility, source: local, language: vi |
| 5 | 05_trach_nhiem_thi_sinh.md | Local | 10925 | category: quy_dinh, topic: candidate_responsibility, source: local, language: vi |
| 6 | 06_cong_tac_de_thi.md | Local | 17122 | category: quy_dinh, topic: exam_administration, source: local, language: vi |
| 7 | 07_in_sao_van_chuyen_de.md | Local | 8407 | category: quy_dinh, topic: logistics, source: local, language: vi |
| 8 | 08_coi_thi.md | Local | 19706 | category: quy_dinh, topic: supervision, source: local, language: vi |
| 9 | 09_cham_thi.md | Local | 39471 | category: quy_dinh, topic: grading_practice, source: local, language: vi |
| 10 | 10_phuc_khao_tot_nghiep.md | Local | 69890 | category: quy_dinh, topic: rechecking, source: local, language: vi |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| category | string | quy_dinh | Phân loại domain chính sách thi cử |
| topic | string | supervision, grading_policy, rechecking | Tách nội dung chi tiết hơn để filter theo chủ đề |
| source | string | local | Xác định nguồn gốc tài liệu |
| language | string | vi | Hỗ trợ filter ngôn ngữ tiếng Việt |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| 01_quy_dinh_chung | FixedSizeChunker | 30 | 195.2 | Medium |
| 01_quy_dinh_chung | SentenceChunker | 11 | 398.3 | High |
| 01_quy_dinh_chung | RecursiveChunker | 649 | 5.7 | Low (over-split) |
| 02_ban_chi_dao_hoi_dong | FixedSizeChunker | 69 | 198.4 | Medium |
| 02_ban_chi_dao_hoi_dong | SentenceChunker | 10 | 1026.7 | High |
| 02_ban_chi_dao_hoi_dong | RecursiveChunker | 1529 | 5.7 | Low (over-split) |
| 09_cham_thi | FixedSizeChunker | 200 | 199.6 | Medium |
| 09_cham_thi | SentenceChunker | 44 | 678.7 | High |
| 09_cham_thi | RecursiveChunker | 4361 | 5.8 | Low (over-split) |

### Strategy Của Tôi

**Loại:** SentenceChunker

**Mô tả cách hoạt động:**
> Chunk theo ranh giới câu (split on ". ", "! ", "? "), group thành chunks với max_sentences_per_chunk=2. Preserve ngữ cảnh câu đầy đủ.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Domain education_policy có cấu trúc quy định với câu dài, SentenceChunker giữ nguyên ý nghĩa câu, tránh over-splitting như RecursiveChunker.

**Code snippet (nếu custom):**
```python
# Không custom, dùng built-in SentenceChunker với max_sentences_per_chunk=2
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| 01_quy_dinh_chung | best baseline (Sentence) | 11 | 398.3 | High - same as mine |
| 02_ban_chi_dao_hoi_dong | best baseline (Sentence) | 10 | 1026.7 | High - same as mine |
| 09_cham_thi | best baseline (Sentence) | 44 | 678.7 | High - same as mine |
| | **SentenceChunker (mine)** | same as baseline | same as baseline | High - preserves sentence context, avoids over-splitting |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi (Nguyễn Thị Ngọc) | SentenceChunker | 9/10 | Preserve context tốt, ít chunks | Chunk dài hơn, cost embedding cao |
| Vũ Đức Minh | RecursiveChunker (chunk_size=800) | 8.5 | Tôn trọng cấu trúc markdown, giữ ngữ cảnh pháp lý, avg length consistent 636 ký tự | Chunk count cao, có thể chậm hơn với tài liệu rất lớn |
| Thành viên khác | Custom chunking theo topic/section | 8 | Phù hợp với nội dung bài luật, giữ nguyên điều khoản | Phức tạp hơn khi hiện thực và dễ tạo chunk quá dài |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> SentenceChunker tốt nhất vì domain education_policy có nhiều quy định với câu dài, cần preserve context. RecursiveChunker over-split thành chunks quá nhỏ, kém hiệu quả.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Dùng regex r'(?<=[.!?])\s+' để split sentences. Group thành chunks với max_sentences_per_chunk. Strip whitespace và loại bỏ empty sentences.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Bắt đầu với separators theo thứ tự. Nếu chunk quá lớn, đệ quy với separator tiếp theo. Base case là khi không còn separator hoặc chunk đủ nhỏ.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Embed từng document, lưu vào list dict hoặc ChromaDB collection. Search bằng dot product với query embedding, sort descending.

**`search_with_filter` + `delete_document`** — approach:
> Filter records theo metadata trước, sau đó search. Delete bằng filter list hoặc ChromaDB delete where doc_id.

### KnowledgeBaseAgent

**`answer`** — approach:
> Retrieve top-k chunks từ store. Build prompt với context là list chunks. Call llm_fn với prompt để generate answer.

### Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\dell\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\python.exe
cachedir: .pytest_cache
rootdir: D:\ChuongTrinhHocTheoTungNgay\day7_10Apr\BaiNop\Day-07-Lab-Data-Foundations-main
plugins: anyio-4.13.0, langsmith-0.7.26
collected 42 items

... (all tests PASSED)
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score (mock embed) | Đúng? |
|------|-----------|-----------|---------|---------------------------|-------|
| 1 | Quy định chung về thi cử là gì? | Các quy định về thi tốt nghiệp. | high | -0.182 | No |
| 2 | Trách nhiệm của thí sinh trong kỳ thi. | Quyền lợi của thí sinh khi thi. | low | 0.003 | Yes |
| 3 | Cách chấm thi như thế nào? | Quy trình chấm điểm bài thi. | high | -0.042 | No |
| 4 | Điều kiện để phúc khảo bài thi? | Cách khiếu nại kết quả thi. | high | -0.010 | No |
| 5 | Công tác coi thi được quy định ra sao? | Nhiệm vụ của giám thị trong phòng thi. | high | 0.068 | No |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Pair 1 và 3 bất ngờ vì tôi dự đoán high, nhưng mock embedder cho điểm thấp/âm. Điều này cho thấy embedding mock có giới hạn lớn với câu tiếng Việt dài và định dạng câu hỏi. Trong thực tế, cần test với embedder thật để đánh giá similarity reviews đúng hơn.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Quy định chung về thi cử là gì? | Quy định chung bao gồm các nguyên tắc tổ chức thi, quyền và nghĩa vụ của các bên tham gia, đảm bảo công bằng và minh bạch. |
| 2 | Trách nhiệm của thí sinh trong kỳ thi? | Thí sinh phải tuân thủ quy định, không vi phạm quy chế thi, mang theo giấy tờ cần thiết, và chấp hành hướng dẫn của giám thị. |
| 3 | Cách chấm thi như thế nào? | Chấm thi theo thang điểm quy định, có giám khảo chấm độc lập, đảm bảo khách quan và chính xác. |
| 4 | Điều kiện để phúc khảo bài thi? | Phúc khảo trong thời hạn 10 ngày kể từ khi công bố kết quả, với lý do cụ thể và bằng chứng. |
| 5 | Công tác coi thi được quy định ra sao? | Giám thị coi thi, giám sát thí sinh, đảm bảo an toàn và không gian thi công bằng. |

### Kết quả của tôi

| # | Query | Top-3 Retrieved Docs | Top-1 Score | At least 1 relevant in top-3? |
|---|-------|----------------------|-------------|-----------------------------|
| 1 | Quy định chung về thi cử là gì? | 09_cham_thi.md, 01_quy_dinh_chung.md, 08_coi_thi.md | 0.479 | Yes |
| 2 | Trách nhiệm của thí sinh trong kỳ thi? | 10_phuc_khao_tot_nghiep.md, 06_cong_tac_de_thi.md (x2) | 0.343 | No |
| 3 | Cách chấm thi như thế nào? | 09_cham_thi.md, 10_phuc_khao_tot_nghiep.md (x2) | 0.348 | Yes |
| 4 | Điều kiện để phúc khảo bài thi? | 10_phuc_khao_tot_nghiep.md (x2), 09_cham_thi.md | 0.288 | Yes |
| 5 | Công tác coi thi được quy định ra sao? | 10_phuc_khao_tot_nghiep.md, 02_ban_chi_dao_hoi_dong.md, 01_quy_dinh_chung.md | 0.347 | Partly |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 3 / 5

### Nhận xét tổng quan

- Mức retrieval hiện tại là trung bình: nhiều truy vấn trả về tài liệu liên quan chung, nhưng không phải luôn đúng với truy vấn cụ thể.
- Top-3 thường bao gồm các tài liệu lớn như `09_cham_thi.md` và `10_phuc_khao_tot_nghiep.md`, nhưng một số query cần nội dung cụ thể hơn (ví dụ Query 2 và Query 5).
- Vì tất cả tài liệu đều dùng `category=quy_dinh`, việc filter theo category không thay đổi kết quả; để nâng retrieval cần metadata chi tiết hơn như `topic` hoặc `section`.
- Agent answer hiện tại chỉ là demo mock; để đánh giá thực chất cần kết nối LLM thực tế và verify context retrieved.

---

## 7. What I Learned

### Failure Analysis

**Query thất bại:** Query 2 "Trách nhiệm của thí sinh trong kỳ thi?".

**Tại sao thất bại?**
- Top-3 không tập trung vào tài liệu chuyên biệt về trách nhiệm thí sinh, mà ưu tiên các tài liệu chung về phúc khảo và công tác đề thi.
- Do `SentenceChunker` tạo chunks theo câu, nên một số chunk dài đã chứa nội dung lẫn lộn, làm similarity với query không đủ sắc nét.
- Metadata filter chưa được dùng, nên search chỉ dựa trên embedding mà không tận dụng category chi tiết.

**Đề xuất cải thiện:**
- Thêm metadata `doc_name` hoặc `section` để filter trước khi search.
- Dùng custom chunking theo mục lục hoặc header nếu tài liệu có cấu trúc markdown rõ ràng.
- Sử dụng `search_with_filter(query, metadata_filter={'category': 'quy_dinh'})` khi cần tách domain rộng nhỏ.

**Bài học rút ra:**
- Data strategy có ảnh hưởng mạnh hơn model embedding mock.
- Chunking phù hợp với domain là chìa khóa: `SentenceChunker` tốt hơn `RecursiveChunker` ở domain này, nhưng vẫn cần tuning để tránh chunk lẫn lộn.

---

## 8. Demo Reflection (5 điểm)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Thành viên khác dùng `RecursiveChunker(chunk_size=800)` để giữ cấu trúc markdown tốt hơn và giảm số lượng chunks, giúp so sánh rõ ưu nhược của chunking logic.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Nhóm khác dùng metadata filter kết hợp `category` và `language`, cho thấy filtering giúp tăng độ chính xác khi query quá chung chung.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ thêm metadata phân loại từng loại quy định (ví dụ `exam_rules`, `grading`, `supervision`) và chunk theo section để retrieval có độ chính xác cao hơn.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **88 / 100** |
