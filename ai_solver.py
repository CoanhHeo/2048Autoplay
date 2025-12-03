"""
Module AI Solver - Thuật toán tự động giải game 2048
Sử dụng thuật toán Expectimax với heuristic tối ưu
"""

import copy
import random
from config import SEARCH_DEPTH, DEBUG_MODE


class AISolver:
    """
    Class chứa thuật toán AI để giải game 2048
    Sử dụng Expectimax: Max node (người chơi) + Chance node (máy spawn ô mới)
    """
    
    def __init__(self, search_depth=SEARCH_DEPTH, spawn_value=1):
        """
        Khởi tạo AI Solver
        
        Args:
            search_depth (int): Độ sâu tìm kiếm Expectimax
            spawn_value (int): Giá trị ô máy sẽ spawn (mặc định: 1)
        """
        self.search_depth = search_depth
        self.initial_depth = search_depth
        self.spawn_value = spawn_value
        self.directions = ['LEFT', 'DOWN', 'RIGHT', 'UP']
        
        # Ma trận trọng số vị trí - Ưu tiên góc DƯỚI TRÁI
        self.position_weights = [
            [6,     5,     4,     3],
            [5,     4,     3,     2],
            [4,     3,     2,     1],
            [15,    14,    13,    12]
        ]
    
    def set_search_depth(self, depth):
        """
        Cập nhật độ sâu tìm kiếm
        
        Args:
            depth (int): Độ sâu mới
        """
        self.search_depth = depth
    
    def set_spawn_value(self, value):
        """
        Cập nhật giá trị ô máy sẽ spawn
        
        Args:
            value (int): Giá trị spawn mới (1-11)
        """
        if 1 <= value <= 11:
            self.spawn_value = value
            print(f"✅ Đã cập nhật spawn_value = {value}")
        else:
            print(f"⚠️  Giá trị spawn phải từ 1-11")
    
    def get_best_move(self, board):
        """
        Tìm nước đi tốt nhất sử dụng thuật toán Expectimax
        
        Max node: Người chơi chọn nước đi tối đa hóa điểm
        Chance node: Máy spawn ô ngẫu nhiên (giá trị: self.spawn_value)
        
        Args:
            board (list): Board 2D hiện tại
            
        Returns:
            str: Hướng đi tốt nhất ('UP', 'DOWN', 'LEFT', 'RIGHT')
        """
        best_move = None
        best_score = -float('inf')
        
        if DEBUG_MODE:
            print("\n🤔 Đang tính toán nước đi tốt nhất...")
        
        # Thử từng hướng đi (Max node - người chơi)
        for direction in self.directions:
            new_board = self.move(board, direction)
            
            # Nếu board không thay đổi (nước đi không hợp lệ), bỏ qua
            if self.boards_equal(board, new_board):
                if DEBUG_MODE:
                    print(f"  {direction}: INVALID")
                continue
            
            # Gọi Expectimax với Chance node (máy spawn ô mới)
            score = self.expectimax(new_board, self.search_depth - 1, False)
            
            if DEBUG_MODE:
                print(f"  {direction}: {score:.0f}")
            
            if score > best_score:
                best_score = score
                best_move = direction
        
        if DEBUG_MODE:
            print(f"✅ Chọn: {best_move} (điểm: {best_score:.0f})")
        
        return best_move
    
    def expectimax(self, board, depth, is_max_player):
        """
        Thuật toán Expectimax
        
        Max node: Người chơi chọn nước đi tốt nhất (tối đa hóa)
        Chance node: Máy spawn ô ngẫu nhiên (giá trị: self.spawn_value)
        
        Args:
            board (list): Board hiện tại
            depth (int): Độ sâu còn lại
            is_max_player (bool): True = Max node, False = Chance node
            
        Returns:
            float: Điểm đánh giá
        """
        # Base case: Hết độ sâu hoặc game over
        if depth == 0 or self.is_terminal(board):
            return self.evaluate_board(board)
        
        if is_max_player:
            # MAX NODE - Người chơi chọn nước đi tốt nhất
            max_score = -float('inf')
            
            for direction in self.directions:
                new_board = self.move(board, direction)
                
                if not self.boards_equal(board, new_board):
                    # Sau khi di chuyển, chuyển sang Chance node
                    score = self.expectimax(new_board, depth - 1, False)
                    max_score = max(max_score, score)
            
            return max_score if max_score != -float('inf') else self.evaluate_board(board)
        
        else:
            # CHANCE NODE - Máy spawn ô tại ô trống ngẫu nhiên
            empty_cells = self.get_empty_cells(board)
            
            if not empty_cells:
                return self.evaluate_board(board)
            
            # Tính điểm trung bình có trọng số của TẤT CẢ khả năng spawn
            total_score = 0
            
            for row, col in empty_cells:
                new_board = copy.deepcopy(board)
                new_board[row][col] = self.spawn_value  # Spawn giá trị đã cấu hình
                
                # Sau khi spawn, chuyển về Max node
                score = self.expectimax(new_board, depth - 1, True)
                total_score += score
            
            # Trả về kỳ vọng (trung bình của tất cả khả năng)
            return total_score / len(empty_cells)
    
    def evaluate_board(self, board):
        """
        Hàm đánh giá Heuristic cho Expectimax
        
        Các yếu tố theo thứ tự ưu tiên:
        1. Monotonicity (Tính đơn điệu) - QUAN TRỌNG NHẤT
        2. Max Tile in Corner (Ô lớn nhất ở góc)
        3. Smoothness (Độ trơn - ô giống nhau nằm cạnh nhau)
        4. Free Tiles (Số ô trống)
        
        Args:
            board (list): Board cần đánh giá
            
        Returns:
            float: Điểm đánh giá heuristic
        """
        size = len(board)
        
        # 1. MONOTONICITY - QUAN TRỌNG NHẤT
        # Snake pattern: các ô sắp xếp giảm dần từ góc
        monotonicity_score = self.calculate_monotonicity_v2(board)
        
        # 2. MAX TILE IN CORNER
        # Giữ ô lớn nhất ở góc (dưới trái hoặc dưới phải)
        max_tile = max(max(row) for row in board)
        corner_score = 0
        
        if board[size-1][0] == max_tile:  # Góc dưới trái (tốt nhất)
            corner_score = 20000
        elif board[size-1][size-1] == max_tile:  # Góc dưới phải
            corner_score = 18000
        elif board[0][0] == max_tile:  # Góc trên trái
            corner_score = 10000
        elif board[0][size-1] == max_tile:  # Góc trên phải
            corner_score = 8000
        else:
            # Penalty nếu số lớn không ở góc
            corner_score = -5000
        
        # 3. SMOOTHNESS (Độ trơn)
        # Khuyến khích các ô giống nhau hoặc gần nhau nằm cạnh nhau
        smoothness_score = self.calculate_smoothness_v2(board)
        
        # 4. FREE TILES (Số ô trống)
        # Càng nhiều ô trống càng tốt - tránh bị kẹt
        empty_cells = len(self.get_empty_cells(board))
        free_tiles_score = empty_cells ** 2 * 300
        
        # Penalty nặng nếu gần đầy board
        if empty_cells <= 2:
            free_tiles_score -= 10000
        elif empty_cells <= 3:
            free_tiles_score -= 5000
        
        # 5. Bonus cho giá trị ô lớn nhất
        max_tile_score = max_tile ** 2 * 10
        
        # 6. MERGE POTENTIAL (Khả năng ghép)
        # Đếm số cặp giống nhau có thể ghép
        merge_score = self.count_mergeable_pairs_v2(board) * 100
        
        # Tổng hợp điểm
        total_score = (
            monotonicity_score * 5.0 +      # Trọng số cao nhất
            corner_score * 1.0 +
            smoothness_score * 2.0 +
            free_tiles_score * 3.0 +        # Rất quan trọng
            max_tile_score * 0.5 +
            merge_score * 1.5
        )
        
        return total_score
    
    def calculate_monotonicity_v2(self, board):
        """
        Tính Monotonicity (Tính đơn điệu)
        
        Đánh giá xem các ô có sắp xếp tăng/giảm dần theo hàng và cột không
        Snake pattern lý tưởng: giảm dần từ góc dưới trái
        
        Args:
            board (list): Board cần đánh giá
            
        Returns:
            float: Điểm monotonicity
        """
        size = len(board)
        score = 0
        
        # Kiểm tra monotonicity theo HÀNG
        for row in range(size):
            # Tính điểm tăng dần và giảm dần
            increasing = 0
            decreasing = 0
            
            for col in range(size - 1):
                curr = board[row][col]
                next_val = board[row][col + 1]
                
                if curr != 0 and next_val != 0:
                    if curr < next_val:
                        increasing += next_val - curr
                    elif curr > next_val:
                        decreasing += curr - next_val
            
            # Lấy max (chọn hướng monotonic tốt hơn)
            # Hàng dưới cùng ưu tiên giảm dần (từ trái sang phải)
            if row == size - 1:
                score += decreasing * 1.5  # Bonus cho hàng dưới
            else:
                score += max(increasing, decreasing)
        
        # Kiểm tra monotonicity theo CỘT
        for col in range(size):
            increasing = 0
            decreasing = 0
            
            for row in range(size - 1):
                curr = board[row][col]
                next_val = board[row + 1][col]
                
                if curr != 0 and next_val != 0:
                    if curr < next_val:
                        increasing += next_val - curr
                    elif curr > next_val:
                        decreasing += curr - next_val
            
            # Cột trái nhất ưu tiên tăng dần (từ trên xuống dưới)
            if col == 0:
                score += increasing * 1.5  # Bonus cho cột trái
            else:
                score += max(increasing, decreasing)
        
        return score
    
    def calculate_smoothness_v2(self, board):
        """
        Tính Smoothness (Độ trơn)
        
        Khuyến khích các ô có giá trị giống nhau hoặc gần nhau nằm cạnh nhau
        
        Args:
            board (list): Board cần đánh giá
            
        Returns:
            float: Điểm smoothness (càng cao càng tốt)
        """
        size = len(board)
        smoothness = 0
        
        for row in range(size):
            for col in range(size):
                if board[row][col] != 0:
                    tile_value = board[row][col]
                    
                    # So sánh với ô bên phải
                    if col < size - 1 and board[row][col + 1] != 0:
                        neighbor = board[row][col + 1]
                        # Penalty theo sự khác biệt
                        smoothness -= abs(tile_value - neighbor)
                    
                    # So sánh với ô bên dưới
                    if row < size - 1 and board[row + 1][col] != 0:
                        neighbor = board[row + 1][col]
                        smoothness -= abs(tile_value - neighbor)
        
        return smoothness
    
    def count_mergeable_pairs_v2(self, board):
        """
        Đếm số cặp ô giống nhau liền kề (có thể ghép)
        Lưu ý: Số 11 (max) không thể ghép
        
        Args:
            board (list): Board cần đánh giá
            
        Returns:
            int: Số cặp có thể ghép
        """
        size = len(board)
        count = 0
        
        for row in range(size):
            for col in range(size):
                if board[row][col] != 0:
                    tile_value = board[row][col]
                    
                    # QUAN TRỌNG: Số 11 không thể ghép
                    if tile_value >= 11:
                        continue
                    
                    # Kiểm tra bên phải
                    if col < size - 1 and board[row][col + 1] == tile_value:
                        count += 1
                    
                    # Kiểm tra bên dưới
                    if row < size - 1 and board[row + 1][col] == tile_value:
                        count += 1
        
        return count
    

    
    def move(self, board, direction):
        """
        Mô phỏng di chuyển board theo hướng cho trước
        
        Args:
            board (list): Board hiện tại
            direction (str): Hướng di chuyển
            
        Returns:
            list: Board mới sau khi di chuyển
        """
        new_board = copy.deepcopy(board)
        size = len(new_board)
        
        if direction == 'LEFT':
            for row in range(size):
                new_board[row] = self.merge_line(new_board[row])
        
        elif direction == 'RIGHT':
            for row in range(size):
                new_board[row] = self.merge_line(new_board[row][::-1])[::-1]
        
        elif direction == 'UP':
            for col in range(size):
                column = [new_board[row][col] for row in range(size)]
                merged = self.merge_line(column)
                for row in range(size):
                    new_board[row][col] = merged[row]
        
        elif direction == 'DOWN':
            for col in range(size):
                column = [new_board[row][col] for row in range(size)]
                merged = self.merge_line(column[::-1])[::-1]
                for row in range(size):
                    new_board[row][col] = merged[row]
        
        return new_board
    
    def merge_line(self, line):
        """
        Ghép một hàng/cột theo luật của game này:
        - Hai số GIỐNG NHAU ghép lại thành số TIẾP THEO
        - 1+1→2, 2+2→3, 3+3→4, ..., 10+10→11
        - QUAN TRỌNG: 11+11 KHÔNG ghép được (11 là số max)
        
        Args:
            line (list): Danh sách các giá trị trong hàng
            
        Returns:
            list: Hàng sau khi ghép
        """
        # Loại bỏ các ô trống và dồn về bên trái
        non_zero = [x for x in line if x != 0]
        
        if len(non_zero) == 0:
            return [0] * len(line)
        
        # Ghép các ô liền kề
        merged = []
        skip = False
        
        for i in range(len(non_zero)):
            if skip:
                skip = False
                continue
            
            # Kiểm tra có thể ghép với ô tiếp theo không
            if i < len(non_zero) - 1:
                current = non_zero[i]
                next_val = non_zero[i + 1]
                
                # Luật game: Chỉ ghép khi 2 số GIỐNG NHAU
                # NGOẠI LỆ: Số 11 (max) không thể ghép
                if current == next_val and current < 11:
                    merged.append(current + 1)  # 1+1=2, 2+2=3, ..., 10+10=11
                    skip = True
                else:
                    merged.append(current)
            else:
                # Ô cuối cùng, không thể ghép
                merged.append(non_zero[i])
        
        # Thêm các ô trống vào cuối
        while len(merged) < len(line):
            merged.append(0)
        
        return merged
    
    def boards_equal(self, board1, board2):
        """
        So sánh hai board có giống nhau không
        
        Args:
            board1 (list): Board thứ nhất
            board2 (list): Board thứ hai
            
        Returns:
            bool: True nếu hai board giống nhau
        """
        return board1 == board2
    
    def get_empty_cells(self, board):
        """
        Lấy danh sách các ô trống
        
        Args:
            board (list): Board hiện tại
            
        Returns:
            list: Danh sách tuple (row, col) của các ô trống
        """
        empty = []
        for row in range(len(board)):
            for col in range(len(board[0])):
                if board[row][col] == 0:
                    empty.append((row, col))
        return empty
    
    def is_terminal(self, board):
        """
        Kiểm tra xem board có phải trạng thái kết thúc không
        
        Args:
            board (list): Board cần kiểm tra
            
        Returns:
            bool: True nếu game over
        """
        # Nếu còn ô trống thì chưa kết thúc
        if self.get_empty_cells(board):
            return False
        
        # Kiểm tra xem còn nước đi hợp lệ không
        for direction in self.directions:
            new_board = self.move(board, direction)
            if not self.boards_equal(board, new_board):
                return False
        
        return True


