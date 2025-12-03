"""
Module nhận diện số sử dụng PaddleOCR
PaddleOCR là OCR mạnh mẽ, hỗ trợ nhiều ngôn ngữ, nhanh và chính xác
"""

from paddleocr import PaddleOCR
import cv2
import numpy as np
from config import DEBUG_MODE


class PaddleRecognizer:
    """
    Class nhận diện số từ ô game bằng PaddleOCR
    """
    
    def __init__(self):
        """
        Khởi tạo PaddleOCR recognizer
        """
        try:
            # Khởi tạo PaddleOCR với config tối ưu
            # use_angle_cls=True: Tự động xoay ảnh nếu cần
            # lang='en': Ngôn ngữ tiếng Anh (cho số)
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en'
            )
            self.enabled = True
            if DEBUG_MODE:
                print("✅ PaddleOCR đã sẵn sàng")
                
        except Exception as e:
            print(f"❌ Lỗi khởi tạo PaddleOCR: {e}")
            self.enabled = False
    
    def recognize_number(self, cell_img):
        """
        Nhận diện số từ một ô
        
        Args:
            cell_img: Ảnh ô game (numpy array)
            
        Returns:
            int: Số nhận diện được (0 nếu ô trống hoặc lỗi)
        """
        if not self.enabled:
            return 0
        
        if cell_img is None or cell_img.size == 0:
            return 0
        
        try:
            # Kiểm tra ô trống
            if self._is_empty_cell(cell_img):
                return 0
            
            # Tiền xử lý ảnh
            processed = self._preprocess_cell(cell_img)
            
            # Nhận diện với PaddleOCR
            result = self.ocr.ocr(processed)
            
            # Xử lý kết quả - PaddleOCR 3.x trả về OCRResult object
            if result and len(result) > 0:
                ocr_result = result[0]
                
                # Lấy dữ liệu từ OCRResult object
                try:
                    # OCRResult có thuộc tính json chứa kết quả
                    if hasattr(ocr_result, 'json'):
                        json_data = ocr_result.json
                        res_data = json_data.get('res', {})
                        
                        rec_texts = res_data.get('rec_texts', [])
                        rec_scores = res_data.get('rec_scores', [])
                        
                        if DEBUG_MODE:
                            print(f"   📝 OCR found {len(rec_texts)} texts: {rec_texts}")
                            print(f"   📊 Scores: {rec_scores}")
                        
                        # Duyệt qua các text đã nhận diện
                        for i, text in enumerate(rec_texts):
                            confidence = rec_scores[i] if i < len(rec_scores) else 0
                            
                            # Lọc kết quả
                            text = str(text).strip().replace(' ', '').replace('.', '').replace(',', '')
                            
                            if text.isdigit():
                                number = int(text)
                                # Game này số từ 1-9
                                if 1 <= number <= 9 and confidence > 0.5:
                                    if DEBUG_MODE:
                                        print(f"   🎯 PaddleOCR: {number} (confidence: {confidence:.2f})")
                                    return number
                    
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"   ⚠️  Lỗi parse OCRResult: {e}")
            
            return 0
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"   ❌ Lỗi PaddleOCR: {e}")
            return 0
    
    def _is_empty_cell(self, cell_img):
        """
        Kiểm tra xem ô có trống không
        
        Args:
            cell_img: Ảnh ô
            
        Returns:
            bool: True nếu ô trống
        """
        # Tính độ lệch chuẩn - ô trống có độ lệch thấp
        std = np.std(cell_img)
        mean = np.mean(cell_img)
        
        # Ô trống thường có std thấp và màu đồng nhất
        if std < 15 and (mean < 50 or mean > 200):
            return True
        
        return False
    
    def _preprocess_cell(self, cell_img):
        """
        Tiền xử lý ảnh để cải thiện độ chính xác OCR
        PaddleOCR yêu cầu ảnh màu (3 channels)
        
        Args:
            cell_img: Ảnh ô gốc
            
        Returns:
            numpy.ndarray: Ảnh đã xử lý (BGR, 3 channels)
        """
        # Đảm bảo ảnh có 3 channels
        if len(cell_img.shape) == 2:
            # Grayscale -> BGR
            cell_img = cv2.cvtColor(cell_img, cv2.COLOR_GRAY2BGR)
        elif len(cell_img.shape) == 3 and cell_img.shape[2] == 4:
            # RGBA -> BGR
            cell_img = cv2.cvtColor(cell_img, cv2.COLOR_RGBA2BGR)
        
        # Tăng độ tương phản
        lab = cv2.cvtColor(cell_img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # Tăng kích thước để OCR đọc tốt hơn
        scale_factor = 3
        height, width = enhanced.shape[:2]
        resized = cv2.resize(enhanced, (width * scale_factor, height * scale_factor), 
                            interpolation=cv2.INTER_CUBIC)
        
        if DEBUG_MODE:
            print(f"   📐 Preprocessed: {resized.shape}")
        
        return resized
    
    def recognize_board(self, grid_cells):
        """
        Nhận diện toàn bộ bảng từ các ô đã tách
        
        Args:
            grid_cells: List 16 ô (4x4) đã tách từ grid
            
        Returns:
            list: Ma trận 4x4 các số nhận diện được
        """
        if len(grid_cells) != 16:
            if DEBUG_MODE:
                print(f"⚠️  Số ô không đúng: {len(grid_cells)}, cần 16 ô")
            return [[0]*4 for _ in range(4)]
        
        board = []
        for i in range(4):
            row = []
            for j in range(4):
                cell_idx = i * 4 + j
                number = self.recognize_number(grid_cells[cell_idx])
                row.append(number)
            board.append(row)
        
        if DEBUG_MODE:
            print("\n📊 Board nhận diện được (PaddleOCR):")
            for row in board:
                print(f"   {row}")
        
        return board


if __name__ == "__main__":
    print("🧪 Testing PaddleRecognizer...")
    recognizer = PaddleRecognizer()
    if recognizer.enabled:
        print("✅ PaddleOCR hoạt động tốt!")
    else:
        print("❌ PaddleOCR không khả dụng")
