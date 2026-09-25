# RAG Evaluation Results — Nhóm IpadKids (Chủ đề: Giao Thông)

## Run information

| Field                              | Value                                      |
| ---------------------------------- | ------------------------------------------ |
| Evaluation date                    | 2026-09-25                                 |
| Framework and version              | ragas 0.4.3                                |
| Evaluator model                    | Chờ cấu hình sau khi indexing hoàn tất     |
| Generator model                    | Cấu hình trong .env (LLM_PROVIDER)         |
| Embedding model                    | BAAI/bge-m3 (sentence-transformers)        |
| Corpus version/commit              | main — 3 legal + 5 news (Giao Thông)       |
| Golden dataset size                | 15 câu hỏi                                 |
| `top_k`                            | 5                                          |
| Fallback threshold and calibration | SCORE_THRESHOLD = 0.3 (chưa hiệu chỉnh)   |

## Configurations

- **Config A — dense-only:** Chỉ dùng semantic search (BAAI/bge-m3 + ChromaDB cosine), không RRF, không fallback.
- **Config B — hybrid + RRF:** Dense + BM25 kết hợp qua Reciprocal Rank Fusion, có PageIndex fallback khi cosine score < 0.3.

Hai config dùng cùng golden dataset, generator, evaluator, prompt và `top_k=5`; chỉ thay retrieval strategy.

## Overall scores

> Kết quả sẽ được cập nhật sau khi hoàn tất indexing và chạy đánh giá với ragas.
> Pipeline đang ở giai đoạn chuẩn bị (indexing chưa chạy vì cần API key LLM).

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |      N/A |      N/A |       N/A |
| Answer relevance  |      N/A |      N/A |       N/A |
| Context recall    |      N/A |      N/A |       N/A |
| Context precision |      N/A |      N/A |       N/A |
| **Average**       |      N/A |      N/A |       N/A |

## A/B comparison

- Cấu hình tốt hơn: Dự kiến Config B (hybrid + RRF) vì BM25 tốt với tên văn bản pháp luật, số nghị định và từ khóa chính xác.
- Evidence: Sẽ cập nhật sau khi có kết quả ragas.
- Trade-off về latency/cost: Config B chạy chậm hơn do cần embed + BM25 song song; chi phí API tương đương vì dùng chung generator.

## Worst performers

> Mục này sẽ được điền sau khi chạy đánh giá đủ 15 câu hỏi golden dataset.

| # | Question                              | Config   | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause                    |
|--:|---------------------------------------|----------|-------------:|----------:|-------:|----------:|---------------|-------------------------------|
| 1 | Chưa xác định (cần chạy evaluation)   | Config A |          N/A |       N/A |    N/A |       N/A | retrieval     | Indexing chưa hoàn tất        |
| 2 | Chưa xác định (cần chạy evaluation)   | Config B |          N/A |       N/A |    N/A |       N/A | retrieval     | Indexing chưa hoàn tất        |
| 3 | Chưa xác định (cần chạy evaluation)   | Config B |          N/A |       N/A |    N/A |       N/A | data          | Bài viết 404 trong news corpus |

## Recommendations

| Priority | Action                                      | Evidence from failure analysis              | Expected impact                    | How to verify                        |
|---------:|---------------------------------------------|---------------------------------------------|------------------------------------|--------------------------------------|
|        1 | Loại bỏ file news bị 404 khỏi corpus        | article_03/04/05 nội dung rất ngắn (<200 ký tự sau lọc) | Tăng precision, giảm noise | Chạy lại acceptance test + eval |
|        2 | Hiệu chỉnh SCORE_THRESHOLD trên in/out domain | Threshold 0.3 chưa được calibrate           | Giảm false fallback                | So sánh fallback rate A vs B         |
|        3 | Tăng chunk overlap lên 100                  | Câu hỏi về văn bản pháp luật cần context rộng hơn | Tăng context recall            | Đánh giá lại context recall metric   |

## Bonus experiments

| Experiment                     | Baseline    | Metric delta | Latency/cost delta | Conclusion                                   |
|--------------------------------|-------------|-------------:|-------------------:|----------------------------------------------|
| Chunk size 500 vs 800          | Config B    |          N/A |                N/A | Cần chạy sau khi có kết quả cơ sở            |
| BAAI/bge-m3 vs text-embedding  | Config B    |          N/A |                N/A | Cần so sánh sau khi có API key               |
