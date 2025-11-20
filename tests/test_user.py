import pytest
from UserRepository import UserRepository

def test_create_user_success(db_conn):
    """Test tạo user mới thành công"""
    repo = UserRepository(db_conn)
    
    # Dữ liệu giả lập
    username = "TestUser_Pytest"
    password = "password123"
    email = "test_pytest@example.com"
    phone = "0909000111"
    addr = "HCM"
    age = 20
    cccd = "001122334455"

    # Thực hiện hành động
    result = repo.create_user(username, password, email, phone, addr, age, cccd)
    
    # Kiểm tra kết quả (Assert)
    assert result is True, "Đăng ký phải trả về True"

    # Kiểm tra xem user đã thực sự vào DB chưa (trong transaction này)
    cursor = db_conn.cursor()
    cursor.execute("SELECT username FROM \"User\" WHERE email = %s", (email,))
    db_user = cursor.fetchone()
    assert db_user is not None
    assert db_user[0] == username

def test_authenticate_success(db_conn):
    """Test đăng nhập đúng mật khẩu"""
    repo = UserRepository(db_conn)
    
    # Tạo user trước
    email = "login_test@example.com"
    password = "mypassword"
    repo.create_user("LoginUser", password, email, "0123456789", "Addr", 22, "123123123123")

    # Thử đăng nhập
    user_session = repo.authenticate_user(email, password)
    
    assert user_session is not None
    assert user_session['username'] == "LoginUser"
    assert user_session['user_role'] == "Member"

def test_authenticate_fail(db_conn):
    """Test đăng nhập sai mật khẩu"""
    repo = UserRepository(db_conn)
    
    email = "fail_login@example.com"
    repo.create_user("FailUser", "realpassword", email, "0123456789", "Addr", 22, "123123123123")

    # Nhập sai pass
    user_session = repo.authenticate_user(email, "wrongpassword")
    
    assert user_session is None

def test_update_profile(db_conn):
    repo = UserRepository(db_conn)
    # Tạo user
    email = "profile_test@gmail.com"
    repo.create_user("OldName", "123", email, "000", "Addr", 20, "111")
    user = repo.authenticate_user(email, "123")
    uid = user['userID']
    
    # User đổi tên và SĐT
    # update_user_profile(uid, username, phone, address, age, new_pass, cccd)
    repo.update_user_profile(uid, "NewName", "999", "Addr", 20, None, "111")
    
    # Kiểm tra
    info = repo.get_user_by_id(uid)
    assert info['username'] == "NewName"
    assert info['phonenumber'] == "999"