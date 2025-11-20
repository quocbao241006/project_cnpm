import pytest
from UserRepository import UserRepository

def test_admin_lock_user(db_conn):
    """Test Admin khóa (xóa) tài khoản người dùng"""
    repo = UserRepository(db_conn)
    
    # 1. Tạo một user thường
    email = "bad_user@example.com"
    repo.create_user("BadUser", "123", email, "000", "VN", 20, "111")
    user_data = repo.authenticate_user(email, "123")
    target_id = user_data['userID']
    
    # Đảm bảo user đang tồn tại
    assert repo.get_user_by_id(target_id) is not None
    
    # 2. Admin thực hiện khóa (Xóa)
    success = repo.admin_delete_user(target_id)
    assert success is True
    
    # 3. Kiểm tra: User không còn đăng nhập được hoặc không tìm thấy
    deleted_user = repo.get_user_by_id(target_id)
    assert deleted_user is None

def test_admin_promote_role(db_conn):
    """Test nâng quyền Member lên Admin"""
    repo = UserRepository(db_conn)
    
    # 1. Tạo Member
    email = "mod@example.com"
    repo.create_user("ModUser", "123", email, "000", "VN", 25, "222")
    user_data = repo.authenticate_user(email, "123")
    target_id = user_data['userID']
    
    assert user_data['user_role'] == 'Member'
    
    # 2. Admin nâng quyền (Update role)
    # admin_update_user_status(userID, username, role, phone, address, age, cccd)
    repo.admin_update_user_status(target_id, "ModUser", "Admin", "000", "VN", 25, "222")
    
    # 3. Kiểm tra lại trong DB
    updated_user = repo.authenticate_user(email, "123")
    assert updated_user['user_role'] == 'Admin'