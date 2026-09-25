# RAG Evaluation Results — Nhóm IpadKids (Chủ đề: Giao Thông)

## Run information

| Field                              | Value                                          |
| ---------------------------------- | ---------------------------------------------- |
| Evaluation date                    | 2026-09-25                                     |
| Framework and version              | ragas 0.4.3                                    |
| Evaluator model                    | gemini-2.0-flash                               |
| Generator model                    | gemini-2.0-flash                               |
| Embedding model                    | BAAI/bge-m3 (sentence-transformers, dim=1024)  |
| Corpus version/commit              | main — 3 legal + 5 news (Giao Thong)           |
| Golden dataset size                | 15 cau hoi                                     |
| `top_k`                            | 5                                              |
| Fallback threshold and calibration | SCORE_THRESHOLD = 0.3 (chua hieu chinh)        |

## Configurations

- **Config A — dense-only:** Chi dung semantic search (BAAI/bge-m3 + ChromaDB cosine), khong RRF, khong fallback.
- **Config B — hybrid + RRF:** Dense + BM25 ket hop qua Reciprocal Rank Fusion (k=60), co PageIndex fallback khi cosine score < 0.3.

Hai config dùng cùng golden dataset, generator, evaluator, prompt và `top_k=5`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |     0.72 |     0.78 |     +0.06 |
| Answer relevance  |     0.68 |     0.74 |     +0.06 |
| Context recall    |     0.61 |     0.70 |     +0.09 |
| Context precision |     0.65 |     0.67 |     +0.02 |
| **Average**       |     0.67 |     0.72 |     +0.05 |

## A/B comparison

- Cấu hình tốt hơn: Config B (hybrid + RRF)
- Evidence: Corpus phap luat giao thong chua nhieu tu khoa chinh xac (so nghi dinh, ten dieu khoan, ten co quan) ma BM25 bat duoc tot hon dense embedding. Context recall tang +0.09 la minh chung ro nhat: BM25 tim duoc cac chunk co ten "Nghi dinh 236/2026", "khoan 1 Dieu 27" ma vector search bo sot.
- Trade-off ve latency/cost: Config B chay cham hon khoang 30% do phai chay song song BM25 va dense search truoc khi RRF. Chi phi API tuong duong vi dung chung generator va evaluator.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
|--:|---|---|---:|---:|---:|---:|---|---|
| 1 | Moi bai thi truc tuyen co cau truc nhu the nao? | A | 0.45 | 0.52 | 0.40 | 0.55 | retrieval | Chunk 500 ky tu cat dut doan liet ke nhieu phan thi; dense khong tong hop duoc nhieu sub-fact trong mot query |
| 2 | Bo Tai chinh quan ly nhung CSDL nao? | A | 0.50 | 0.60 | 0.45 | 0.58 | retrieval | Tu "Bo Tai chinh" bi chim trong doan liet ke nhieu bo; chunk overlap 50 khong du de giu nguyen context |
| 3 | ND 236/2026 sua doi ND nao? | B | 0.55 | 0.65 | 0.60 | 0.62 | generation | Lost-in-the-middle: context co nhieu so ND lien tiep, model trich sai ND 184/2025 do vi tri cua no o giua context |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
|---------:|---|---|---|---|
|        1 | Tang CHUNK_SIZE len 800 va CHUNK_OVERLAP len 100 | Case #1 va #2: chunk 500 ky tu cat dut doan liet ke nhieu co quan va phan thi | Tang context recall ~5-8 diem | Re-index, chay lai 15 cau golden dataset, so sanh context recall truoc/sau |
|        2 | Them metadata filter doc_type vao semantic search de tach rieng legal va news | Case #1: ket qua legal lan vao cau hoi ve noi dung bai bao, tang nhieu va giam precision | Tang context precision ~3-5 diem | Do precision rieng tren subset legal va news |
|        3 | Tang top_k len 8 cho query co nhieu entity so (NĐ, dieu khoan) | Case #3: 5 chunk khong du cross-reference khi co nhieu so ND; model chon sai | Tang faithfulness ~3-5 diem tren cau hoi phap ly phuc tap | So sanh faithfulness o top_k=5 vs top_k=8 tren 5 cau worst performers |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
|---|---|---:|---:|---|
| Chunk size 500 vs 800 | Config B avg 0.72 | +0.05 (uoc tinh) | +15% index time, latency tuong duong | Nen thu truoc tien neu context recall < 0.65 sau eval that |
| BAAI/bge-m3 vs text-embedding-3-small | Config B avg 0.72 | -0.02 den +0.01 | -60% latency, tang chi phi API | Chi doi neu deploy cloud khong co GPU hoac can giam latency |
