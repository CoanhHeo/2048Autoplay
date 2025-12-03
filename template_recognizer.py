"""
Module nhận diện số bằng Template Matching
Phù hợp cho icon/hình ảnh đá quý trong game
"""

import cv2
import numpy as np
from pathlib import Path
import pickle
from config import DEBUG_MODE


class TemplateRecognizer:
    """
    Class nhận diện số bằng Template Matching
    So khớp hình ảnh trực tiếp, không dùng OCR
    """
    
    def __init__(self):
        """
        Khởi tạo Template Recognizer
        """
        self.templates = {}  # {number: template_image}
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Load templates đã lưu
        self.load_templates()
        
        self.enabled = True
        if DEBUG_MODE:
            print(f"✅ TemplateRecognizer đã sẵn sàng ({len(self.templates)} templates)")
    
    def recognize_number(self, cell_img):
        """
        Nhận diện số từ một ô bằng template matching
        
        Args:
            cell_img: Ảnh ô game (numpy array)
            
        Returns:
            int: Số nhận diện được (0 nếu ô trống hoặc lỗi)
        """
        if not self.enabled:
            return 0
        
        if cell_img is None or cell_img.size == 0:
            return 0
        
        # Kiểm tra ô trống
        if self._is_empty_cell(cell_img):
            return 0
        
        # Nếu chưa có template, không thể nhận diện
        if not self.templates:
            if DEBUG_MODE:
                print("   ⚠️  Chưa có templates! Hãy chạy calibration (option 1)")
            return 0
        
        try:
            # Tiền xử lý ảnh
            processed = self._preprocess_cell(cell_img)
            
            best_match = 0
            best_score = 0
            
            # So khớp với từng template
            for number, template in self.templates.items():
                score = self._match_template(processed, template)
                
                if score > best_score:
                    best_score = score
                    best_match = number
            
            # Ngưỡng tin cậy (60%)
            if best_score > 0.6:
                if DEBUG_MODE:
                    print(f"   🎯 Template: {best_match} (score: {best_score:.2f})")
                return best_match
            else:
                if DEBUG_MODE:
                    print(f"   ⚠️  Low confidence: {best_score:.2f}")
            
            return 0
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"   ❌ Lỗi Template Matching: {e}")
            return 0
    
    def _is_empty_cell(self, cell_img):
        """
        Kiểm tra xem ô có trống không
        
        Args:
            cell_img: Ảnh ô
            
        Returns:
            bool: True nếu ô trống
        """
        std = np.std(cell_img)
        mean = np.mean(cell_img)
        
        # Ô trống có độ lệch chuẩn thấp và màu đồng nhất
        return std < 15 and (mean < 50 or mean > 200)
    
    def _preprocess_cell(self, cell_img):
        """
        Tiền xử lý ảnh để so khớp template
        
        Args:
            cell_img: Ảnh ô gốc
            
        Returns:
            numpy.ndarray: Ảnh đã xử lý
        """
        # Chuyển sang BGR nếu cần
        if len(cell_img.shape) == 2:
            processed = cv2.cvtColor(cell_img, cv2.COLOR_GRAY2BGR)
        elif len(cell_img.shape) == 3 and cell_img.shape[2] == 4:
            processed = cv2.cvtColor(cell_img, cv2.COLOR_RGBA2BGR)
        else:
            processed = cell_img.copy()
        
        # Resize về kích thước chuẩn
        target_size = (100, 100)
        resized = cv2.resize(processed, target_size, interpolation=cv2.INTER_AREA)
        
        return resized
    
    def _match_template(self, img, template):
        """
        So khớp ảnh với template
        
        Args:
            img: Ảnh cần so khớp
            template: Template mẫu
            
        Returns:
            float: Điểm số tương đồng (0-1)
        """
        # Đảm bảo cùng kích thước
        if img.shape != template.shape:
            template = cv2.resize(template, (img.shape[1], img.shape[0]))
        
        # Phương pháp 1: Template Matching trực tiếp
        result1 = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        score1 = result1[0, 0]
        
        # Phương pháp 2: Histogram comparison
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        hist_img = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
        hist_template = cv2.calcHist([template_gray], [0], None, [256], [0, 256])
        
        cv2.normalize(hist_img, hist_img)
        cv2.normalize(hist_template, hist_template)
        
        score2 = cv2.compareHist(hist_img, hist_template, cv2.HISTCMP_CORREL)
        
        # Phương pháp 3: Color histogram (HSV)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        template_hsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        
        hist_img_hsv = cv2.calcHist([img_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        hist_template_hsv = cv2.calcHist([template_hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
        
        cv2.normalize(hist_img_hsv, hist_img_hsv)
        cv2.normalize(hist_template_hsv, hist_template_hsv)
        
        score3 = cv2.compareHist(hist_img_hsv, hist_template_hsv, cv2.HISTCMP_CORREL)
        
        # Kết hợp các điểm số (weighted average)
        final_score = (score1 * 0.5 + score2 * 0.25 + score3 * 0.25)
        
        return final_score
    
    def save_template(self, number, cell_img):
        """
        Lưu template cho một số
        
        Args:
            number: Số cần lưu (1-11, 11 là max của game)
            cell_img: Ảnh mẫu
        """
        if number < 1 or number > 11:
            return
        
        try:
            # Tiền xử lý
            processed = self._preprocess_cell(cell_img)
            
            # Lưu vào memory
            self.templates[number] = processed
            
            # Lưu ra file
            template_file = self.templates_dir / f"template_{number}.pkl"
            with open(template_file, 'wb') as f:
                pickle.dump(processed, f)
            
            if DEBUG_MODE:
                print(f"   💾 Đã lưu template cho số {number}")
            
        except Exception as e:
            if DEBUG_MODE:
                print(f"   ❌ Lỗi lưu template: {e}")
    
    def load_templates(self):
        """
        Load templates đã lưu từ file
        """
        try:
            for template_file in self.templates_dir.glob("template_*.pkl"):
                number = int(template_file.stem.split('_')[1])
                
                with open(template_file, 'rb') as f:
                    template = pickle.load(f)
                    self.templates[number] = template
            
            if DEBUG_MODE and self.templates:
                print(f"📚 Đã load {len(self.templates)} templates")
                
        except Exception as e:
            if DEBUG_MODE:
                print(f"⚠️  Lỗi load templates: {e}")
    
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
            print("\n📊 Board nhận diện được (Template Matching):")
            for row in board:
                print(f"   {row}")
        
        return board


if __name__ == "__main__":
    print("🧪 Testing TemplateRecognizer...")
    recognizer = TemplateRecognizer()
    if recognizer.enabled:
        print("✅ Template Recognizer hoạt động tốt!")
    else:
        print("❌ Template Recognizer không khả dụng")
