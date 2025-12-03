# 🎮 Auto 2048 Game Tool

Tool tự động chơi mini game 2048 trong game "Lữ Khách Đại Lục: Idle RPG" sử dụng AI và Computer Vision.

## ✨ Tính năng

- 🤖 **AI tự động**: Sử dụng thuật toán Expectimax để tìm nước đi tối ưu
- 👁️ **Computer Vision**: Nhận diện trạng thái game từ màn hình
- ⌨️ **Tự động điều khiển**: Gửi phím mũi tên để điều khiển game
- 🎯 **Chế độ interactive**: Chạy từng bước để học hỏi
- 📊 **Thống kê**: Theo dõi điểm số và hiệu suất

## 📋 Yêu cầu hệ thống

- **macOS** (đã được thiết kế cho macOS)
- **Python 3.8+**
- **Tesseract OCR** (để nhận diện số)

## 🚀 Cài đặt

### Bước 1: Clone hoặc tải project

```bash
cd /path/to/autoMinigame248RealOfPixel
```

### Bước 2: Cài đặt Tesseract OCR

Trên macOS, sử dụng Homebrew:

```bash
brew install tesseract
```

Kiểm tra cài đặt:

```bash
tesseract --version
```

### Bước 3: Cài đặt Python dependencies

Tạo virtual environment (khuyến nghị):

```bash
python3 -m venv venv
source venv/bin/activate
```

Cài đặt các thư viện:

```bash
pip install -r requirements.txt
```

### Bước 4: Cấp quyền truy cập

Tool cần quyền:
- **Screen Recording**: Để chụp màn hình
- **Accessibility**: Để gửi phím

Khi chạy lần đầu, macOS sẽ yêu cầu cấp quyền. Vào:
- `System Preferences` → `Security & Privacy` → `Privacy`
- Chọn `Screen Recording` và thêm Terminal/Python
- Chọn `Accessibility` và thêm Terminal/Python

## 📖 Hướng dẫn sử dụng

### 1. Chạy tool

```bash
python main.py
```

### 2. Setup vùng game (lần đầu tiên)

- Chọn option `1` trong menu
- Mở game và hiển thị mini game 2048
- Di chuyển chuột đến **góc trên trái** của lưới game → Nhấn Enter
- Di chuyển chuột đến **góc dưới phải** của lưới game → Nhấn Enter
- Tool sẽ lưu ảnh `setup_test.png` để bạn kiểm tra

### 3. Chạy auto

Có 2 chế độ:

#### Chế độ tự động (Auto)
- Chọn option `2` trong menu
- Nhập số nước đi tối đa (hoặc Enter để không giới hạn)
- Tool sẽ tự động chơi game

#### Chế độ interactive (Từng bước)
- Chọn option `3` trong menu
- Nhấn Enter để AI thực hiện từng nước đi
- Quan sát và học hỏi cách AI chơi

### 4. Dừng tool

- **Dừng bình thường**: Nhấn `Ctrl+C`
- **Dừng khẩn cấp**: Di chuột lên góc trên trái màn hình

## ⚙️ Cấu hình

Chỉnh sửa file `config.py` để điều chỉnh:

```python
# Kích thước lưới
GRID_SIZE = 4  # 4x4

# Độ sâu AI (càng cao càng thông minh nhưng chậm hơn)
SEARCH_DEPTH = 4  # Khuyến nghị: 3-5

# Thời gian chờ giữa các nước đi
MOVE_DELAY = 0.3  # giây

# Debug mode - hiển thị thông tin chi tiết
DEBUG_MODE = True
```

## 📁 Cấu trúc project

```
autoMinigame248RealOfPixel/
├── main.py              # File chính, chạy tool
├── config.py            # Cấu hình
├── screen_capture.py    # Module chụp màn hình
├── game_state.py        # Module nhận diện trạng thái game
├── ai_solver.py         # Module AI (Expectimax algorithm)
├── game_controller.py   # Module điều khiển (gửi phím)
├── requirements.txt     # Dependencies
└── README.md           # File này
```

## 🧠 Cách hoạt động

### 1. Screen Capture (Chụp màn hình)
- Sử dụng `mss` để chụp vùng game nhanh chóng
- Xử lý ảnh bằng OpenCV (chuyển xám, threshold, blur)
- Chia ảnh thành lưới 4x4

### 2. Game State Recognition (Nhận diện trạng thái)
- Sử dụng Tesseract OCR để nhận diện số trong từng ô
- Phương pháp dự phòng: Nhận diện dựa trên màu sắc
- Xây dựng ma trận 4x4 đại diện cho board

### 3. AI Solver (Giải thuật)
- **Expectimax Algorithm**: Kết hợp giữa Minimax và xác suất
  - Max node: Người chơi chọn nước đi tốt nhất
  - Chance node: Tính giá trị kỳ vọng khi spawn ô mới
  
- **Heuristics đánh giá board**:
  - Số ô trống (càng nhiều càng tốt)
  - Tổng giá trị các ô
  - Giá trị ô lớn nhất
  - Smoothness (các ô liền kề có giá trị gần nhau)
  - Monotonicity (hàng/cột tăng/giảm dần)
  - Ô lớn nhất ở góc

### 4. Game Controller (Điều khiển)
- Sử dụng `pyautogui` để gửi phím mũi tên
- Delay giữa các nước đi để game xử lý
- Cơ chế FailSafe để dừng khẩn cấp

## 🔧 Troubleshooting

### Lỗi: "Tesseract not found"
```bash
# Cài đặt Tesseract
brew install tesseract

# Hoặc chỉ định đường dẫn trong code
pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
```

### Lỗi: "Permission denied" khi chụp màn hình
- Vào `System Preferences` → `Security & Privacy` → `Screen Recording`
- Thêm Terminal hoặc Python vào danh sách

### OCR không nhận diện được số
- Kiểm tra file `setup_test.png` để đảm bảo vùng chụp đúng
- Tăng độ tương phản của màn hình
- Điều chỉnh threshold trong `screen_capture.py`
- Có thể cần huấn luyện OCR cho font chữ đặc biệt

### AI chọn nước đi không tối ưu
- Tăng `SEARCH_DEPTH` trong `config.py` (nhưng sẽ chậm hơn)
- Điều chỉnh các heuristics trong `ai_solver.py`
- Thêm trọng số cho các yếu tố đánh giá

### Game không nhận phím
- Đảm bảo cửa sổ game đang được focus
- Kiểm tra quyền Accessibility
- Thử tăng `MOVE_DELAY`

## 🎯 Tips để đạt điểm cao

1. **Setup vùng chụp chính xác**: Đảm bảo chỉ chụp lưới 4x4, không bao gồm viền
2. **Tăng SEARCH_DEPTH**: Độ sâu 4-5 cho kết quả tốt
3. **Giữ ô lớn ở góc**: AI đã được tối ưu cho chiến thuật này
4. **Chạy ở chế độ fullscreen**: Giảm nhiễu từ các yếu tố khác

## 📝 Lưu ý

- Tool này chỉ dùng cho mục đích học tập và giải trí
- Không được sử dụng để gian lận trong thi đấu hoặc vi phạm điều khoản của game
- Hiệu suất phụ thuộc vào cấu hình máy và chất lượng OCR

## 🤝 Đóng góp

Nếu bạn muốn cải thiện tool:
1. Tối ưu thuật toán AI
2. Cải thiện độ chính xác OCR
3. Thêm tính năng mới
4. Báo lỗi và đề xuất

## 📄 License

MIT License - Free to use and modify

## 👨‍💻 Tác giả


---

**Chúc bạn đạt điểm cao! 🏆**
