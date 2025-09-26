# Hướng Dẫn Chi Tiết Sử Dụng Ollama (Local LLM)

## Tổng Quan Ollama

Ollama là một công cụ cho phép bạn chạy các mô hình ngôn ngữ lớn (LLM) trên máy tính cá nhân. Điều này mang lại nhiều lợi ích:

- **Miễn phí**: Không tốn phí API như OpenAI
- **Bảo mật**: Dữ liệu không rời khỏi máy tính của bạn
- **Offline**: Hoạt động mà không cần internet
- **Tùy chỉnh**: Có thể fine-tune model theo nhu cầu

## Cài Đặt Ollama

### Windows

1. **Tải Ollama:**

   - Truy cập: https://ollama.ai/download
   - Tải file installer cho Windows
   - Chạy file `.exe` và làm theo hướng dẫn

2. **Kiểm tra cài đặt:**
   ```powershell
   ollama --version
   ```

### macOS

```bash
# Cách 1: Homebrew
brew install ollama

# Cách 2: Curl
curl -fsSL https://ollama.ai/install.sh | sh
```

### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Cài Đặt và Quản Lý Models

### 1. Tải Models Phổ Biến

```bash
# Llama 2 (7B) - Khuyến nghị cho máy có 8GB+ RAM
ollama pull llama2

# Llama 2 13B - Cho máy có 16GB+ RAM
ollama pull llama2:13b

# Code Llama - Chuyên về code
ollama pull codellama

# Mistral - Nhẹ và nhanh
ollama pull mistral

# Gemma - Google's model
ollama pull gemma:7b

# Phi-3 - Microsoft's model (nhẹ)
ollama pull phi3:mini
```

### 2. Liệt Kê Models Đã Cài

```bash
ollama list
```

### 3. Xóa Model

```bash
ollama rm llama2
```

## Khởi Động Ollama Server

### Tự Động (Windows)

Ollama tự động chạy dưới dạng service sau khi cài đặt.

### Thủ Công

```bash
# Khởi động server
ollama serve

# Server sẽ chạy ở http://localhost:11434
```

### Kiểm Tra Server

```bash
# Test kết nối
curl http://localhost:11434/api/tags

# Hoặc truy cập browser: http://localhost:11434
```

## Sử Dụng Ollama với Hệ Thống

### 1. Test Trực Tiếp

```bash
# Chat trực tiếp với model
ollama run llama2

# Thoát chat: /bye
```

### 2. API Call

```bash
# POST request
curl http://localhost:11434/api/generate \
  -d '{
    "model": "llama2",
    "prompt": "Giải thích tại sao học Stack và Queue quan trọng",
    "stream": false
  }'
```

### 3. Tích Hợp với Python

Trong file `llm_explainer.py`, class `OllamaExplainer` đã được cài đặt sẵn:

```python
from llm_explainer import OllamaExplainer

# Khởi tạo
explainer = OllamaExplainer(model_name="llama2")

# Sử dụng
explanation = explainer.explain_recommendations(
    student_code="B21DCCN001",
    recommendations=sample_data
)
```

## Cấu Hình Tối Ưu

### 1. Điều Chỉnh Tham Số Model

```python
class OllamaExplainer:
    def explain_recommendations(self, student_code, recommendations):
        response = self.requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,      # Độ sáng tạo (0.0-2.0)
                    "top_p": 0.9,           # Nucleus sampling
                    "top_k": 40,            # Top-k sampling
                    "num_predict": 200,     # Số token tối đa
                    "repeat_penalty": 1.1,   # Tránh lặp lại
                    "seed": 42              # Reproducible results
                }
            }
        )
```

### 2. Tùy Chỉnh Context Length

```bash
# Tăng context length khi pull model
ollama pull llama2 --context-length 4096
```

### 3. Sử Dụng GPU (Nếu có)

Ollama tự động detect và sử dụng GPU nếu có. Kiểm tra:

```bash
# Xem GPU usage
nvidia-smi

# Hoặc trong Windows Task Manager -> Performance -> GPU
```

## Models Khuyến Nghị Cho Giải Thích Giáo Dục

### 1. **Llama 2 7B** (Khuyến nghị)

```bash
ollama pull llama2
```

- **RAM cần:** 8GB+
- **Ưu điểm:** Cân bằng tốt giữa chất lượng và tốc độ
- **Phù hợp:** Máy tính cá nhân thông thường

### 2. **Mistral 7B** (Nhanh)

```bash
ollama pull mistral
```

- **RAM cần:** 6GB+
- **Ưu điểm:** Nhanh, tiết kiệm tài nguyên
- **Phù hợp:** Máy có cấu hình thấp

