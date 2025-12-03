# 🎮 Chiến Lược Chơi Game Tối Ưu

## 📋 Luật Game
- **Ghép số**: `n + n = n+1` (ví dụ: 1+1→2, 2+2→3, 3+3→4, ..., 8+8→9)
- **Mục tiêu**: Đạt số cao nhất (9) và tránh bị đầy bảng

---

## 🎯 Chiến Lược AI Đã Implement

### 1. **Snake Pattern (Rắn)** 🐍
- Giữ số lớn nhất ở **góc trên trái**
- Các số sắp xếp giảm dần theo pattern zic-zac:
  ```
  [9] [8] [7] [6]
  [2] [3] [4] [5]
  [1] [0] [0] [0]
  [0] [0] [0] [0]
  ```

### 2. **Ưu Tiên Hướng Di Chuyển**
- **LEFT** và **UP**: Ưu tiên cao nhất (bonus 10%)
- **DOWN** và **RIGHT**: Chỉ dùng khi cần thiết
- Lý do: Giữ số lớn ổn định ở góc trên trái

### 3. **Quản Lý Ô Trống** 📊
- Điểm ô trống: `empty_cells² × 200` (tăng mũ để ưu tiên cực cao)
- Penalty nếu ≤2 ô trống: `-5000` điểm
- Mục tiêu: **Luôn giữ ít nhất 3-4 ô trống**

### 4. **Tối Ưu Ghép Số** ♟️
- Thưởng cho **cặp số giống nhau liền kề**: `+100` điểm/cặp
- Penalty cho **số chênh lệch >2 liền kề**: `-10` điểm/đơn vị chênh lệch
- Khuyến khích nhóm các số giống nhau lại gần nhau

### 5. **Monotonicity (Đơn điệu)** 📈
- Thưởng cho hàng/cột tăng hoặc giảm đều: `+40` điểm
- Tránh trạng thái lộn xộn, khó ghép

### 6. **Expectimax Algorithm** 🧠
- Độ sâu tìm kiếm: **5 bước**
- Dự đoán các ô spawn ngẫu nhiên
- Tính điểm kỳ vọng cho mỗi nước đi

---

## 🏆 Hệ Thống Điểm Đánh Giá

| Yếu tố | Công thức | Trọng số |
|--------|-----------|----------|
| Ô trống | `empty² × 200` | Cao nhất |
| Số lớn nhất | `max² × 50` | Cao |
| Vị trí góc | `+2000` (góc trên trái) | Rất cao |
| Snake pattern | `pattern × 30` | Trung bình |
| Cặp ghép được | `pairs × 100` | Cao |
| Chênh lệch lớn | `-diff × 10` | Penalty |
| Monotonicity | `mono × 40` | Trung bình |
| Tổng giá trị | `total × 5` | Thấp |
| Gần đầy | `-5000` (≤2 ô trống) | Penalty lớn |

---

## 💡 Tips Cho AI

### ✅ **Nên làm:**
1. Luôn ưu tiên LEFT hoặc UP
2. Giữ số lớn nhất ở góc trên trái
3. Tạo snake pattern từ góc
4. Nhóm các số giống nhau lại gần nhau
5. Giữ ít nhất 30-40% ô trống

### ❌ **Không nên:**
1. Dùng RIGHT hoặc DOWN trừ khi bắt buộc
2. Để số lớn ở giữa bảng
3. Tạo các số chênh lệch lớn liền kề
4. Để board đầy >75% (12/16 ô)
5. Di chuyển ngẫu nhiên không có kế hoạch

---

## 🎲 Ví Dụ Tốt vs Xấu

### ✅ Board TỐT:
```
[8] [7] [6] [5]
[1] [2] [3] [4]
[0] [0] [0] [0]
[0] [0] [0] [0]
```
- Số lớn ở góc ✓
- Snake pattern rõ ràng ✓
- Nhiều ô trống ✓
- Số sắp xếp đều ✓

### ❌ Board XẤU:
```
[1] [8] [2] [7]
[5] [1] [6] [3]
[2] [4] [3] [5]
[7] [2] [8] [1]
```
- Số lớn rải rác ✗
- Không có pattern ✗
- Ít ô trống ✗
- Số lộn xộn ✗

---

## 🔧 Tùy Chỉnh

Trong `config.py`:
```python
SEARCH_DEPTH = 5    # Giảm xuống 3-4 nếu chậm
MOVE_DELAY = 1.0    # Điều chỉnh theo nhu cầu
```

Trong `ai_solver.py`:
- Thay đổi trọng số trong `evaluate_board()`
- Thay đổi `preferred_directions` để thử chiến lược khác
- Điều chỉnh bonus/penalty cho các yếu tố

---

## 📊 Kết Quả Kỳ Vọng

Với thuật toán này:
- **Đạt số 7-8**: Dễ dàng (90% game)
- **Đạt số 9**: Có thể (50-70% game)
- **Điểm trung bình**: 150-250
- **Tránh thua**: >95% thời gian

---

## 🚀 Chạy Tool

```bash
python main.py
```

Chọn:
- **Option 1**: Setup vùng game
- **Option 6**: Test nhận diện
- **Option 4**: Chạy auto mode

Good luck! 🎯
