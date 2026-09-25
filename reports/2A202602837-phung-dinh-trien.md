# Individual contribution report

Mỗi thành viên copy template này thành:

```text
reports/<student-id>-<short-name>.md
```

Giới hạn khuyến nghị: 1 trang, không chép lại README hoặc mô tả lý thuyết chung. Báo cáo không phải một bài pipeline cá nhân; mục đích là ghi nhận ownership và bằng chứng đóng góp trong sản phẩm nhóm.

---

## Thông tin

- Họ và tên: Phùng Đình Triển
- Mã học viên: 2A202602837
- Nhóm: IpadKid
- Repository/branch: https://github.com/tuantung26/K4-L3B-RAG-Pipeline.git

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 1 – Chuẩn bị repository và corpus | Chuẩn bị cấu trúc dữ liệu cho pipeline, lựa chọn và thu thập các văn bản pháp luật về giao thông từ nguồn chính thức. Khi cơ chế tải tự động gặp lỗi DNS, tôi chuyển sang tải các văn bản PDF thủ công và đặt vào `data/landing/legal/`. | `data/landing/legal/` và các file cấu hình/script liên quan | Done |
| Task 2 – Thu thập tin tức | Sử dụng Crawl4AI để crawl 5 bài viết liên quan đến pháp luật và an toàn giao thông. Lưu kết quả crawl dưới dạng JSON, gồm URL, tiêu đề, thời gian crawl và nội dung Markdown. | `src/task2_crawl_news.py`, `data/landing/news/article_01.json` – `article_05.json` | Done |
| Task 3 – Chuẩn hóa corpus | Chuyển các văn bản PDF/DOC/DOCX và dữ liệu JSON đã thu thập sang Markdown thống nhất để sử dụng cho các bước chunking, embedding và retrieval. | `src/task3_convert_markdown.py`, `data/standardized/legal/`, `data/standardized/news/` | Done |
Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng nguồn văn bản pháp luật chính thức và lựa chọn chủ đề pháp luật về giao thông làm corpus.
   
   **Lý do/evidence:** Corpus gồm các văn bản pháp luật về giao thông được thu thập từ nguồn văn bản chính thức, kết hợp với các bài viết tin tức liên quan để tạo dữ liệu có cả nguồn pháp lý và nguồn tin tức.

   **Trade-off:** Nguồn chính thức có độ tin cậy cao nhưng việc thu thập tự động gặp vấn đề kết nối/DNS, vì vậy một số văn bản phải được tải thủ công.

2. **Quyết định:** Sử dụng Crawl4AI để thu thập 5 bài viết và chuẩn hóa toàn bộ dữ liệu về Markdown.
   
   **Lý do/evidence:** Crawl4AI cho phép lấy nội dung bài viết từ các trang web và lưu thành JSON; sau đó `MarkItDown` được sử dụng để chuyển dữ liệu về định dạng Markdown thống nhất.

   **Trade-off:** Quy trình có thêm bước crawl và chuyển đổi dữ liệu, nhưng corpus có format thống nhất và thuận tiện cho các bước chunking, embedding và retrieval phía sau.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - Chạy script Task 2 để kiểm tra việc crawl và lưu 5 bài viết.
  - Chạy script Task 3 để kiểm tra việc chuyển đổi dữ liệu sang Markdown.
- Kết quả trước/sau:
  - Sau Task 2: thu được 5 file JSON trong `data/landing/news/`.
  - Sau Task 3: dữ liệu được chuẩn hóa thành các file Markdown trong `data/standardized/legal/` và `data/standardized/news/`.
- Lỗi đã phát hiện và cách xử lý:
  - Cơ chế tải văn bản pháp luật tự động gặp lỗi DNS đối với `datafiles.chinhphu.vn`. Tôi chuyển sang tải các file PDF thủ công và tiếp tục pipeline từ thư mục `data/landing/legal/`.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Việc thu thập một số văn bản pháp luật chưa thể thực hiện hoàn toàn tự động do vấn đề kết nối/DNS với nguồn dữ liệu.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Hoàn thiện cơ chế download có khả năng retry/fallback để việc thu thập dữ liệu có thể chạy lại tự động mà không cần tải thủ công.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Phùng Đình Triển
