import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Thêm thư mục backend (chứa app/) vào sys.path để import app.* khi chạy pytest
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

