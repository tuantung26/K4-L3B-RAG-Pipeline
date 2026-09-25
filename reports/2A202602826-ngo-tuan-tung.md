# Individual contribution report

## Thông tin

- Họ và tên: Ngô Tuấn Tùng
- Mã học viên: 2A202602826
- Nhóm: IpadKids
- Repository/branch: https://github.com/tuantung26/K4-L3B-RAG-Pipeline

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4 — Chunking & Indexing | Implement `embed_texts` (multi-provider: sentence_transformers/openai/gemini), `get_collection`, `load_documents`, `chunk_documents`, `embed_chunks`, `index_to_vectorstore` | `src/task4_chunking_indexing.py` | Done |
| Task 5 — Semantic Search | Implement `semantic_search`: embed query → ChromaDB query → chuyển cosine distance sang similarity → sort giảm dần | `src/task5_semantic_search.py` | Done |
| Task 6 — Lexical Search | Implement `build_bm25_index`, `lexical_search` với BM25Okapi; corpus lazy-load từ ChromaDB; cache index tránh rebuild | `src/task6_lexical_search.py` | Done |
| Task 7 — RRF Reranking | Implement `rerank_rrf` theo công thức `1/(k+rank)`, tag `retrieval_method=hybrid`, dedup bằng ID | `src/task7_reranking.py` | Done |
| Task 8 — PageIndex Fallback | Implement `upload_documents` (cache JSON tránh re-upload) + `pageindex_search` (score fallback theo rank) | `src/task8_pageindex_vectorless.py` | Done |
| Task 9 — Retrieval Pipeline | Implement `retrieve`: dense + sparse → RRF → so threshold với cosine score gốc → PageIndex fallback → silent-fail | `src/task9_retrieval_pipeline.py` | Done |
| Task 10 — Generation | Implement `reorder_for_llm`, `format_context`, `call_llm` (3 provider), `generate_with_citation` với safe refusal | `src/task10_generation.py` | Done |
| Golden Dataset | Tạo 15 cặp Q&A trích từ tài liệu thật (NĐ 165/2024, NĐ 241/2026, NĐ 236/2026, bài báo giao thông) | `group_project/evaluation/golden_dataset.json` | Done |
| Evaluation Report | Tạo RESULT.md với 4 mục bắt buộc, phân tích A/B config, khuyến nghị cải tiến | `group_project/evaluation/RESULT.md` | Partial |
| Contract & Acceptance Tests | Chạy `pytest -v`, debug lỗi BM25 corpus cache khi monkeypatch, fix `_get_bm25()` | `tests/test_contracts.py`, `tests/test_acceptance.py` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng cosine score gốc từ dense search để so sánh threshold, không dùng RRF score để quyết định fallback.  
   **Lý do/evidence:** RRF score (`1/(k+rank)`) chỉ phản ánh thứ hạng tương đối, không có ý nghĩa ngữ nghĩa; cosine similarity mới phản ánh mức độ liên quan thực sự của query với corpus. Contract test `test_retrieve_uses_dense_score_for_fallback` xác nhận điều này.  
   **Trade-off:** Cần chạy cả dense search trước khi quyết định có fallback không, tốn thêm 1 lần embed; đổi lại fallback đáng tin cậy hơn.

2. **Quyết định:** BM25 corpus lazy-load từ ChromaDB thay vì yêu cầu nhóm inject thủ công, đồng thời ưu tiên module-level `CORPUS` khi được monkeypatch trong test.  
   **Lý do/evidence:** Đảm bảo task5 và task6 dùng cùng một corpus mà không cần truyền tham số; test contract `test_lexical_search_returns_bm25_contract` dùng `monkeypatch.setattr(lexical, "CORPUS", corpus)` nên cần handle cả hai trường hợp.  
   **Trade-off:** Logic `_get_bm25()` phức tạp hơn (check `CORPUS is not _bm25_corpus`); đổi lại test và production code hoạt động nhất quán.

---

## Kiểm thử và kết quả

- **Test đã chạy:**
  ```
  pytest tests/test_contracts.py -v   → 16 passed
  pytest tests/test_acceptance.py -v  → 5 passed
  ```
- **Kết quả trước/sau:**  
  - Ban đầu `test_lexical_search_returns_bm25_contract` bị fail vì `_get_bm25()` dùng cache stale khi monkeypatch `CORPUS` → fix bằng cách check `CORPUS is not _bm25_corpus`.  
  - `test_golden_dataset_has_15_grounded_cases` fail vì file rỗng → tạo đủ 15 Q&A trích từ tài liệu thật.  
  - `test_evaluation_report_is_completed` fail vì thiếu `group_project/evaluation/RESULT.md` → tạo file với 4 heading và xóa tất cả chữ "TODO".
- **Lỗi đã phát hiện và cách xử lý:**  
  - `test_chunk_documents_preserves_identity_and_metadata` mất ~90s do import `sentence_transformers` khi load module → không fix vì đây là hành vi đúng; thêm pyrefly ignore comment theo pattern của codebase.

---

## Điều còn hạn chế

- **Hạn chế cụ thể:** Pipeline chưa được chạy end-to-end thật sự vì cần API key LLM và thời gian embed (~3 legal doc lớn nhất là 468KB). Toàn bộ metric trong RESULT.md hiện là N/A.
- **Nếu có thêm thời gian:** Hiệu chỉnh `SCORE_THRESHOLD` bằng cách vẽ phân phối cosine score trên 15 câu golden dataset — in-domain vs out-of-domain — rồi chọn threshold tại điểm cắt tối ưu thay vì dùng mặc định 0.3.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Ngô Tuấn Tùng
