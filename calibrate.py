"""
Tool để calibrate (hiệu chỉnh) nhận diện số
Giúp tool "học" các số trong game của bạn
"""

import cv2
import sys
from screen_capture import ScreenCapture
from game_state import GameState
from config import GRID_SIZE


def calibrate():
    """
    Chạy calibration - người dùng nhập số thủ công để tool học
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
    print("\n⚠️  Đảm bảo đã setup vùng game (chọn option 1 trong main menu)")
    
    input("\nNhấn Enter để bắt đầu...")
    
    # Khởi tạo
    screen_capture = ScreenCapture()
    game_state = GameState(GRID_SIZE)
    
    print("\n📸 Đang chụp màn hình...")
    img = screen_capture.capture()
    
    # Tiền xử lý
    processed = screen_capture.preprocess_image(img)
    
    # Chia thành lưới
    grid = screen_capture.split_into_grid(processed, GRID_SIZE)
    
    # Lưu ảnh gốc để hiển thị
    grid_original = screen_capture.split_into_grid(img, GRID_SIZE)
    
    print("\n🎓 Bắt đầu calibration...\n")
    
    learned_count = 0
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell_img = grid_original[row][col]
            
            # Hiển thị ô
            cv2.imshow(f"Ô [{row}][{col}]", cell_img)
            cv2.waitKey(1)
            
            print(f"\n📍 Ô [{row}][{col}]:")
            user_input = input("   Nhập số trong ô này (Enter nếu trống, 'q' để thoát): ").strip()
            
            cv2.destroyAllWindows()
            
            if user_input.lower() == 'q':
                print("\n⏹️  Đã dừng calibration")
                break
            
            if user_input == '':
                print("   ⏭️  Bỏ qua (ô trống)")
                continue
            
            if not user_input.isdigit():
                print("   ❌ Không hợp lệ, bỏ qua")
                continue
            
            number = int(user_input)
            
            # Lưu template
            game_state.recognizer.save_template(number, cell_img)
            learned_count += 1
            print(f"   ✅ Đã học số {number}")
        
        else:
            continue
        break
    
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


if __name__ == "__main__":
    try:
        calibrate()
    except KeyboardInterrupt:
        print("\n\n⏹️  Đã dừng")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        sys.exit(1)
