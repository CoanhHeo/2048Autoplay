"""
Module nhận diện trạng thái game
Chức năng: Phân tích ảnh để xác định giá trị của từng ô trong lưới 4x4
"""

import cv2
import numpy as np
from dotenv import load_dotenv
from config import GRID_SIZE, OCR_CONFIDENCE_THRESHOLD, DEBUG_MODE, AI_MODEL
from gemini_recognizer import GeminiRecognizer
from template_recognizer import TemplateRecognizer

# Load environment variables (cho Gemini API key)
load_dotenv()


class GameState:
    """
    Class quản lý và nhận diện trạng thái game
    Hỗ trợ 2 AI model: Gemini (online) và Template Matching (local)
    """
    
    def __init__(self, grid_size=GRID_SIZE, ai_model=AI_MODEL):
        """
        Khởi tạo GameState
        
        Args:
            grid_size (int): Kích thước lưới (mặc định 4x4)
            ai_model (str): AI model để nhận diện ('gemini' hoặc 'template')
        """
        self.grid_size = grid_size
        self.board = [[0] * grid_size for _ in range(grid_size)]
        self.ai_model = ai_model.lower()
        
        # Khởi tạo các recognizer
        self.gemini_recognizer = None
        self.template_recognizer = None
        
        # Khởi tạo AI model được chọn
        if self.ai_model == 'gemini':
            self.gemini_recognizer = GeminiRecognizer()
            if self.gemini_recognizer.is_available():
                if DEBUG_MODE:
                    print("🤖 Đang sử dụng: Gemini AI (online, chính xác cao)")
            else:
                print("⚠️  Gemini không khả dụng, chuyển sang Template Matching")
                self.ai_model = 'template'
                self.template_recognizer = TemplateRecognizer()
        
        elif self.ai_model == 'template':
            self.template_recognizer = TemplateRecognizer()
            if self.template_recognizer.enabled:
                if DEBUG_MODE:
                    print("🤖 Đang sử dụng: Template Matching (local, nhanh)")
            else:
                print("⚠️  Template Matching không khả dụng!")
                self.ai_model = None
        
        else:
            # Mặc định dùng Template Matching
            if DEBUG_MODE:
                print("🤖 Mặc định sử dụng: Template Matching")
            self.ai_model = 'template'
            self.template_recognizer = TemplateRecognizer()
        
    def recognize_number_from_cell(self, cell_img):
        """
        Nhận diện số từ một ô ảnh sử dụng OCR
        
        Args:
            cell_img (numpy.ndarray): Ảnh của một ô
            
        Returns:
            int: Số được nhận diện (0 nếu ô trống hoặc không nhận diện được)
        """
        try:
            # Kiểm tra xem ô có trống không (hầu hết pixel đều tối)
            mean_brightness = np.mean(cell_img)
            if mean_brightness < 50:  # Ngưỡng để xác định ô trống
                return 0
            
            # Cấu hình OCR để chỉ nhận diện số
            custom_config = r'--oem 3 --psm 10 -c tessedit_char_whitelist=0123456789'
            
            # Nhận diện text từ ảnh
            text = pytesseract.image_to_string(cell_img, config=custom_config)
            
            # Làm sạch và chuyển đổi text thành số
            text = text.strip()
            if text.isdigit():
                number = int(text)
                return number
            else:
                return 0
                
        except Exception as e:
            if DEBUG_MODE:
                print(f"⚠️  Lỗi khi nhận diện số: {e}")
            return 0
    
    def recognize_number_by_color(self, cell_img):
        """
        Nhận diện số dựa trên màu sắc của ô (phương pháp dự phòng)
        Trong game, mỗi số thường có một màu đặc trưng
        
        Args:
            cell_img (numpy.ndarray): Ảnh của một ô
            
        Returns:
            int: Số được đoán dựa trên màu
        """
        # Tính màu trung bình của ô
        if len(cell_img.shape) == 3:
            avg_color = np.mean(cell_img, axis=(0, 1))
        else:
            avg_color = np.mean(cell_img)
        
        # TODO: Cần thu thập dữ liệu màu cho từng số từ game thực tế
        # Đây là placeholder logic
        
        return 0  # Trả về 0 nếu không xác định được
    
    def update_from_grid(self, grid_images, full_image=None):
        """
        Cập nhật trạng thái board từ lưới ảnh
        Hỗ trợ 2 AI model: Gemini (online) và PaddleOCR (local)
        
        Args:
            grid_images (list): Danh sách 2D các ảnh ô [row][col]
            full_image (numpy.ndarray): Ảnh đầy đủ của lưới game (cho Gemini)
            
        Returns:
            list: Board 2D với các giá trị số
        """
        board = None
        
        # Thử dùng AI model được chọn
        if self.ai_model == 'gemini' and self.gemini_recognizer and full_image is not None:
            board = self.gemini_recognizer.recognize_board(full_image)
            if board is not None:
                self.board = board
                if DEBUG_MODE:
                    print("🤖 Đã nhận diện bằng Gemini AI")
                return self.board
            else:
                if DEBUG_MODE:
                    print("⚠️  Gemini thất bại, fallback sang PaddleOCR")
                self.ai_model = 'paddle'
                if not self.paddle_recognizer:
                    self.paddle_recognizer = PaddleRecognizer()
        
        # Dùng Template Matching
        if self.ai_model == 'template' and self.template_recognizer:
            # Chuyển grid_images 2D thành list 1D (16 ô)
            grid_cells = []
            for row in range(self.grid_size):
                for col in range(self.grid_size):
                    grid_cells.append(grid_images[row][col])
            
            board = self.template_recognizer.recognize_board(grid_cells)
            if board is not None:
                self.board = board
                if DEBUG_MODE:
                    print("🤖 Đã nhận diện bằng Template Matching")
                    print("🎮 Trạng thái game hiện tại:")
                    self.print_board()
                return self.board
            else:
                if DEBUG_MODE:
                    print("❌ Template Matching thất bại")
        
        # Nếu không có AI nào hoạt động, trả về board trống
        if DEBUG_MODE:
            print("❌ Không có AI model nào khả dụng!")
            print("🎮 Trạng thái game hiện tại:")
            self.print_board()
        
        return self.board
    
    def print_board(self):
        """
        In ra board dưới dạng text để dễ nhìn
        """
        print("┌" + "─────┬" * (self.grid_size - 1) + "─────┐")
        for i, row in enumerate(self.board):
            print("│", end="")
            for cell in row:
                if cell == 0:
                    print("     │", end="")
                else:
                    print(f" {cell:3d} │", end="")
            print()
            if i < self.grid_size - 1:
                print("├" + "─────┼" * (self.grid_size - 1) + "─────┤")
        print("└" + "─────┴" * (self.grid_size - 1) + "─────┘")
    
    def get_board(self):
        """
        Lấy trạng thái board hiện tại
        
        Returns:
            list: Board 2D
        """
        return self.board
    
    def is_empty_cell(self, row, col):
        """
        Kiểm tra ô có trống không
        
        Args:
            row (int): Hàng
            col (int): Cột
            
        Returns:
            bool: True nếu ô trống
        """
        return self.board[row][col] == 0
    
    def get_score(self):
        """
        Tính điểm dựa trên tổng các số trên board
        
        Returns:
            int: Tổng điểm
        """
        total = 0
        for row in self.board:
            total += sum(row)
        return total
    
    def get_max_tile(self):
        """
        Lấy giá trị lớn nhất trên board
        
        Returns:
            int: Giá trị lớn nhất
        """
        max_val = 0
        for row in self.board:
            max_val = max(max_val, max(row))
        return max_val
    
    def count_empty_cells(self):
        """
        Đếm số ô trống
        
        Returns:
            int: Số lượng ô trống
        """
        count = 0
        for row in self.board:
            count += row.count(0)
        return count
    
    def is_game_over(self):
        """
        Kiểm tra xem game đã kết thúc chưa
        (Không còn ô trống và không còn nước đi hợp lệ)
        
        Returns:
            bool: True nếu game over
        """
        # Nếu còn ô trống thì game chưa over
        if self.count_empty_cells() > 0:
            return False
        
        # Kiểm tra xem còn có thể ghép được không
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                current = self.board[row][col]
                
                # Kiểm tra ô bên phải
                if col < self.grid_size - 1:
                    if abs(self.board[row][col + 1] - current) == 1:
                        return False
                
                # Kiểm tra ô bên dưới
                if row < self.grid_size - 1:
                    if abs(self.board[row + 1][col] - current) == 1:
                        return False
        
        return True


# Hàm tiện ích để test module
if __name__ == "__main__":
    print("🧪 Testing GameState module...")
    
    # Tạo một board mẫu để test
    game = GameState()
    
    # Giả lập một board
    game.board = [
        [2, 4, 8, 16],
        [0, 2, 4, 8],
        [2, 0, 2, 4],
        [4, 2, 0, 2]
    ]
    
    print("Board mẫu:")
    game.print_board()
    
    print(f"\n📊 Điểm số: {game.get_score()}")
    print(f"🏆 Ô lớn nhất: {game.get_max_tile()}")
    print(f"📭 Số ô trống: {game.count_empty_cells()}")
    print(f"🎮 Game over: {game.is_game_over()}")
    
    print("\n✅ Test hoàn thành!")
