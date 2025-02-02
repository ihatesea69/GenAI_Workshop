---
title: "Giới hạn Token trong Large Language Models"
date: 2024-02-01
draft: false
weight: 1
---

## Vấn đề
Large Language Models (LLMs) gặp hạn chế đáng kể về giới hạn token, gây khó khăn trong việc xử lý các tài liệu lớn (ví dụ: báo cáo 20 trang) một cách hiệu quả. Hạn chế này ảnh hưởng đến khả năng hiểu và tạo phản hồi dựa trên ngữ cảnh lớn của mô hình.

![Token Limitations](/images/token_limit.jpg)

## Giải pháp

### 1. Chiến lược "Chia Để Trị"
```python
text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=512,
    chunk_overlap=50,
    length_function=len
)
```
- **Kích thước chunk**: 512 ký tự mỗi chunk
- **Độ chồng lấp**: 50 ký tự để duy trì tính liên tục ngữ cảnh
- **Dấu phân tách**: Ký tự xuống dòng cho các điểm ngắt tự nhiên

### 2. Triển khai Vector Storage
```python
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(chunks, embeddings)
```
- Sử dụng mô hình embedding của OpenAI
- FAISS cho tìm kiếm tương đồng hiệu quả
- Lưu trữ vector trong bộ nhớ để truy xuất nhanh

### 3. RAG (Retrieval Augmented Generation)
```python
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3})
)
```
- Truy xuất 3 chunk liên quan nhất
- Kết hợp các chunk để tạo phản hồi có ngữ cảnh
- Sử dụng LLM của OpenAI để tạo phản hồi

## Tính năng

### Xử lý Tài liệu
- Hỗ trợ nhiều định dạng file (TXT, PDF, DOCX)
- Chức năng xem trước tài liệu
- Theo dõi tiến trình xử lý

### Xử lý Truy vấn
- Nhập câu hỏi tương tác
- Hiển thị các chunk tài liệu liên quan
- Phản hồi AI dựa trên ngữ cảnh

### Giao diện Người dùng
- Giao diện Streamlit trực quan
- Chỉ báo tiến trình
- Phần kết quả có thể mở rộng

## Ví dụ Triển khai

```python
# Upload và xử lý tài liệu
uploaded_file = st.file_uploader("📄 Tải lên tài liệu", type=["txt", "pdf", "docx"])
if uploaded_file is not None:
    text = uploaded_file.read().decode("utf-8")
    
    # Xử lý chunk
    chunks = text_splitter.split_text(text)
    
    # Lưu trữ vector
    vectorstore = FAISS.from_texts(chunks, embeddings)
    
    # Xử lý truy vấn
    query = st.text_input("Đặt câu hỏi của bạn:")
    if query:
        docs = vectorstore.similarity_search(query, k=3)
        response = qa_chain.run(query)
```

## Best Practices

1. **Tiền xử lý**
   - Làm sạch và chuẩn hóa văn bản trước khi chia nhỏ
   - Loại bỏ nội dung không liên quan để tối ưu hóa token
   - Duy trì cấu trúc tài liệu khi có thể

2. **Chiến lược Chia nhỏ**
   - Điều chỉnh kích thước chunk dựa trên loại nội dung
   - Sử dụng độ chồng lấp phù hợp để bảo toàn ngữ cảnh
   - Xem xét ranh giới ngữ nghĩa khi có thể

3. **Tối ưu hóa Truy vấn**
   - Triển khai cache cho các truy vấn thường xuyên
   - Tối ưu số lượng chunk được truy xuất
   - Cân bằng chất lượng phản hồi với tốc độ xử lý

## Cân nhắc về Hiệu năng

1. **Sử dụng Bộ nhớ**
   - Giám sát kích thước vector store
   - Triển khai xử lý hàng loạt cho tài liệu lớn
   - Dọn dẹp bộ nhớ tạm

2. **Thời gian Phản hồi**
   - Cache các truy vấn phổ biến
   - Tối ưu hóa truy xuất chunk
   - Cân bằng kích thước chunk với độ chính xác

3. **Độ chính xác**
   - Xác thực phản hồi với tài liệu nguồn
   - Điều chỉnh kích thước chunk dựa trên độ phức tạp nội dung
   - Giám sát và ghi log chất lượng truy xuất