### 3. **Phi-3 Mini** (Nhẹ nhất)

```bash
ollama pull phi3:mini
```

- **RAM cần:** 4GB+
- **Ưu điểm:** Rất nhẹ, chạy mượt
- **Phù hợp:** Laptop, máy yếu

### 4. **Code Llama** (Chuyên về code)

```bash
ollama pull codellama
```

- **RAM cần:** 8GB+
- **Ưu điểm:** Hiểu code tốt
- **Phù hợp:** Giải thích bài tập lập trình

## Troubleshooting

### 1. Lỗi Kết Nối

**Triệu chứng:** `Connection refused`

**Giải pháp:**

```bash
# Kiểm tra service
ollama serve

# Hoặc restart
pkill ollama
ollama serve
```

### 2. Model Không Tải Được

**Triệu chứng:** `Error pulling model`

**Giải pháp:**

```bash
# Xóa model lỗi
ollama rm model_name

# Tải lại
ollama pull model_name

# Kiểm tra dung lượng ổ cứng
df -h  # Linux/Mac
dir    # Windows
```

### 3. Chậm/Lag

**Nguyên nhân:** Thiếu RAM hoặc CPU yếu

**Giải pháp:**

- Chuyển sang model nhẹ hơn (phi3:mini)
- Đóng các ứng dụng khác
- Giảm `num_predict`

### 4. Kết Quả Kém Chất Lượng

**Giải pháp:**

```python
# Cải thiện prompt
prompt = f"""
Bạn là giáo viên lập trình chuyên nghiệp.
Phân tích và giải thích rõ ràng, dễ hiểu:

{context}

Trả lời bằng tiếng Việt trong 2-3 câu ngắn gọn.
Tập trung vào lợi ích học tập cụ thể.
"""

# Điều chỉnh temperature
"temperature": 0.3  # Giảm để ổn định hơn
```

## Tích Hợp vào Streamlit App

### 1. Cập Nhật UI

Trong `app.py`, phần Ollama configuration:

```python
elif llm_type == "Ollama (Local)":
    col1, col2 = st.columns(2)
    with col1:
        # Dropdown với models phổ biến
        model_options = ["llama2", "mistral", "phi3:mini", "codellama", "gemma:7b"]
        model_name = st.selectbox("Chọn model:", model_options, index=0)
    with col2:
        base_url = st.text_input("Ollama URL:", "http://localhost:11434")

    # Test connection button
    if st.button("🔍 Test kết nối"):
        try:
            import requests
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = [m["name"] for m in response.json()["models"]]
                st.success(f"✅ Kết nối thành công! Models: {', '.join(available_models)}")
            else:
                st.error("❌ Server không phản hồi")
        except Exception as e:
            st.error(f"❌ Lỗi kết nối: {str(e)}")

    if st.button("Tạo giải thích Ollama"):
        # Implementation...
```

### 2. Hiển Thị Thông Tin Model

```python
# Thêm sidebar info
with st.sidebar.expander("🤖 Thông tin Ollama"):
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()["models"]
            for model in models:
                st.write(f"• {model['name']} ({model['size']})")
        else:
            st.write("Không thể kết nối server")
    except:
        st.write("Ollama chưa sẵn sàng")
```

## Benchmark Performance

### So Sánh Models (Ước tính)

| Model      | RAM  | Tốc độ     | Chất lượng | Phù hợp     |
| ---------- | ---- | ---------- | ---------- | ----------- |
| phi3:mini  | 4GB  | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | Máy yếu     |
| mistral    | 6GB  | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | Cân bằng    |
| llama2     | 8GB  | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | Khuyến nghị |
| llama2:13b | 16GB | ⭐⭐       | ⭐⭐⭐⭐⭐ | Máy mạnh    |

### Test Script

```python
import time
import requests

def benchmark_ollama(model_name, prompt):
    start_time = time.time()

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )

        end_time = time.time()

        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "time": end_time - start_time,
                "tokens": len(result["response"].split()),
                "response": result["response"]
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Sử dụng
result = benchmark_ollama("llama2", "Giải thích tại sao học Stack quan trọng")
print(f"Thời gian: {result['time']:.2f}s")
```

## Kết Luận

Ollama là giải pháp tuyệt vời cho việc:

- **Phát triển/Test**: Không tốn phí API
- **Bảo mật**: Dữ liệu không rời khỏi máy
- **Tùy chỉnh**: Có thể fine-tune theo domain cụ thể
- **Offline**: Hoạt động khi không có internet

**Khuyến nghị:**

1. Bắt đầu với `mistral` hoặc `llama2`
2. Test trên dataset nhỏ trước
3. Monitor RAM usage
4. Chuẩn bị fallback sang rule-based nếu cần
