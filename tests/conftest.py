import pytest
import sys
import os

# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db_connection

# --- TẠO LỚP BỌC (WRAPPER) ---
class MockConnection:
    """
    Lớp giả lập Connection.
    Nhiệm vụ: Chặn commit() và rollback() bên trong code ứng dụng
    để giữ cho Transaction test luôn sống đến cuối bài test.
    """
    def __init__(self, real_connection):
        self.real_connection = real_connection

    def commit(self):
        # Chặn commit: Không cho lưu dữ liệu vĩnh viễn
        pass

    def rollback(self):
        # MỚI: Chặn rollback.
        # Lý do: Nếu ứng dụng gọi rollback khi gặp lỗi, nó sẽ xóa luôn
        # cả dữ liệu giả (User, Product) mà ta vừa tạo để test.
        pass

    def __getattr__(self, name):
        # Chuyển tiếp các lệnh khác (cursor, close...) sang kết nối thật
        return getattr(self.real_connection, name)

@pytest.fixture(scope="function")
def db_conn():
    real_conn = db_connection()
    if real_conn is None:
        pytest.fail("Lỗi kết nối DB")

    # Bọc kết nối thật
    mock_conn = MockConnection(real_conn)
    
    yield mock_conn
    
    # TEARDOWN: Sau khi test xong, ta dùng kết nối THẬT để rollback 
    # nhằm dọn dẹp sạch sẽ dữ liệu rác.
    real_conn.rollback()
    real_conn.close()