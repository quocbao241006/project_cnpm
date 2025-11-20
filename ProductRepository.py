import psycopg2
class ProductRepository:
    def __init__(self, _connection):
        self.connection = _connection
        self.cursor = self.connection.cursor()
        print("ProductRepository đã được khởi tạo")
        pass
    #=======================================================================================
    def get_all_product(self):
        try:
            sql = '''SELECT productID, productName, description, price, product_code, number_of_sale, images, stock_quantity  FROM "product" ORDER BY productID ASC'''
            self.cursor.execute(sql)
            list_product = self.cursor.fetchall()
            product = []            
            for row in list_product:
                product_dict = {}
                product_dict['productID'] = row[0]
                product_dict['productName'] = row[1]
                product_dict['description'] = row[2]
                product_dict['price'] = row[3]
                product_dict['number_of_sale'] = row[4]
                product_dict['images'] = row[5]
                product_dict['stock_quantity'] = row[6]
                product.append(product_dict)
            return product
        except Exception as e:
            print(f"lôi khi lấy danh sách: {e}")
            return []
    #===============================================================================================================
    def get_product_by_id(self, _productID):
        try:
            # Chỉ SELECT từ bảng product. Đủ 100% thông tin bạn cần.
            sql = '''SELECT productID, productName, description, product_code, 
                            price, stock_quantity, number_of_sale, images, categoryID
                     FROM "product" 
                     WHERE productID = %s
                     ORDER BY productID'''
            
            self.cursor.execute(sql, (_productID,))
            result = self.cursor.fetchone()
            
            if result:
                return {
                    'productID': result[0],
                    'productName': result[1],
                    'description': result[2],
                    'product_code': result[3],
                    'price': result[4],
                    'stock_quantity': result[5],
                    'number_of_sale': result[6],
                    'images': result[7],
                    'categoryID': result[8] 
                }
            return None # Không tìm thấy

        except Exception as e:
            print(f"Lỗi lấy sản phẩm ID {_productID}: {e}")
            return None
    #===============================================================================================================
    def get_product_by_categoryID(self, _categoryID):
        try:
            sql = '''SELECT productID, productName, description, product_code, price, stock_quantity, images
                        from "product" 
                        where categoryID = %s
                        order by productID'''
            self.cursor.execute(sql,(_categoryID,))
            result = self.cursor.fetchall()
            products_list = [] 
            
            for item in result:
                products_list.append({
                    'productID': item[0],
                    'productName': item[1],
                    'description': item[2],
                    'product_code': item[3],
                    'price': item[4],
                    'stock_quantity': item[5],
                    'images': item[6]
                })
            return products_list
        except Exception as e:
            print(f'loi: {e}')
            return []
    #===============================================================================================================
    def delete_product(self, _productID):
        try:
            sql_check = 'SELECT COUNT(*) FROM "orderdetail" WHERE productID = %s'
            self.cursor.execute(sql_check, (_productID,))
            count = self.cursor.fetchone()[0]
            
            if count > 0:
                raise Exception(f"Không thể xóa: Sản phẩm này đang nằm trong {count} đơn hàng lịch sử.")

            sql_delete = 'DELETE FROM "product" WHERE productID = %s'
            self.cursor.execute(sql_delete, (_productID,))
            if self.cursor.rowcount == 0:
                raise Exception(f"Không tìm thấy sản phẩm ID {_productID} để xóa.")

            self.connection.commit()
            print(f"✅ Đã xóa thành công sản phẩm ID {_productID}")
            return True

        except Exception as e:
            self.connection.rollback()
            print(f"❌ Lỗi xóa sản phẩm: {e}")
            return False       
    #===============================================================================================================
    def search_product(self, keyword):
        try:
            search_pattern = f"%{keyword}%"
            sql = '''select productID, productName, description, price, number_of_sale, images, stock_quantity  FROM "product" where productName ILIKE %s or description ILIKE %s'''
            self.cursor.execute(sql, (search_pattern, search_pattern))
            result = self.cursor.fetchall()
            product = []
            for item in result:
                product_item = {}
                product_item['productID'] = item[0]
                product_item['productName'] = item[1]
                product_item['description'] = item[2]
                product_item['price'] = item[3]
                product_item['number_of_sale'] = item[4]
                product_item['images'] = item[5]
                product_item['stock_quantity'] = item[6]
                product.append(product_item)
            return product
        except Exception as e:
            print(f"Lỗi search đơn hàng: {e}")
            return []
    #===================================================================================================================
    def add_new_product(self,_productName, _categoryID, _productCode, _description, _price, _stock_quantity, _images):
        try:
            if _price <= 0 or _stock_quantity < 0:
                raise ValueError("Giá hoặc số lượng tồn kho không hợp lệ.")
            sql = '''insert into "product"(productName, categoryid, product_code, description, price, stock_quantity, images) values
                    (%s,%s,%s,%s,%s,%s,%s)
                    returning productID'''
            self.cursor.execute(sql, (_productName,_categoryID,_productCode,_description,_price, _stock_quantity,_images))
            new_product_id = self.cursor.fetchone()[0]
            self.connection.commit()
            print(f"thêm thành công sản phẩm: {new_product_id}")
            return new_product_id
        except Exception as e:
            print(f"loi insert table product: {e}")
            self.connection.rollback()
            return None
    #=============================================================================================================================
    def update_product(self, _productID, _newName, _newCategoryID, _newProductCode, _newDesc,_newPrice, _newStock, _newImages):
        try:
            if _newPrice <= 0: # Giá phải lớn hơn 0
                raise ValueError("Giá sản phẩm phải là số dương (> 0).") 
            if _newStock < 0: # Tồn kho không được âm
                 raise ValueError("Số lượng tồn kho không được âm.")
            sql = '''update "product"
                        set productName = %s,
                            categoryID = %s,
                            product_code = %s,
                            description = %s,
                            price = %s,
                            stock_quantity = %s,
                            images = %s
                        where productID = %s'''
            self.cursor.execute(sql, (_newName, _newCategoryID, _newProductCode, _newDesc, _newPrice, _newStock, _newImages,_productID))
            if self.cursor.rowcount == 0:
                raise Exception(f"Không tìm thấy sản phẩm có ID: {_productID} để cập nhật.")
            self.connection.commit()
            return True
        except Exception as e:
            print(f"loi khong update duoc : {e}")
            self.connection.rollback()
            return False
    # category
    # =====================================================
    def add_new_category(self, _categoryName):
        try:
            sql = '''insert into "category"(categoryName) 
                    values(%s)
                    returning categoryID'''
            self.cursor.execute(sql, (_categoryName,))
            categoryID = self.cursor.fetchone()[0]
            self.connection.commit()
            return categoryID
        except Exception as e:
            print(f"loi: {e}")
            self.connection.rollback()
            return None
    #=====================================================
    def update_category(self, _categoryID,_newName):
        try:
            sql = '''update "category"
                    set categoryName = %s
                    where categoryID = %s'''
            self.cursor.execute(sql, (_newName,_categoryID))
            self.connection.commit()
        except Exception as e:
            print(f"loi khong the cap nhap category : {e}")
            self.connection.rollback()
    #=====================================================
    def get_all_categories(self):
        try:
            sql = '''select categoryID, categoryName
                    From "category"'''
            self.cursor.execute(sql,())
            result = self.cursor.fetchall()
            category = []
            for item in result:
                category_list = {}
                category_list['categoryID'] =  item[0]
                category_list['categoryName'] = item[1]
                category.append(category_list)
            return category
        except Exception as e:
            print(f"khong the lay danh muc : {e}")
            return []
    #=====================================================
    def delete_category(self,_categoryID):
        try:
            # kiểm tra
            sql_count = 'SELECT COUNT(*) FROM "product" WHERE categoryID = %s'
            self.cursor.execute(sql_count, (_categoryID,))
            count_result = self.cursor.fetchone()
            product_count = count_result[0]
            if product_count > 0:
                raise Exception(f"Không thể xóa danh mục. Vẫn còn {product_count} sản phẩm thuộc danh mục này.")
            elif product_count == 0:
                sql = '''DELETE FROM "category" where categoryID = %s'''
                self.cursor.execute(sql, (_categoryID,))
                print(f"xóa thành công category {_categoryID} ")
            self.connection.commit()
        except Exception as e:
            print(f"lỗi không thể xóa: {e}")    
            self.connection.rollback()
    #================================================================
