"""
Main - File chính để chạy tool Auto 2048
Kết hợp tất cả các module để tạo thành tool hoàn chỉnh
"""

import time
import sys
from dotenv import load_dotenv
from screen_capture import ScreenCapture
from game_state import GameState
from ai_solver import AISolver
from game_controller import GameController
from config import SCREEN_REGION, GRID_SIZE, SEARCH_DEPTH, MOVE_DELAY, DEBUG_MODE

# Load environment variables (cho Gemini API key)
load_dotenv()


class Auto2048:
    """
    Class chính điều phối toàn bộ tool
    """
    
    def __init__(self):
        """
        Khởi tạo tool
        """
        print("🚀 Đang khởi tạo Auto 2048 Tool...")
        
        # Khởi tạo các component
        self.screen_capture = ScreenCapture()
        self.game_state = GameState(GRID_SIZE)
        self.ai_solver = AISolver(SEARCH_DEPTH)
        self.game_controller = GameController(MOVE_DELAY)
        
        # Biến trạng thái
        self.is_running = False
        self.move_count = 0
        self.best_score = 0
        
        print("✅ Khởi tạo thành công!")
    
    def setup_game_region(self):
        """
        Hướng dẫn người dùng setup vùng chụp game
        """
        print("\n" + "="*60)
        print("📍 SETUP VÙ NƠM GAME")
        print("="*60)
        print("\nBước 1: Mở game và hiển thị mini game 2048")
        print("Bước 2: Di chuyển chuột đến góc TRÊN TRÁI của lưới game")
        print("Bước 3: Nhấn Enter...")
        input()
        
        # Lấy tọa độ góc trên trái
        top_left = self.game_controller.get_mouse_position()
        print(f"✅ Đã lưu góc trên trái: {top_left}")
        
        print("\nBước 4: Di chuyển chuột đến góc DƯỚI PHẢI của lưới game")
        print("Bước 5: Nhấn Enter...")
        input()
        
        # Lấy tọa độ góc dưới phải
        bottom_right = self.game_controller.get_mouse_position()
        print(f"✅ Đã lưu góc dưới phải: {bottom_right}")
        
        # Tính toán vùng chụp
        region = {
            'top': top_left[1],
            'left': top_left[0],
            'width': bottom_right[0] - top_left[0],
            'height': bottom_right[1] - top_left[1]
        }
        
        print(f"\n📊 Vùng chụp đã được thiết lập:")
        print(f"   Top: {region['top']}")
        print(f"   Left: {region['left']}")
        print(f"   Width: {region['width']}")
        print(f"   Height: {region['height']}")
        
        # Cập nhật vùng chụp
        self.screen_capture.update_region(region)
        
        # Test chụp màn hình
        print("\n🧪 Test chụp màn hình...")
        img = self.screen_capture.capture()
        self.screen_capture.save_debug_image(img, "setup_test.png")
        print("✅ Đã lưu ảnh test: setup_test.png")
        print("   Hãy kiểm tra file này để đảm bảo vùng chụp đúng!")
        
        return region
    
    def capture_and_analyze(self):
        """
        Chụp màn hình và phân tích trạng thái game
        
        Returns:
            list: Board hiện tại, hoặc None nếu thất bại
        """
        try:
            # Chụp màn hình
            img = self.screen_capture.capture()
            
            # Tiền xử lý ảnh
            processed = self.screen_capture.preprocess_image(img)
            
            # Chia thành lưới
            grid = self.screen_capture.split_into_grid(processed, GRID_SIZE)
            
            # Nhận diện trạng thái (truyền cả ảnh đầy đủ cho Gemini)
            board = self.game_state.update_from_grid(grid, full_image=img)
            
            # Lưu ảnh debug nếu cần
            if DEBUG_MODE:
                self.screen_capture.save_debug_image(img, f"capture_{self.move_count}.png")
            
            return board
            
        except Exception as e:
            print(f"❌ Lỗi khi phân tích game: {e}")
            return None
    
    def make_move(self, direction):
        """
        Thực hiện một nước đi
        
        Args:
            direction (str): Hướng di chuyển
            
        Returns:
            bool: True nếu thành công
        """
        if direction is None:
            print("⚠️  Không tìm thấy nước đi hợp lệ!")
            return False
        
        # Gửi phím
        success = self.game_controller.send_move(direction)
        
        if success:
            self.move_count += 1
            print(f"✅ Nước đi #{self.move_count}: {direction}")
        
        return success
    
    def run_auto(self, max_moves=None, auto_learn=False):
        """
        Chạy auto với số lượng nước đi giới hạn hoặc không giới hạn
        
        Args:
            max_moves (int): Số nước đi tối đa (None = không giới hạn)
            auto_learn (bool): Tự động train Tesseract từ kết quả Gemini
        """
        print("\n" + "="*60)
        print("🤖 BẮT ĐẦU CHẠY AUTO")
        print("="*60)
        print(f"AI Model: {self.game_state.ai_model.upper()}")
        print(f"Độ sâu tìm kiếm: {SEARCH_DEPTH}")
        print(f"Thời gian chờ giữa nước đi: {MOVE_DELAY}s")
        if auto_learn:
            print("🎓 Chế độ: AUTO + LEARN (Gemini train Tesseract)")
        if max_moves:
            print(f"Số nước đi tối đa: {max_moves}")
        else:
            print("Số nước đi: Không giới hạn")
        print("\n⚠️  Nhấn Ctrl+C để dừng")
        print("⚠️  Di chuột lên góc trên trái màn hình để dừng khẩn cấp")
        
        # Đếm ngược
        for i in range(3, 0, -1):
            print(f"\nBắt đầu trong {i}...")
            time.sleep(1)
        
        print("\n🎮 Đang chạy...\n")
        
        self.is_running = True
        self.move_count = 0
        learned_count = 0  # Đếm số template đã học
        
        try:
            while self.is_running:
                # Kiểm tra giới hạn nước đi
                if max_moves and self.move_count >= max_moves:
                    print(f"\n✅ Đã đạt số nước đi tối đa: {max_moves}")
                    break
                
                # Chụp màn hình
                img = self.screen_capture.capture()
                processed = self.screen_capture.preprocess_image(img)
                grid = self.screen_capture.split_into_grid(img, GRID_SIZE)
                
                # Phân tích bằng AI model hiện tại
                board = self.game_state.update_from_grid(grid, full_image=img)
                
                if board is None:
                    print("❌ Không thể phân tích game!")
                    break
                
                # Auto-learn: Dùng kết quả Gemini để train Tesseract
                if auto_learn and self.game_state.ai_model == 'gemini':
                    for row in range(GRID_SIZE):
                        for col in range(GRID_SIZE):
                            number = board[row][col]
                            if number > 0:  # Chỉ học các ô có số
                                cell_img = grid[row][col]
                                self.game_state.recognizer.save_template(number, cell_img)
                                learned_count += 1
                    
                    if self.move_count % 5 == 0 and learned_count > 0:  # Thông báo mỗi 5 moves
                        print(f"🎓 Đã học {learned_count} templates cho Tesseract")
                
                # Kiểm tra game over
                if self.game_state.is_game_over():
                    print("\n🎮 Game Over!")
                    break
                
                # Tính điểm hiện tại
                current_score = self.game_state.get_score()
                max_tile = self.game_state.get_max_tile()
                
                if current_score > self.best_score:
                    self.best_score = current_score
                
                # Đếm số lượng ô trống (số 0)
                count_empty = sum(1 for row in board for cell in row if cell == 0)
                
                # Tự động điều chỉnh search_depth dựa trên số ô trống
                old_depth = self.ai_solver.search_depth
                new_depth = 5  # Mặc định
                
                if count_empty < 1:
                    new_depth = 10
                elif count_empty < 2:
                    new_depth = 9
                elif count_empty < 3:
                    new_depth = 8
                elif count_empty < 4:
                    new_depth = 7
                elif count_empty < 5:
                    new_depth = 6
                else:
                    new_depth = 5
                
                # Cập nhật nếu thay đổi
                if new_depth != old_depth:
                    self.ai_solver.set_search_depth(new_depth)
                    print(f"🧠 Điều chỉnh SEARCH_DEPTH: {old_depth} → {new_depth} (Ô trống: {count_empty})")
                
                print(f"📊 Điểm: {current_score} | Ô lớn nhất: {max_tile} | Ô trống: {count_empty} | Nước đi: {self.move_count} | Depth: {self.ai_solver.search_depth}")
                
                # Tìm nước đi tốt nhất
                best_move = self.ai_solver.get_best_move(board)
                
                # Thực hiện nước đi
                if not self.make_move(best_move):
                    break
                
                # Chờ một chút để game xử lý
                time.sleep(0.05)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Đã dừng bởi người dùng")
        
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
        
        finally:
            self.is_running = False
            self.print_summary()
            
            if auto_learn and learned_count > 0:
                print(f"\n🎓 TỔNG KẾT AUTO-LEARN:")
                print(f"   Đã học {learned_count} templates")
                print(f"   Templates đã lưu vào thư mục 'templates/'")
                print(f"   💡 Bây giờ có thể chuyển sang Tesseract (option 7 → 3)")
    
    def print_summary(self):
        """
        In ra thống kê sau khi chạy
        """
        print("\n" + "="*60)
        print("📊 THỐNG KÊ")
        print("="*60)
        print(f"Tổng số nước đi: {self.move_count}")
        print(f"Điểm cao nhất: {self.best_score}")
        print(f"Ô lớn nhất: {self.game_state.get_max_tile()}")
        print("="*60)
    
    def run_calibration(self):
        """
        Chạy calibration - dạy tool nhận diện số
        """
        print("""
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║        🎯 CALIBRATION TOOL 🎓            ║
    ║                                           ║
    ║   Giúp tool học nhận diện số trong game  ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
        """)
        
        print("\n📋 Hướng dẫn:")
        print("1. Mở game và hiển thị mini game 2048")
        print("2. Tool sẽ chụp từng ô")
        print("3. Bạn nhập số trong ô đó (hoặc Enter nếu ô trống)")
        print("4. Tool sẽ học và lưu lại")
        
        input("\nNhấn Enter để bắt đầu...")
        
        # Hiển thị thông tin vùng chụp
        print(f"\n📊 Vùng chụp hiện tại:")
        print(f"   Top: {self.screen_capture.region['top']}")
        print(f"   Left: {self.screen_capture.region['left']}")
        print(f"   Width: {self.screen_capture.region['width']}")
        print(f"   Height: {self.screen_capture.region['height']}")
        
        print("\n📸 Đang chụp màn hình...")
        img = self.screen_capture.capture()
        
        # Lưu ảnh gốc để kiểm tra
        self.screen_capture.save_debug_image(img, "calibration_capture.png")
        print("💾 Đã lưu ảnh gốc: calibration_capture.png (kiểm tra xem vùng chụp có đúng không)")
        
        # Tiền xử lý
        processed = self.screen_capture.preprocess_image(img)
        
        # Chia thành lưới
        grid = self.screen_capture.split_into_grid(processed, GRID_SIZE)
        grid_original = self.screen_capture.split_into_grid(img, GRID_SIZE)
        
        print("\n🎓 Bắt đầu calibration...\n")
        
        # Tạo ma trận để hiển thị
        calibration_board = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        learned_count = 0
        
        def print_calibration_board():
            """In ma trận calibration hiện tại"""
            print("\n" + "="*50)
            print("📊 MA TRẬN CALIBRATION HIỆN TẠI:")
            print("┌" + "─────┬" * (GRID_SIZE - 1) + "─────┐")
            for i, row in enumerate(calibration_board):
                print("│", end="")
                for cell in row:
                    if cell == '':
                        print("  ?  │", end="")
                    else:
                        print(f" {cell:^3s} │", end="")
                print()
                if i < GRID_SIZE - 1:
                    print("├" + "─────┼" * (GRID_SIZE - 1) + "─────┤")
            print("└" + "─────┴" * (GRID_SIZE - 1) + "─────┘")
            print("="*50 + "\n")
        
        try:
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    cell_img = grid_original[row][col]
                    
                    # Hiển thị ma trận trước khi nhập
                    print_calibration_board()
                    
                    # Hiển thị ô
                    import cv2
                    cv2.imshow(f"Ô [{row}][{col}]", cell_img)
                    cv2.waitKey(1)
                    
                    print(f"📍 Đang calibrate ô [{row}][{col}] (hàng {row+1}, cột {col+1}):")
                    user_input = input("   Nhập số trong ô này (Enter nếu trống, 'q' để thoát): ").strip()
                    
                    cv2.destroyAllWindows()
                    
                    if user_input.lower() == 'q':
                        print("\n⏹️  Đã dừng calibration")
                        break
                    
                    if user_input == '':
                        print("   ⏭️  Bỏ qua (ô trống)")
                        calibration_board[row][col] = '-'
                        continue
                    
                    if not user_input.isdigit():
                        print("   ❌ Không hợp lệ, bỏ qua")
                        calibration_board[row][col] = '❌'
                        continue
                    
                    number = int(user_input)
                    
                    # Cập nhật ma trận
                    calibration_board[row][col] = str(number)
                    
                    # Lưu template - kiểm tra AI model đang dùng
                    if self.game_state.ai_model == 'template' and self.game_state.template_recognizer:
                        self.game_state.template_recognizer.save_template(number, cell_img)
                        learned_count += 1
                        print(f"   ✅ Đã học số {number}")
                    elif self.game_state.ai_model == 'gemini':
                        print(f"   ⚠️  Gemini không cần calibration!")
                        calibration_board[row][col] = str(number)
                    else:
                        print(f"   ❌ Không có recognizer để lưu template!")
                        calibration_board[row][col] = '❌'
                
                else:
                    continue
                break
            
            # Hiển thị ma trận cuối cùng
            print_calibration_board()
            
            print(f"\n" + "="*50)
            print(f"🎉 Calibration hoàn tất!")
            print(f"📚 Đã học {learned_count} số")
            print(f"💾 Templates đã lưu vào thư mục 'templates/'")
            print("="*50)
            print("\n💡 Tips:")
            print("- Chạy lại calibration để thêm số mới")
            print("- Số càng nhiều, nhận diện càng chính xác")
            print("- Nên calibrate với nhiều trạng thái khác nhau của game")
            print("\n✅ Bây giờ bạn có thể chạy tool auto!")
            
        except KeyboardInterrupt:
            print("\n\n⏹️  Đã dừng calibration")
        except Exception as e:
            print(f"\n❌ Lỗi: {e}")
    
    def test_recognition(self):
        """
        Test nhận diện số - chụp màn hình và hiển thị kết quả
        """
        print("""
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║        🧪 TEST RECOGNITION 🔍            ║
    ║                                           ║
    ║   Kiểm tra độ chính xác nhận diện số     ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
        """)
        
        print("\n📋 Hướng dẫn:")
        print("1. Mở game và hiển thị mini game 2048")
        print("2. Tool sẽ chụp màn hình và nhận diện tất cả các số")
        print("3. So sánh kết quả với game thực tế")
        print("4. Nếu sai, chạy Calibration để cải thiện")
        
        choice = input("\nNhấn Enter để test, 'c' để chạy liên tục (Ctrl+C để dừng): ").strip().lower()
        
        continuous = (choice == 'c')
        test_count = 0
        
        try:
            while True:
                test_count += 1
                
                print(f"\n{'='*60}")
                print(f"📸 TEST #{test_count}")
                print('='*60)
                
                # Chụp màn hình
                print("\n📸 Đang chụp màn hình...")
                img = self.screen_capture.capture()
                
                # Tiền xử lý
                processed = self.screen_capture.preprocess_image(img)
                
                # Chia thành lưới
                grid = self.screen_capture.split_into_grid(processed, GRID_SIZE)
                grid_original = self.screen_capture.split_into_grid(img, GRID_SIZE)
                
                # Nhận diện
                print("🔍 Đang nhận diện các số...")
                board = self.game_state.update_from_grid(grid_original)
                
                # Hiển thị kết quả
                print("\n" + "="*60)
                print("🎯 KẾT QUẢ NHẬN DIỆN:")
                print("="*60)
                self.game_state.print_board()
                
                # Thống kê
                total_cells = GRID_SIZE * GRID_SIZE
                recognized_cells = sum(1 for row in board for cell in row if cell > 0)
                empty_cells = sum(1 for row in board for cell in row if cell == 0)
                
                print("\n📊 THỐNG KÊ:")
                print(f"   • Tổng số ô: {total_cells}")
                print(f"   • Ô có số: {recognized_cells}")
                print(f"   • Ô trống: {empty_cells}")
                print(f"   • Số lớn nhất: {self.game_state.get_max_tile()}")
                print(f"   • Tổng điểm: {self.game_state.get_score()}")
                
                # Lưu ảnh debug
                debug_filename = f"test_recognition_{test_count}.png"
                self.screen_capture.save_debug_image(img, debug_filename)
                print(f"\n💾 Đã lưu ảnh: {debug_filename}")
                
                print("\n" + "="*60)
                print("💡 ĐÁNH GIÁ:")
                
                user_feedback = input("\n❓ Kết quả có chính xác không? (y/n/q để thoát): ").strip().lower()
                
                if user_feedback == 'q':
                    print("\n👋 Kết thúc test")
                    break
                elif user_feedback == 'n':
                    print("\n💡 Gợi ý:")
                    print("   1. Chạy Calibration (option 2) để cải thiện")
                    print("   2. Kiểm tra vùng chụp màn hình (option 1)")
                    print("   3. Đảm bảo game hiển thị rõ ràng, không bị che khuất")
                elif user_feedback == 'y':
                    print("\n✅ Tuyệt vời! Tool đã sẵn sàng để chạy auto!")
                
                # Nếu không phải continuous, hỏi có tiếp tục không
                if not continuous:
                    cont = input("\nTest tiếp? (Enter=có, 'q'=thoát): ").strip().lower()
                    if cont == 'q':
                        break
                else:
                    # Trong chế độ continuous, chờ một chút
                    print("\nChờ 2 giây trước khi test tiếp... (Ctrl+C để dừng)")
                    time.sleep(2)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Đã dừng test")
        
        print(f"\n{'='*60}")
        print(f"📊 TỔNG KẾT")
        print(f"{'='*60}")
        print(f"Số lần test: {test_count}")
        print(f"{'='*60}")
        print("\n✅ Hoàn tất!")
    
    def run_interactive(self):
        """
        Chạy ở chế độ interactive (từng bước một)
        """
        print("\n" + "="*60)
        print("👆 CHẾ ĐỘ INTERACTIVE")
        print("="*60)
        print("Nhấn Enter để thực hiện nước đi tiếp theo")
        print("Nhấn 'q' và Enter để thoát")
        print("="*60)
        
        self.is_running = True
        
        try:
            while self.is_running:
                # Chờ người dùng nhấn Enter
                user_input = input("\n👉 Nhấn Enter (hoặc 'q' để thoát): ").strip().lower()
                
                if user_input == 'q':
                    break
                
                # Chụp và phân tích
                board = self.capture_and_analyze()
                
                if board is None:
                    continue
                
                # Kiểm tra game over
                if self.game_state.is_game_over():
                    print("\n🎮 Game Over!")
                    break
                
                # Tìm và thực hiện nước đi
                best_move = self.ai_solver.get_best_move(board)
                self.make_move(best_move)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Đã dừng")
        
        finally:
            self.is_running = False
            self.print_summary()


