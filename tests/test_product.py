import pytest
from ProductRepository import ProductRepository

def test_add_and_search_product(db_conn):
    repo = ProductRepository(db_conn)
    
    # 1. Thêm sản phẩm
    name = "Laptop Pytest Gaming"
    cat_id = 2 # Giả sử ID 2 là Laptop (đảm bảo trong project.sql đã insert)
    code = "PYTEST-001"
    desc = "Test auto"
    price = 50000000
    stock = 10
    img = "test.jpg"
    
    new_id = repo.add_new_product(name, cat_id, code, desc, price, stock, img)
    assert new_id is not None
    
    # 2. Tìm kiếm sản phẩm vừa thêm
    results = repo.search_product("Pytest")
    
    # Kiểm tra kết quả
    assert len(results) >= 1
    found_product = next((p for p in results if p['productID'] == new_id), None)
    assert found_product is not None
    assert found_product['price'] == price

def test_add_product_invalid_price(db_conn):
    """Test validation giá âm"""
    repo = ProductRepository(db_conn)
    
    # Trong code ProductRepository.py của bạn, bạn dùng try-except và in lỗi, trả về None
    new_id = repo.add_new_product("Fail Product", 1, "F1", "Desc", -1000, 10, "img")
    
    assert new_id is None
def test_category_crud(db_conn):
    """Test trọn bộ vòng đời danh mục: Tạo -> Sửa -> Xóa"""
    repo = ProductRepository(db_conn)
    
    # 1. Tạo danh mục mới
    cat_id = repo.add_new_category("Test Category")
    assert cat_id is not None
    
    # Kiểm tra xem đã có trong list chưa
    cats = repo.get_all_categories()
    assert any(c['categoryID'] == cat_id for c in cats)
    
    # 2. Sửa tên danh mục
    repo.update_category(cat_id, "Updated Name")
    cats_after = repo.get_all_categories()
    updated_cat = next(c for c in cats_after if c['categoryID'] == cat_id)
    assert updated_cat['categoryName'] == "Updated Name"
    
    # 3. Xóa danh mục
    repo.delete_category(cat_id)
    cats_final = repo.get_all_categories()
    assert not any(c['categoryID'] == cat_id for c in cats_final)

def test_update_and_delete_product(db_conn):
    repo = ProductRepository(db_conn)
    
    # 1. Tạo sản phẩm giả
    pid = repo.add_new_product("Old Name", 1, "CODE1", "Desc", 10000, 10, "img")
    
    # 2. Test Update: Đổi tên và tăng giá
    # update_product(id, newName, catID, code, desc, price, stock, img)
    success = repo.update_product(pid, "New Name", 1, "CODE1", "Desc", 20000, 50, "img")
    assert success is True
    
    # Verify lại dữ liệu
    p = repo.get_product_by_id(pid)
    assert p['productName'] == "New Name"
    assert p['price'] == 20000
    assert p['stock_quantity'] == 50
    
    # 3. Test Delete
    del_success = repo.delete_product(pid)
    assert del_success is True
    
    # Verify đã mất
    assert repo.get_product_by_id(pid) is None