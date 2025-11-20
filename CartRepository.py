import psycopg2
class CartRepository:
    def __init__(self, _connection):
        self.connection = _connection
        self.cursor = self.connection.cursor()
        print("CartRepository đã khởi động")
        pass
    def add_to_cart(self,_userID, _productID, _quantity, _unitprice):
        try:
            sql = '''select cartID from "cart" where userID = %s'''
            self.cursor.execute(sql, (_userID,))
            result = self.cursor.fetchone()
            if result is None:
                print("chưa có giỏ hàng, tiến hành tạo mới")
                sql_create_cart ='''insert into "cart"(userID) values (%s) RETURNING cartID'''
                self.cursor.execute(sql_create_cart, (_userID,))
                cartID = self.cursor.fetchone()[0]
                print(f"đã tạo cart mới {cartID}")
            else:
                cartID = result[0]
                print(f"đã tìm thấy giỏ hàng của {_userID}: ID giỏ hàng là {cartID}")
            sql_product = '''select cartdetailID from "cartdetail" where cartID = %s and productID = %s'''
            self.cursor.execute(sql_product, (cartID, _productID))
            product = self.cursor.fetchone()
            if product is None:
                sql_insert = '''Insert into "cartdetail"(cartID, productID, quantity, unitprice) values
                                (%s, %s, %s, %s)'''
                self.cursor.execute(sql_insert, (cartID, _productID, _quantity, _unitprice))
                print("Da them thanh cong")
            else:
                sql_update = '''update "cartdetail" set quantity = quantity + %s where productID = %s and cartID = %s'''
                self.cursor.execute(sql_update, (_quantity, _productID, cartID))
                print("Da cong don thanh cong")
            self.connection.commit()
        except Exception as e:
            print(f"khong the the don hang, loi : {e}")
            self.connection.rollback()
    def get_cart_detail(self, _userID):
        try:
            sql = '''select p.productName, p.images, cd.quantity, cd.unitprice, cd.cartdetailID
                        from "cartdetail" as cd join "cart" as c on cd.cartID = c.cartID
                                join "product" as p on cd.productID = p.productID
                        where c.userID = %s'''
            self.cursor.execute(sql, (_userID,))
            result = self.cursor.fetchall()
            cart_detail = []
            for item in result:
                cart_dict = {}
                cart_dict['productName'] = item[0]
                cart_dict['images'] = item[1]
                cart_dict['quantity'] = item[2]
                cart_dict['unitprice'] = item[3]
                cart_dict['cartdetailID'] = item[4]
                cart_detail.append(cart_dict)
            print(f"da tra ve gio hang cua nguoi dung {_userID}")
            return cart_detail
            
        except Exception as e:
            print(f"loi : {e}")
            return []
    def update_cart_quantity(self,_cartDetailID, _quantity):
        try:
            if _quantity > 0:
                sql = '''update "cartdetail" 
                        set quantity = %s
                        where cartdetailID = %s'''
                self.cursor.execute(sql, (_quantity, _cartDetailID))
                print("cập nhập thành công")
            else:
                sql_delete = '''delete from "cartdetail"
                                where cartdetailID = %s'''
                self.cursor.execute(sql_delete, (_cartDetailID,))
                print("đã xóa vì số lượng  = 0")
            self.connection.commit()
        except Exception as e:
            print(f"loi cap nhap: {e}")
            self.connection.rollback()
    def remove_from_cart(self,_cartdetailID):
        try:
            sql = '''delete from "cartdetail" 
                        where cartdetailID = %s'''
            self.cursor.execute(sql, (_cartdetailID,))
            self.connection.commit()
        except Exception as e:
            print(f"Loi : {e} , khong xoa duoc item")
            self.connection.rollback()