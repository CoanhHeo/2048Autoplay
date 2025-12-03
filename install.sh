#!/bin/bash

# Script cài đặt nhanh cho Auto 2048 Tool trên macOS

echo "🚀 Bắt đầu cài đặt Auto 2048 Tool..."

# Kiểm tra Python
echo ""
echo "📦 Kiểm tra Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 chưa được cài đặt!"
    echo "Vui lòng cài đặt Python 3.8+ từ https://www.python.org/"
    exit 1
fi

python_version=$(python3 --version)
echo "✅ Đã tìm thấy: $python_version"

# Kiểm tra Homebrew
echo ""
echo "🍺 Kiểm tra Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew chưa được cài đặt!"
    echo "Cài đặt Homebrew bằng lệnh:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    exit 1
fi

echo "✅ Homebrew đã được cài đặt"

# Cài đặt Tesseract
echo ""
echo "👁️ Cài đặt Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    tesseract_version=$(tesseract --version | head -n 1)
    echo "✅ Tesseract đã được cài đặt: $tesseract_version"
else
    echo "Đang cài đặt Tesseract..."
    brew install tesseract
    echo "✅ Đã cài đặt Tesseract"
fi

# Tạo virtual environment
echo ""
echo "🐍 Tạo Python virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment đã tồn tại, bỏ qua..."
else
    python3 -m venv venv
    echo "✅ Đã tạo virtual environment"
fi

# Kích hoạt virtual environment
echo ""
echo "🔌 Kích hoạt virtual environment..."
source venv/bin/activate

# Cài đặt dependencies
echo ""
echo "📚 Cài đặt Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Cài đặt hoàn tất!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Bước tiếp theo:"
echo ""
echo "1. Cấp quyền cho Python/Terminal:"
echo "   - System Preferences → Security & Privacy → Privacy"
echo "   - Chọn 'Screen Recording' và thêm Terminal"
echo "   - Chọn 'Accessibility' và thêm Terminal"
echo ""
echo "2. Chạy tool:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. Đọc README.md để biết thêm chi tiết"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