# Hàm tiện ích để test module
if __name__ == "__main__":
    print("🧪 Testing AISolver module...")
    
    # Tạo một board mẫu
    test_board = [
        [2, 4, 0, 0],
        [0, 2, 0, 0],
        [4, 0, 2, 0],
        [0, 0, 0, 0]
    ]
    
    # Tạo AI solver
    ai = AISolver(search_depth=3)
    
    print("Board ban đầu:")
    for row in test_board:
        print(row)
    
    print("\nĐang tìm nước đi tốt nhất...")
    best_move = ai.get_best_move(test_board)
    
    print(f"\n✅ Nước đi tốt nhất: {best_move}")
    
    # Test merge line theo luật: n+n=n+1
    print("\n🧪 Test merge_line (luật: n+n=n+1):")
    test_lines = [
        ([1, 1, 0, 0], "1+1→2"),
        ([2, 2, 3, 3], "2+2→3, 3+3→4"),
        ([1, 0, 1, 0], "Có ô trống, 1+1→2"),
        ([1, 1, 1, 1], "4 ô số 1 → 1+1=2, 1+1=2"),
        ([4, 4, 4, 0], "3 ô số 4 → 4+4=5, 4 còn lại"),
        ([1, 2, 3, 4], "Không ghép được (khác nhau)"),
        ([7, 7, 8, 8], "7+7→8, 8+8→9")
    ]
    
    for line, desc in test_lines:
        merged = ai.merge_line(line)
        print(f"{line} -> {merged}  ({desc})")
    
    print("\n✅ Test hoàn thành!")
