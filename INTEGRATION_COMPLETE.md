# Hướng Dẫn Sử Dụng Tính Năng LLM Đã Tích Hợp

## ✅ Đã Hoàn Thành

- ✅ Cài đặt Ollama
- ✅ Tải model `mistral`
- ✅ Cài đặt thư viện `openai`, `requests`, `pandas`
- ✅ Tích hợp code LLM vào `app.py`
- ✅ Tạo 3 loại explainer: Rule-based, Ollama, OpenAI

## 🚀 Cách Sử Dụng Trong Web

### Bước 1: Khởi động Ollama (quan trọng!)

```powershell
# Mở terminal mới và chạy:
$env:PATH += ";C:\Users\Admin\AppData\Local\Programs\Ollama"
ollama serve
```

**Lưu ý:** Giữ terminal này mở để Ollama server chạy

### Bước 2: Khởi động Web App

```powershell
# Terminal khác:
venv\Scripts\activate
streamlit run app.py
```

### Bước 3: Sử Dụng Tính Năng

1. **Tạo gợi ý bài tập** như bình thường:

   - Chọn model
   - Chọn sinh viên
   - Nhấn "Tạo gợi ý bài tập"

2. **Sử dụng giải thích LLM:**
   - Sau khi có kết quả gợi ý, tìm phần "🤖 Giải Thích Thông Minh"
   - Chọn loại giải thích:

## 📋 3 Loại Giải Thích

### 1. **Rule-based (Miễn phí)** ⭐ Khuyến nghị bắt đầu

- ✅ Luôn hoạt động
- ✅ Nhanh (< 1 giây)
- ✅ Không cần internet
- 📝 Nhấn "🔍 Tạo giải thích Rule-based"

### 2. **Ollama (Local LLM)** ⭐⭐ Tốt nhất cho privacy

- ✅ Miễn phí, chạy local
- ✅ Chất lượng cao
- ⚠️ Cần Ollama server chạy
- 📝 Chọn model "mistral" → "🤖 Tạo giải thích Ollama"

### 3. **OpenAI GPT** ⭐⭐⭐ Chất lượng cao nhất

- ✅ Chất lượng tốt nhất
- ❌ Cần API key có phí
- 📝 Nhập API key → "🤖 Tạo giải thích GPT"

## 🔧 Troubleshooting

### Lỗi "Lỗi kết nối Ollama"

```powershell
# Kiểm tra server:
ollama list

# Nếu lỗi, restart:
ollama serve
```

### Lỗi "Import không tìm thấy"

```powershell
# Cài lại thư viện:
venv\Scripts\activate
pip install openai requests pandas
```

### Test Ollama riêng lẻ

```powershell
# Test trực tiếp:
$env:PATH += ";C:\Users\Admin\AppData\Local\Programs\Ollama"
ollama run mistral
# Nhập: "Giải thích tại sao học Stack quan trọng"
# Thoát: /bye
```

## 💡 Demo Nhanh

Nếu muốn test mà không chạy full web:

```powershell
venv\Scripts\activate
python test_llm_integration.py
```

## 🎯 Kết Quả Mong Đợi

### Rule-based Output:

```
Dựa trên phân tích, hệ thống gợi ý tập trung vào chủ đề 'Cấu trúc dữ liệu'
với độ khó tăng dần để phát triển kỹ năng từng bước. Các bài tập được sắp xếp
theo mức độ phù hợp giảm dần từ 0.950 đến 0.820.
```

### Ollama Output:

```
Các bài tập này được gợi ý vì chúng tạo nên một lộ trình học tập từ cơ bản
đến nâng cao trong lĩnh vực cấu trúc dữ liệu. Bắt đầu với Stack và Queue
giúp sinh viên nắm vững khái niệm cơ bản, sau đó tiến tới Binary Search Tree
để hiểu về cây, và cuối cùng là Heap để thành thạo các cấu trúc phức tạp hơn.
```

## 📊 So Sánh Performance

| Loại       | Tốc độ     | Chất lượng | Chi phí            | Offline |
| ---------- | ---------- | ---------- | ------------------ | ------- |
| Rule-based | ⭐⭐⭐⭐⭐ | ⭐⭐⭐     | ✅ Free            | ✅      |
| Ollama     | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | ✅ Free            | ✅      |
| OpenAI     | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ | ❌ ~$0.003/request | ❌      |

## 🔮 Tính Năng Sắp Tới

- [ ] Giải thích cho từng bài tập cụ thể
- [ ] Cache kết quả để tăng tốc
- [ ] Hỗ trợ nhiều ngôn ngữ
- [ ] Fine-tune model cho domain giáo dục

## 📞 Hỗ Trợ

Nếu gặp lỗi, hãy:

1. Kiểm tra Ollama server: `ollama list`
2. Kiểm tra virtual environment: `venv\Scripts\activate`
3. Chạy test: `python test_llm_integration.py`
