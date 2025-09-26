# Hướng Dẫn Tích Hợp LLM cho Giải Thích Kết Quả

## Tổng Quan

Hệ thống hỗ trợ 3 phương pháp tích hợp LLM để giải thích kết quả gợi ý bài tập:

1. **OpenAI GPT** - Chất lượng cao, cần API key có phí
2. **Ollama** - Chạy local, miễn phí, cần cài đặt
3. **Rule-based** - Fallback, không cần LLM

## Cài Đặt

### 1. OpenAI GPT

```bash
pip install openai>=1.0.0
```

**Sử dụng:**

- Lấy API key từ https://platform.openai.com/api-keys
- Nhập vào ô "OpenAI API Key" trong giao diện
- Chọn "Tạo giải thích GPT"

**Chi phí:** ~$0.001-0.003 per request

### 2. Ollama (Local LLM)

> 📖 **Xem hướng dẫn chi tiết:** [OLLAMA_GUIDE.md](./OLLAMA_GUIDE.md)

**Cài đặt nhanh:**

```bash
# Windows: Tải từ https://ollama.ai/download
# macOS/Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Tải model khuyến nghị
ollama pull llama2        # Cân bằng (8GB RAM)
ollama pull mistral       # Nhanh (6GB RAM)
ollama pull phi3:mini     # Nhẹ (4GB RAM)

# Khởi động server
ollama serve
```

**Models khuyến nghị cho giải thích giáo dục:**

- **llama2**: Chất lượng tốt, cần 8GB+ RAM
- **mistral**: Nhanh, tiết kiệm tài nguyên
- **phi3:mini**: Nhẹ nhất, phù hợp máy yếu
- **codellama**: Chuyên về lập trình

**Ưu điểm:**

- ✅ Miễn phí hoàn toàn
- ✅ Chạy offline, bảo mật dữ liệu
- ✅ Tùy chỉnh cao
- ✅ Không giới hạn số lần sử dụng

### 3. Rule-based (Fallback)

Không cần cài đặt gì thêm. Sử dụng thuật toán phân tích pattern để tạo giải thích.

## Cách Sử dụng

### Bước 1: Tạo Gợi Ý Bài Tập

1. Chọn sinh viên
2. Chọn số lượng gợi ý
3. Nhấn "Tạo gợi ý bài tập"

### Bước 2: Bật Giải Thích AI

1. Tích vào checkbox "Bật giải thích thông minh"
2. Chọn loại AI phù hợp
3. Cung cấp thông tin cần thiết (API key, model name, etc.)
4. Nhấn nút tương ứng để tạo giải thích

### Bước 3: Xem Giải Thích Chi Tiết

- Nhấn nút "❓ Tại sao gợi ý bài X?" để xem giải thích cho từng bài tập cụ thể

## Ví Dụ Kết Quả

### Giải Thích Tổng Quan

```
Dựa trên phân tích, các bài tập được gợi ý tập trung vào chủ đề 'Cấu trúc dữ liệu'
với độ khó tăng dần từ Dễ đến Trung bình, giúp sinh viên xây dựng nền tảng vững chắc
trước khi tiếp cận các bài toán phức tạp hơn. Thứ tự gợi ý được sắp xếp theo mức độ
phù hợp, bắt đầu từ Stack và Queue để làm quen với khái niệm cơ bản.
```

### Giải Thích Chi Tiết

```
Bài tập "Stack và Queue" được gợi ý vì đây là nền tảng quan trọng của cấu trúc dữ liệu,
phù hợp để sinh viên củng cố kiến thức cơ bản trước khi tiến tới các chủ đề nâng cao hơn.
```

## Tùy Chỉnh Nâng Cao

### 1. Thay Đổi Prompt Template

Chỉnh sửa file `llm_explainer.py`, tìm phần prompt và thay đổi:

```python
prompt = f"""
Bạn là chuyên gia giáo dục lập trình. Phân tích danh sách gợi ý sau:

{context}

Hãy giải thích:
1. Lý do chọn những bài tập này
2. Trình tự học tập hiệu quả
3. Kỹ năng sẽ phát triển

Viết ngắn gọn, dễ hiểu bằng tiếng Việt.
"""
```

### 2. Thêm Context Từ Lịch Sử

Để tăng độ chính xác, có thể thêm thông tin lịch sử học tập:

```python
# Trong hàm get_top_k_recommendations, thêm:
user_history = get_user_interaction_history(user_id, dataset)  # Cần implement
explainer.explain_recommendations(student_code, rec_data, user_history)
```

### 3. Cache Kết Quả

Để tiết kiệm chi phí API:

```python
import hashlib
import json

def get_cache_key(student_code, recommendations):
    data = {"student": student_code, "recs": recommendations}
    return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()

# Sử dụng st.cache_data hoặc file cache
```

## Troubleshooting

### Lỗi Thường Gặp

1. **OpenAI API Error**

   - Kiểm tra API key hợp lệ
   - Đảm bảo có đủ credit
   - Kiểm tra kết nối internet

2. **Ollama Connection Error**

   - Kiểm tra Ollama server đang chạy: `ollama list`
   - Đảm bảo port 11434 không bị chặn
   - Thử restart Ollama service

3. **Import Error**
   - Cài đặt thư viện: `pip install requests openai pandas`
   - Hoặc: `pip install -r requirements.txt`
   - Kiểm tra virtual environment đang active
   - Với conda: `conda install requests openai pandas`

### Tối Ưu Hóa Performance

1. **Giảm Token Usage:**

   - Giới hạn số bài tập trong context (5-10 bài)
   - Rút gọn thông tin mô tả bài tập
   - Sử dụng GPT-3.5 thay vì GPT-4

2. **Tăng Tốc Response:**
   - Cache kết quả thường dùng
   - Sử dụng temperature thấp (0.3-0.7)
   - Giới hạn max_tokens

## Phát Triển Thêm

### Tính Năng Có Thể Bổ Sung

1. **Nhiều Ngôn Ngữ:** Hỗ trợ giải thích bằng tiếng Anh
2. **Personalization:** Dựa trên learning style của sinh viên
3. **Feedback Loop:** Cho phép sinh viên đánh giá chất lượng giải thích
4. **Analytics:** Theo dõi hiệu quả của các loại giải thích

### API Integration

Có thể tạo endpoint riêng cho tính năng giải thích:

```python
@app.route('/api/explain')
def explain_recommendations():
    # Implementation
    pass
```

## Kết Luận

Tích hợp LLM giúp nâng cao trải nghiệm người dùng bằng cách:

- Cung cấp lý do rõ ràng cho mỗi gợi ý
- Hướng dẫn thứ tự học tập hiệu quả
- Tăng độ tin cậy của hệ thống gợi ý
- Hỗ trợ quá trình ra quyết định của người học
