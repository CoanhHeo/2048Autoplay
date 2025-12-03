"""
File cấu hình cho tool auto 2048
Chứa các thông số có thể điều chỉnh
"""

# Load biến môi trường từ file .env
from dotenv import load_dotenv
load_dotenv()

# Cấu hình vùng chụp màn hình
# Bạn sẽ cần điều chỉnh các giá trị này dựa trên màn hình của bạn
SCREEN_REGION = {
    'top': 100,      # Tọa độ Y trên cùng của vùng game
    'left': 100,     # Tọa độ X bên trái của vùng game
    'width': 800,    # Chiều rộng vùng game
    'height': 800    # Chiều cao vùng game
}

# Kích thước lưới game
GRID_SIZE = 4  # Lưới 4x4

# Độ sâu tìm kiếm cho thuật toán AI
# Tăng lên 5 để AI dự đoán xa hơn và tránh bị kẹt
SEARCH_DEPTH = 5  # Tìm kiếm sâu 5 bước (có thể giảm xuống 3-4 nếu chậm)

# Thời gian chờ giữa các nước đi (giây)
# Template Matching: 0.2s (rất nhanh, offline)
# Gemini: 1.0s (tránh rate limit 15 req/min)
MOVE_DELAY = 0.2

# Ngưỡng độ tin cậy khi nhận diện số
OCR_CONFIDENCE_THRESHOLD = 0.5

# Debug mode - hiển thị ảnh và thông tin chi tiết
DEBUG_MODE = True

# AI Model cho nhận diện số
# Có 2 options:
# 'gemini' - Chính xác cao (95-98%), chậm ~2s/move, cần internet, quota limited
# 'template' - Template Matching, nhanh, offline, phù hợp cho icon/hình ảnh (KHUYẾN NGHỊ!)
AI_MODEL = 'template'  # Mặc định dùng Template Matching (tốt nhất cho icon game)
