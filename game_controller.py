"""
Module điều khiển game
Chức năng: Gửi phím mũi tên để điều khiển game
"""

import pyautogui
import time
from config import MOVE_DELAY, DEBUG_MODE


class GameController:
    """
    Class để điều khiển game bằng cách gửi phím
    """
    
    def __init__(self, move_delay=MOVE_DELAY):
        """
        Khởi tạo GameController
        
        Args:
            move_delay (float): Thời gian chờ giữa các nước đi (giây)
        """
        self.move_delay = move_delay
        
        # Mapping từ direction string sang key name của pyautogui
        self.key_mapping = {
            'UP': 'up',
            'DOWN': 'down',
            'LEFT': 'left',
            'RIGHT': 'right'
        }
        
        # Cấu hình pyautogui
        pyautogui.PAUSE = 0.1  # Thời gian chờ giữa các lệnh pyautogui
        pyautogui.FAILSAFE = True  # Di chuột lên góc màn hình để dừng khẩn cấp
        
        if DEBUG_MODE:
            print("🎮 GameController đã khởi tạo")
            print("⚠️  Để dừng khẩn cấp, di chuột lên góc trên bên trái màn hình")
    
    def send_move(self, direction):
        """
        Gửi một nước đi đến game
        
        Args:
            direction (str): Hướng di chuyển ('UP', 'DOWN', 'LEFT', 'RIGHT')
            
        Returns:
            bool: True nếu gửi thành công
        """
        if direction not in self.key_mapping:
            print(f"❌ Hướng không hợp lệ: {direction}")
            return False
        
        try:
            # Lấy key name tương ứng
            key = self.key_mapping[direction]
            
            if DEBUG_MODE:
                print(f"⌨️  Gửi phím: {direction} ({key})")
            
            # Gửi phím
            pyautogui.press(key)
            
            # Chờ một chút để game xử lý
            time.sleep(self.move_delay)
            
            return True
            
        except pyautogui.FailSafeException:
            print("🛑 Đã dừng khẩn cấp (FailSafe)")
            return False
        except Exception as e:
            print(f"❌ Lỗi khi gửi phím: {e}")
            return False
    
    def send_moves(self, directions):
        """
        Gửi nhiều nước đi liên tiếp
        
        Args:
            directions (list): Danh sách các hướng di chuyển
            
        Returns:
            int: Số nước đi đã gửi thành công
        """
        success_count = 0
        
        for direction in directions:
            if self.send_move(direction):
                success_count += 1
            else:
                break  # Dừng nếu có lỗi
        
        return success_count
    
    def click_position(self, x, y):
        """
        Click vào một vị trí cụ thể trên màn hình
        (Hữu ích để focus vào cửa sổ game)
        
        Args:
            x (int): Tọa độ X
            y (int): Tọa độ Y
        """
        try:
            if DEBUG_MODE:
                print(f"🖱️  Click vào vị trí ({x}, {y})")
            
            pyautogui.click(x, y)
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Lỗi khi click: {e}")
    
    def focus_game_window(self, window_x, window_y):
        """
        Focus vào cửa sổ game bằng cách click vào nó
        
        Args:
            window_x (int): Tọa độ X của cửa sổ game
            window_y (int): Tọa độ Y của cửa sổ game
        """
        if DEBUG_MODE:
            print("🎯 Đang focus vào cửa sổ game...")
        
        self.click_position(window_x, window_y)
    
    def wait(self, seconds):
        """
        Chờ một khoảng thời gian
        
        Args:
            seconds (float): Số giây cần chờ
        """
        if DEBUG_MODE:
            print(f"⏳ Chờ {seconds} giây...")
        time.sleep(seconds)
    
    def set_move_delay(self, delay):
        """
        Cập nhật thời gian chờ giữa các nước đi
        
        Args:
            delay (float): Thời gian chờ mới (giây)
        """
        self.move_delay = delay
        if DEBUG_MODE:
            print(f"⚙️  Đã cập nhật move_delay: {delay}s")
    
    def get_screen_size(self):
        """
        Lấy kích thước màn hình
        
        Returns:
            tuple: (width, height)
        """
        size = pyautogui.size()
        if DEBUG_MODE:
            print(f"🖥️  Kích thước màn hình: {size}")
        return size
    
    def get_mouse_position(self):
        """
        Lấy vị trí hiện tại của chuột
        (Hữu ích để xác định tọa độ cửa sổ game)
        
        Returns:
            tuple: (x, y)
        """
        pos = pyautogui.position()
        if DEBUG_MODE:
            print(f"🖱️  Vị trí chuột: {pos}")
        return pos
    
    def test_keys(self):
        """
        Test gửi tất cả các phím mũi tên
        """
        print("🧪 Testing keys...")
        print("Sẽ gửi: UP, DOWN, LEFT, RIGHT")
        print("Đảm bảo focus vào ứng dụng phù hợp!")
        
        for i in range(3, 0, -1):
            print(f"Bắt đầu trong {i}...")
            time.sleep(1)
        
        for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            print(f"\nGửi: {direction}")
            self.send_move(direction)
            time.sleep(0.5)
        
        print("\n✅ Test hoàn thành!")


# Hàm tiện ích để test module
if __name__ == "__main__":
    print("🧪 Testing GameController module...")
    print("\n⚠️  Cảnh báo: Module này sẽ gửi phím mũi tên đến ứng dụng đang focus!")
    print("Bạn có muốn tiếp tục test không? (y/n)")
    
    response = input().strip().lower()
    
    if response == 'y':
        controller = GameController()
        
        # Hiển thị vị trí chuột hiện tại
        print("\n📍 Di chuyển chuột đến vị trí cửa sổ game và nhấn Enter...")
        input()
        x, y = controller.get_mouse_position()
        print(f"Vị trí đã lưu: ({x}, {y})")
        
        # Test gửi phím
        print("\nBắt đầu test gửi phím trong 3 giây...")
        time.sleep(1)
        
        controller.test_keys()
    else:
        print("❌ Đã hủy test")
