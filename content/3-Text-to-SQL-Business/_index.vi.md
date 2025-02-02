---
title: "Text-to-SQL cho Doanh nghiệp"
date: 2024-02-01
draft: false
weight: 3
---


## Vấn đề
Doanh nghiệp cần chuyển đổi câu hỏi bằng ngôn ngữ tự nhiên thành truy vấn SQL có thể chạy trực tiếp trên cơ sở dữ liệu của họ, cho phép người dùng không chuyên về kỹ thuật truy cập và phân tích dữ liệu hiệu quả mà không cần biết SQL.

## Kiến trúc Giải pháp

### 1. Phân tích Schema Cơ sở dữ liệu
```python
def connect_to_database(self, db_path):
    self.conn = sqlite3.connect(db_path)
    cursor = self.conn.cursor()
    
    # Trích xuất thông tin schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = [col[1] for col in columns]
```
- Trích xuất schema tự động
- Ánh xạ bảng và cột
- Phát hiện quan hệ

### 2. Chuyển đổi Ngôn ngữ Tự nhiên sang SQL
```python
def generate_sql(self, query):
    prompt = f"""
    Với schema cơ sở dữ liệu sau:
    {self.schema}
    
    Chuyển đổi câu hỏi này thành SQL:
    "{query}"
    """
    
    response = self.client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Bạn là một chuyên gia SQL."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
```
- Chuyển đổi bằng GPT-4
- Tạo truy vấn dựa trên schema
- Thực thi quy tắc tối ưu hóa

### 3. Thực thi Truy vấn và Kết quả
```python
def execute_sql(self, sql):
    formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
    df = pd.read_sql_query(sql, self.conn)
    return formatted_sql, df
```
- Định dạng và xác thực SQL
- Thực thi truy vấn an toàn
- Kết quả dạng DataFrame

## Tính năng

### Tích hợp Cơ sở dữ liệu
- Hỗ trợ SQLite
- Phát hiện schema tự động
- Ánh xạ quan hệ

### Xử lý Truy vấn
- Hiểu ngôn ngữ tự nhiên
- Tối ưu hóa SQL
- Xử lý lỗi

### Trình bày Kết quả
- Hiển thị SQL định dạng
- Bảng dữ liệu tương tác
- Khả năng xuất dữ liệu

## Ví dụ Triển khai

```python
# Khởi tạo processor
processor = TextToSQLProcessor()

# Kết nối cơ sở dữ liệu
if processor.connect_to_database("database.db"):
    # Nhận câu hỏi
    query = "Tổng doanh số bán hàng trong quý vừa qua là bao nhiêu?"
    
    # Tạo và thực thi SQL
    sql = processor.generate_sql(query)
    formatted_sql, results = processor.execute_sql(sql)
    
    # Hiển thị kết quả
    print(formatted_sql)
    print(results)
```

## Best Practices

1. **Tạo Truy vấn**
   - Xác thực tham chiếu schema
   - Tối ưu hóa phép JOIN
   - Triển khai kiểm tra bảo mật

2. **Xử lý Lỗi**
   - Xác thực đầu vào người dùng
   - Xử lý lỗi SQL một cách khéo léo
   - Cung cấp thông báo lỗi rõ ràng

3. **Hiệu suất**
   - Cache truy vấn thường xuyên
   - Tối ưu hóa tập kết quả lớn
   - Giám sát thời gian thực thi

