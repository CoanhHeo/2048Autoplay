"""
Module chụp màn hình và xử lý ảnh
Chức năng: Chụp vùng game và chuẩn bị ảnh để nhận diện
"""

import mss
import numpy as np
from PIL import Image
import cv2
from config import SCREEN_REGION, DEBUG_MODE


class ScreenCapture:
    """
    Class để chụp màn hình và xử lý ảnh
    """
    
    def __init__(self, region=None):
        """
        Khởi tạo screen capture
        
        Args:
            region (dict): Vùng cần chụp {'top': y, 'left': x, 'width': w, 'height': h}
                          Nếu None, sử dụng giá trị từ config
        """
        self.region = region or SCREEN_REGION
        self.sct = mss.mss()  # Khởi tạo đối tượng chụp màn hình
        
    def capture(self):
        """
        Chụp màn hình vùng game
        
        Returns:
            numpy.ndarray: Ảnh dạng BGR (OpenCV format)
        """
        # Chụp màn hình
        screenshot = self.sct.grab(self.region)
        
        # Chuyển đổi sang numpy array
        img = np.array(screenshot)
        
        # Chuyển từ BGRA sang BGR (loại bỏ alpha channel)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        if DEBUG_MODE:
            print(f"📸 Đã chụp màn hình: {img.shape}")
        
        return img
    
    def preprocess_image(self, img):
        """
        Tiền xử lý ảnh để chuẩn bị cho việc nhận diện
        
        Args:
            img (numpy.ndarray): Ảnh gốc
            
        Returns:
            numpy.ndarray: Ảnh đã được xử lý
        """
        # Chuyển sang ảnh xám
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Áp dụng threshold để tăng độ tương phản
        # THRESH_BINARY: pixel sáng hơn ngưỡng -> trắng, tối hơn -> đen
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Áp dụng Gaussian blur để giảm nhiễu
        blurred = cv2.GaussianBlur(thresh, (5, 5), 0)
        
        if DEBUG_MODE:
            print("🔧 Đã tiền xử lý ảnh")
        
        return blurred
    
    def split_into_grid(self, img, grid_size=4):
        """
        Chia ảnh thành lưới các ô
        
        Args:
            img (numpy.ndarray): Ảnh đã được xử lý
            grid_size (int): Kích thước lưới (4 cho 4x4)
            
        Returns:
            list: Danh sách các ô ảnh [row][col]
        """
        height, width = img.shape[:2]
        cell_height = height // grid_size
        cell_width = width // grid_size
        
        grid = []
        for row in range(grid_size):
            row_cells = []
            for col in range(grid_size):
                # Tính toán vị trí của ô
                y1 = row * cell_height
                y2 = (row + 1) * cell_height
                x1 = col * cell_width
                x2 = (col + 1) * cell_width
                
                # Cắt ô từ ảnh gốc
                cell = img[y1:y2, x1:x2]
                row_cells.append(cell)
            
            grid.append(row_cells)
        
        if DEBUG_MODE:
            print(f"✂️  Đã chia ảnh thành lưới {grid_size}x{grid_size}")
        
        return grid
    
    def save_debug_image(self, img, filename="debug_screenshot.png"):
        """
        Lưu ảnh để debug
        
        Args:
            img (numpy.ndarray): Ảnh cần lưu
            filename (str): Tên file
        """
        cv2.imwrite(filename, img)
        print(f"💾 Đã lưu ảnh debug: {filename}")
    
    def update_region(self, new_region):
        """
        Cập nhật vùng chụp màn hình
        
        Args:
            new_region (dict): Vùng mới
        """
        self.region = new_region
        print(f"🔄 Đã cập nhật vùng chụp: {new_region}")


# Hàm tiện ích để test module
if __name__ == "__main__":
    print("🧪 Testing ScreenCapture module...")
    
    # Tạo đối tượng capture
    capture = ScreenCapture()
    
    # Chụp màn hình
    img = capture.capture()
    
    # Tiền xử lý
    processed = capture.preprocess_image(img)
    
    # Chia thành lưới
    grid = capture.split_into_grid(processed)
    
    # Lưu ảnh debug
    capture.save_debug_image(img, "test_capture.png")
    capture.save_debug_image(processed, "test_processed.png")
    
    print("✅ Test hoàn thành!")
