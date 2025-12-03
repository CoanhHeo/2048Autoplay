# 🤖 Hướng dẫn setup Gemini AI để nhận diện số

## Bước 1: Lấy API Key

1. Truy cập: https://makersuite.google.com/app/apikey
2. Đăng nhập bằng Google Account
3. Click "Create API Key"
4. Copy API key

## Bước 2: Cài đặt thư viện

```bash
pip install google-generativeai
```

Hoặc:

```bash
pip install -r requirements.txt
```

## Bước 3: Cấu hình API Key

### Cách 1: Sử dụng file .env (Khuyến nghị)

1. Tạo file `.env` trong thư mục project:

```bash
cp .env.example .env
```

2. Mở file `.env` và thêm API key:

```
GEMINI_API_KEY=your_actual_api_key_here
```

### Cách 2: Set biến môi trường

**macOS/Linux:**
```bash
export GEMINI_API_KEY=your_actual_api_key_here
```

**Windows:**
```cmd
set GEMINI_API_KEY=your_actual_api_key_here
```

## Bước 4: Load biến môi trường

Tool đã tích hợp `python-dotenv` để tự động load từ file `.env`.

Đảm bảo file `config.py` có:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Bước 5: Chạy tool

```bash
python main.py
```

Tool sẽ tự động:
- ✅ Kiểm tra Gemini API key
- ✅ Ưu tiên sử dụng Gemini AI nếu có
- ✅ Fallback sang OCR/Template matching nếu Gemini không khả dụng

## Ưu điểm Gemini

- ✅ **Độ chính xác cao**: Nhận diện tốt với font chữ/icon đặc biệt
- ✅ **Không cần training**: Không cần Calibration
- ✅ **Hiểu context**: Nhận diện cả lưới 4x4 một lúc
- ✅ **Xử lý được màu sắc phức tạp**

## Lưu ý

- API key miễn phí có giới hạn requests
- Gemini cần internet để hoạt động
- Nếu Gemini lỗi, tool sẽ tự động dùng phương pháp dự phòng

## Kiểm tra

Chạy test:

```bash
python gemini_recognizer.py
```

Kết quả:
```
✅ Gemini sẵn sàng sử dụng
```

Hoặc:
```
❌ Gemini chưa sẵn sàng
Cần setup GEMINI_API_KEY
```
