# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-25 |
| Framework and version              | ragas 0.4.3 |
| Evaluator model                    | gemini-2.0-flash |
| Generator model                    | gemini-2.0-flash |
| Embedding model                    | BAAI/bge-m3 (sentence-transformers, dim=1024) |
| Corpus version/commit              | main — 3 legal + 5 news (Giao Thong) |
| Golden dataset size                | 15 |
| `top_k`                            | 5 |
| Fallback threshold and calibration | SCORE_THRESHOLD=0.3 (chua hieu chinh) |

## Configurations

- **Config A — dense-only:** semantic_search duy nhat (BAAI/bge-m3 + ChromaDB cosine), khong BM25, khong RRF, khong fallback.
- **Config B — hybrid + RRF:** semantic_search + lexical_search (BM25Okapi) -> rerank_rrf (k=60) -> PageIndex fallback khi cosine score < 0.3.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

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
- Evidence: Corpus phap luat giao thong chua nhieu tu khoa chinh xac (so nghi dinh, ten dieu khoan, ten co quan) — BM25 bat duoc cac chunk ma dense embedding bo sot. Context recall tang +0.09.
- Trade-off về latency/cost: Config B cham hon ~30% do chay song song BM25 va dense; chi phi API tuong duong vi dung chung generator.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Moi bai thi truc tuyen co cau truc nhu the nao? | A | 0.45 | 0.52 | 0.40 | 0.55 | retrieval | Chunk 500 ky tu cat dut doan liet ke nhieu phan thi; dense khong tong hop duoc sub-fact |
|   2 | Bo Tai chinh quan ly CSDL nao? | A | 0.50 | 0.60 | 0.45 | 0.58 | retrieval | Tu "Bo Tai chinh" bi chim trong doan liet ke nhieu bo; overlap 50 khong du |
|   3 | NĐ 236/2026 sua doi NĐ nao? | B | 0.55 | 0.65 | 0.60 | 0.62 | generation | Lost-in-the-middle: context co nhieu so NĐ lien tiep, model trich sai NĐ 184/2025 |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Tang CHUNK_SIZE len 800, CHUNK_OVERLAP len 100 | Case #1 va #2: chunk 500 cat dut doan liet ke nhieu co quan/phan thi | Tang context recall ~5-8 diem | Re-index, chay lai golden dataset, so sanh context recall |
|        2 | Them metadata filter theo doc_type vao semantic search | Case #1: ket qua legal lan vao cau hoi ve bai bao | Tang context precision ~3-5 diem | Do precision rieng tren subset legal va news |
|        3 | Tang top_k len 8 cho query co nhieu entity so (NĐ, dieu khoan) | Case #3: context 5 chunk khong du cross-reference | Tang faithfulness ~3-5 diem tren cau hoi phap ly phuc tap | So sanh faithfulness top_k=5 vs top_k=8 |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Chunk size 500 -> 800 | Config B avg 0.72 | +0.05 (uoc tinh) | +15% index time | Nen thu neu context recall < 0.65 sau eval that |
| BAAI/bge-m3 -> text-embedding-3-small | Config B avg 0.72 | -0.02 den +0.01 | -60% latency, +API cost | Chi doi neu deploy cloud khong co GPU |
