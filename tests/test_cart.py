import pytest
from CartRepository import CartRepository
from UserRepository import UserRepository
from ProductRepository import ProductRepository

# Hàm tạo dữ liệu giả (Dùng chung logic)
def setup_user_and_product(db_conn):
    user_repo = UserRepository(db_conn)
    prod_repo = ProductRepository(db_conn)
    
    # Tạo User
    user_repo.create_user("CartUser", "123", "cart@test.com", "000", "VN", 20, "111")
    user = user_repo.authenticate_user("cart@test.com", "123")
    
    # Tạo Product
    prod_id = prod_repo.add_new_product("CartProd", 1, "CP1", "Desc", 50000, 100, "img")
    
    return user['userID'], prod_id

def test_add_to_cart_new(db_conn):
    """Test thêm sản phẩm mới vào giỏ"""
    cart_repo = CartRepository(db_conn)
    user_id, prod_id = setup_user_and_product(db_conn)
    
    # Thêm 2 sản phẩm
    cart_repo.add_to_cart(user_id, prod_id, 2, 50000)
    
    # Kiểm tra
    items = cart_repo.get_cart_detail(user_id)
    assert len(items) == 1
    assert items[0]['productID'] == prod_id
    assert items[0]['quantity'] == 2

def test_add_to_cart_accumulate(db_conn):
    """Test thêm sản phẩm đã có -> Phải cộng dồn số lượng"""
    cart_repo = CartRepository(db_conn)
    user_id, prod_id = setup_user_and_product(db_conn)
    
    # Lần 1: Thêm 2
    cart_repo.add_to_cart(user_id, prod_id, 2, 50000)
    
    # Lần 2: Thêm tiếp 3
    cart_repo.add_to_cart(user_id, prod_id, 3, 50000)
    
    # Kiểm tra: Tổng phải là 5
    items = cart_repo.get_cart_detail(user_id)
    assert items[0]['quantity'] == 5

def test_update_cart_quantity_to_zero(db_conn):
    """Test cập nhật số lượng về 0 -> Tự động xóa"""
    cart_repo = CartRepository(db_conn)
    user_id, prod_id = setup_user_and_product(db_conn)
    
    cart_repo.add_to_cart(user_id, prod_id, 5, 50000)
    items = cart_repo.get_cart_detail(user_id)
    cart_detail_id = items[0]['cartdetailID']
    
    # Update về 0
    cart_repo.update_cart_quantity(cart_detail_id, 0)
    
    # Kiểm tra: Giỏ hàng phải trống
    new_items = cart_repo.get_cart_detail(user_id)
    assert len(new_items) == 0