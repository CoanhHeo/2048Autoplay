"""
Module nhận diện số sử dụng Google Gemini AI
Sử dụng Gemini Vision để nhận diện ma trận 4x4 từ ảnh game
"""

import google.generativeai as genai
from PIL import Image
import numpy as np
import cv2
import json
import os
from dotenv import load_dotenv
from config import DEBUG_MODE

# Load environment variables
load_dotenv()


class GeminiRecognizer:
    """
    Class nhận diện số bằng Gemini AI
    """
    
    def __init__(self, api_key=None):
        """
        Khởi tạo Gemini recognizer
        
        Args:
            api_key (str): Google API key. Nếu None, đọc từ biến môi trường GEMINI_API_KEY
        """
        # Lấy API key
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            print("⚠️  Chưa có GEMINI_API_KEY!")
            print("💡 Hướng dẫn:")
            print("   1. Lấy API key tại: https://aistudio.google.com/app/apikey")
            print("   2. Tạo file .env và thêm: GEMINI_API_KEY=your_api_key_here")
            print("   3. Hoặc set biến môi trường: export GEMINI_API_KEY=your_api_key")
            self.enabled = False
            return
        
        # Cấu hình Gemini
        try:
            genai.configure(api_key=self.api_key)
            
            # Thử các model theo thứ tự ưu tiên (sử dụng tên đầy đủ với prefix models/)
            # Gemini 2.0 Flash Lite - model nhẹ, miễn phí, ít bị giới hạn quota
            model_names = [
                'models/gemini-2.0-flash-lite', # Model nhẹ, quota cao hơn
                'models/gemini-2.5-flash',      # Model mới nhất, nhanh nhất
                'models/gemini-flash-latest',   # Alias cho model flash mới nhất
                'models/gemini-2.0-flash',      # Backup option
                'models/gemini-pro-latest'      # Fallback option
            ]
            
            self.model = None
            for model_name in model_names:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    self.model_name = model_name
                    if DEBUG_MODE:
                        print(f"✅ Gemini AI đã được khởi tạo (model: {model_name})")
                    break
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"⚠️  Model {model_name} không khả dụng: {e}")
                    continue
            
            if self.model is None:
                raise Exception("Không tìm thấy model Gemini khả dụng")
            
            self.enabled = True
        
        except Exception as e:
            print(f"❌ Lỗi khởi tạo Gemini: {e}")
            self.enabled = False
    
    def recognize_board(self, img):
        """
        Nhận diện toàn bộ ma trận 4x4 từ ảnh bằng Gemini
        
        Args:
            img (numpy.ndarray): Ảnh của lưới game
            
        Returns:
            list: Ma trận 4x4 các số, hoặc None nếu thất bại
        """
        if not self.enabled:
            return None
        
        try:
            # Chuyển numpy array sang PIL Image
            if isinstance(img, np.ndarray):
                # Chuyển từ BGR (OpenCV) sang RGB (PIL)
                if len(img.shape) == 3 and img.shape[2] == 3:
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                else:
                    img_rgb = img
                pil_img = Image.fromarray(img_rgb)
            else:
                pil_img = img
            
            # Tạo prompt cho Gemini
            prompt = """
Bạn là một AI chuyên phân tích game 2048. Hãy phân tích ảnh này và trả về ma trận 4x4 các số trong game.

QUAN TRỌNG:
- Ảnh chứa một lưới 4x4 của game 2048
- Mỗi ô có thể chứa số (1, 2, 3, 4, 5, 6, 7, 8, 9, ...) hoặc trống
- Nếu ô trống, trả về 0
- Trả về CHÍNH XÁC dưới dạng JSON với format:
{
  "board": [
    [a, b, c, d],
    [e, f, g, h],
    [i, j, k, l],
    [m, n, o, p]
  ]
}

Trong đó a, b, c, ... là các số trong ô tương ứng (0 nếu trống).

CHỈ trả về JSON, không thêm text nào khác.
"""
            
            if DEBUG_MODE:
                print("🤖 Đang gọi Gemini AI để nhận diện...")
            
            # Gọi Gemini API
            response = self.model.generate_content([prompt, pil_img])
            
            # Parse response
            response_text = response.text.strip()
            
            if DEBUG_MODE:
                print(f"📝 Gemini response: {response_text}")
            
            # Xử lý response - loại bỏ markdown code block nếu có
            if response_text.startswith('```'):
                # Loại bỏ ```json và ```
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1])
            
            # Parse JSON
            result = json.loads(response_text)
            board = result.get('board')
            
            if board and len(board) == 4 and all(len(row) == 4 for row in board):
                if DEBUG_MODE:
                    print("✅ Gemini nhận diện thành công!")
                return board
            else:
                print("⚠️  Format response không đúng")
                return None
        
        except json.JSONDecodeError as e:
            print(f"❌ Lỗi parse JSON: {e}")
            if DEBUG_MODE:
                print(f"Response text: {response_text}")
            return None
        
        except Exception as e:
            print(f"❌ Lỗi khi gọi Gemini: {e}")
            return None
    
    def is_available(self):
        """
        Kiểm tra Gemini có sẵn sử dụng không
        
        Returns:
            bool: True nếu có thể sử dụng
        """
        return self.enabled


# Test module
if __name__ == "__main__":
    print("🧪 Testing GeminiRecognizer...")
    
    recognizer = GeminiRecognizer()
    
    if recognizer.is_available():
        print("✅ Gemini sẵn sàng sử dụng")
    else:
        print("❌ Gemini chưa sẵn sàng")
        print("Cần setup GEMINI_API_KEY")