def main():
    """
    Hàm main
    """
    print("""
    ╔═══════════════════════════════════════════╗
    ║                                           ║
    ║        🎮 AUTO 2048 GAME TOOL 🤖         ║
    ║                                           ║
    ║     Tự động chơi mini game 2048          ║
    ║                                           ║
    ╚═══════════════════════════════════════════╝
    """)
    
    # Khởi tạo tool
    auto = Auto2048()
    
    # Menu
    while True:
        print("\n" + "="*60)
        print("\nMENU")
        print("="*60)
        print("1. Setup vùng game (bắt buộc chạy lần đầu)")
        print("2. Calibration - Dạy tool nhận diện số (Template only)")
        print("3. Chạy auto (tự động liên tục)")
        print("4. Chạy interactive (từng bước một)")
        print("5. Chọn AI model (Template/Gemini) ⚙️")
        print("6. Cài đặt Spawn Value (1-11) 🎲")
        print("7. Thoát")
        print("="*60)
        
        # Hiển thị AI model hiện tại
        current_model = auto.game_state.ai_model.upper() if auto.game_state.ai_model else 'NONE'
        spawn_value = auto.ai_solver.spawn_value
        print(f"🤖 AI model hiện tại: {current_model}")
        print(f"🎲 Spawn value hiện tại: {spawn_value}")
        print("="*60)
        
        choice = input("\nChọn chức năng (1-7): ").strip()
        
        if choice == '1':
            auto.setup_game_region()
        
        elif choice == '2':
            # Calibration - Chỉ cho Template Matching
            if auto.game_state.ai_model != 'template':
                print("\n⚠️  Calibration chỉ dùng cho Template Matching!")
                print("💡 Hãy chuyển sang Template (option 5) trước khi calibrate")
            else:
                auto.run_calibration()
                print("\n💡 GỢI Ý: Thử chuyển AI model khác (option 5)")
        
        elif choice == '3':
            max_moves_input = input("\nSố nước đi tối đa (Enter để không giới hạn): ").strip()
            if max_moves_input.isdigit():
                auto.run_auto(int(max_moves_input), auto_learn=False)
            else:
                auto.run_auto(auto_learn=False)
        
        elif choice == '4':
            auto.run_interactive()
        
        elif choice == '5':
            print("\n⚙️  CHỌN AI MODEL")
            print("="*60)
            current_model = auto.game_state.ai_model.upper() if auto.game_state.ai_model else 'NONE'
            print(f"AI model hiện tại: {current_model}")
            print("\nCác AI model khả dụng:")
            print("1. Template Matching (local, nhanh, tốt cho icon) ⚡")
            print("2. Gemini AI (online, chính xác cao, quota limited) 🤖")
            print("="*60)
            
            ai_choice = input("\nChọn AI model (1-2): ").strip()
            
            new_model = None
            if ai_choice == '1':
                new_model = 'template'
                print("✅ Đã chọn Template Matching")
                print("💡 Lưu ý: Cần calibrate (setup và chạy option 2) để tạo templates!")
            elif ai_choice == '2':
                new_model = 'gemini'
                print("✅ Đã chọn Gemini AI")
            else:
                print("❌ Lựa chọn không hợp lệ!")
            
            if new_model:
                # Cập nhật ngay lập tức
                print("🔄 Đang cập nhật AI model...")
                auto.game_state = GameState(GRID_SIZE, ai_model=new_model)
                print(f"✅ Đã chuyển sang {new_model.upper()}!")
                print("💡 Có thể sử dụng ngay mà không cần restart")
        
        elif choice == '6':
            print("\n🎲 CÀI ĐẶT SPAWN VALUE")
            print("="*60)
            print(f"Spawn value hiện tại: {auto.ai_solver.spawn_value}")
            print("\n💡 Spawn value là giá trị ô mà máy sẽ spawn ngẫu nhiên")
            print("   trong thuật toán Expectimax (Chance node)")
            print("\n📌 Giá trị cho phép: 1-11")
            print("   - Spawn 1: Game dễ hơn, dành cho early game")
            print("   - Spawn 2-3: Cân bằng, thực tế hơn")
            print("   - Spawn 4+: Khó hơn, test chiến lược")
            print("="*60)
            
            spawn_input = input("\nNhập spawn value (1-11): ").strip()
            
            if spawn_input.isdigit():
                spawn_val = int(spawn_input)
                auto.ai_solver.set_spawn_value(spawn_val)
            else:
                print("❌ Giá trị không hợp lệ!")
        
        elif choice == '7':
            print("\n👋 Tạm biệt!")
            sys.exit(0)
        
        else:
            print("❌ Lựa chọn không hợp lệ!")


if __name__ == "__main__":
    main()
