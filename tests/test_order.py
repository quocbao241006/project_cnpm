import pytest
from OrderRepository import OrderRepository
from UserRepository import UserRepository
from ProductRepository import ProductRepository

# Hàm hỗ trợ tạo dữ liệu giả (Helper)
def create_dummy_data(db_conn):
    user_repo = UserRepository(db_conn)
    prod_repo = ProductRepository(db_conn)
    
    # 1. Tạo User giả
    email = "buyer_test@example.com"
    user_repo.create_user("Buyer", "1234", email, "0909", "VN", 20, "001")
    user_data = user_repo.authenticate_user(email, "1234")
    user_id = user_data['userID']
    
    # 2. Tạo Sản phẩm giả (Tồn kho = 10)
    prod_id = prod_repo.add_new_product("Test Product", 1, "T1", "Desc", 100000, 10, "img.jpg")
    
    return user_id, prod_id

def test_place_order_success(db_conn):
    """
    Kịch bản: Mua 2 sản phẩm.
    Mong đợi: Đặt hàng thành công, Tồn kho giảm từ 10 xuống 8.
    """
    order_repo = OrderRepository(db_conn)
    prod_repo = ProductRepository(db_conn)
    
    # 1. Chuẩn bị dữ liệu
    user_id, prod_id = create_dummy_data(db_conn)
    
    cart_items = [{
        'productID': prod_id,
        'quantity': 2,          # Mua 2 cái
        'unitprice': 100000,
        'cartdetailID': 999     # ID giả, không quan trọng ở hàm này
    }]
    
    ship_info = {
        'recipient_name': 'Bao',
        'recipient_phone': '0909',
        'address': 'HCM City'
    }
    
    # 2. Thực hiện hành động: Đặt hàng
    order_id = order_repo.place_order(user_id, cart_items, ship_info, "COD")
    
    # 3. Kiểm tra kết quả (Assert)
    assert order_id is not None, "Phải trả về Order ID"
    
    # Kiểm tra tồn kho: Ban đầu 10, mua 2 -> Phải còn 8
    current_prod = prod_repo.get_product_by_id(prod_id)
    assert current_prod['stock_quantity'] == 8, "Kho phải giảm đúng số lượng đã mua"

def test_place_order_out_of_stock(db_conn):
    """
    Kịch bản: Tồn kho có 10, cố tình mua 100.
    Mong đợi: Đặt hàng thất bại (None), Tồn kho vẫn y nguyên là 10.
    """
    order_repo = OrderRepository(db_conn)
    prod_repo = ProductRepository(db_conn)
    
    user_id, prod_id = create_dummy_data(db_conn)
    
    # Cố tình mua quá số lượng (Mua 100 trong khi kho chỉ có 10)
    cart_items = [{
        'productID': prod_id,
        'quantity': 100,      
        'unitprice': 100000
    }]
    
    ship_info = {'recipient_name': 'Bao', 'recipient_phone': '0909', 'address': 'HCM'}
    
    # Hành động
    order_id = order_repo.place_order(user_id, cart_items, ship_info, "COD")
    
    # Assert
    assert order_id is None, "Phải trả về None khi hết hàng"
    
    # Kiểm tra kho: Phải giữ nguyên là 10, không được bị trừ âm
    current_prod = prod_repo.get_product_by_id(prod_id)
    assert current_prod['stock_quantity'] == 10

def test_cancel_order(db_conn):
    """Test chức năng hủy đơn hàng và hoàn lại kho"""
    order_repo = OrderRepository(db_conn)
    prod_repo = ProductRepository(db_conn)
    
    # 1. Tạo đơn hàng trước
    user_id, prod_id = create_dummy_data(db_conn)
    cart_items = [{'productID': prod_id, 'quantity': 2, 'unitprice': 100000}] # Mua 2
    ship_info = {'recipient_name': 'Bao', 'recipient_phone': '0909', 'address': 'HCM'}
    
    order_id = order_repo.place_order(user_id, cart_items, ship_info, "COD")
    
    # Lúc này kho còn 8 (10 - 2)
    assert prod_repo.get_product_by_id(prod_id)['stock_quantity'] == 8
    
    # 2. Hủy đơn hàng
    success = order_repo.cancel_order(order_id, user_id)
    assert success is True
    
    # 3. Kiểm tra kho: Phải được cộng lại 2 -> Về lại 10
    assert prod_repo.get_product_by_id(prod_id)['stock_quantity'] == 10
    
    # 4. Kiểm tra trạng thái đơn hàng
    orders = order_repo.get_member_orders(user_id)
    # Lấy đơn hàng mới nhất
    my_order = next((o for o in orders if o['orderID'] == order_id), None)
    assert my_order['status'] == 'Cancelled'

def test_admin_update_order_status(db_conn):
    order_repo = OrderRepository(db_conn)
    # Helper tạo đơn hàng (bạn copy hàm create_dummy_data từ bài trước)
    user_id, prod_id = create_dummy_data(db_conn)
    
    # Tạo đơn hàng
    cart = [{'productID': prod_id, 'quantity': 1, 'unitprice': 100}]
    ship = {'recipient_name': 'Test', 'recipient_phone': '123', 'address': 'Addr'}
    oid = order_repo.place_order(user_id, cart, ship, "COD")
    
    # Mặc định là 'New Order'
    order_details = order_repo.get_order_details_items(oid)
    assert order_details[0]['orderStatus'] == 'New Order'
    
    # Admin chuyển trạng thái sang 'Shipped'
    success = order_repo.update_orders_status(oid, "Shipped")
    assert success is True
    
    # Kiểm tra lại
    updated_details = order_repo.get_order_details_items(oid)
    assert updated_details[0]['orderStatus'] == 'Shipped'