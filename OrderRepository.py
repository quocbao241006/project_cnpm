import psycopg2

class OrderRepository:
    
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor() 
        print("OrderRepository đã được khởi tạo")

    def place_order(self, user_id, cart_items, shipping_info, payment_method):
        try:
        # ... (Phần tính toán giữ nguyên)
            shipping_fee = 30000
            total_product_amount = sum(item['quantity'] * item['unitprice'] for item in cart_items)
            final_total = int(total_product_amount + shipping_fee)
        
            status = 'Awaiting Payment' if payment_method == 'Online' else 'New Order'
        
        # 2. Tạo Order (Tên bảng chuyển thành "order" để nhất quán)
            sql_order = '''INSERT INTO "order" (userID, totalAmount, status) 
                       VALUES (%s, %s, %s) RETURNING orderID''' 
        
            self.cursor.execute(sql_order, (user_id, final_total, status))
            new_order_id = self.cursor.fetchone()[0]

        # 3. Tạo Order Detail & Trừ kho (Tên bảng product, orderdetail đã đúng)
            for item in cart_items:
            # ... (Logic kiểm tra và trừ kho giữ nguyên)
                sql_check_stock = '''SELECT stock_quantity FROM product WHERE productID = %s FOR UPDATE'''
                self.cursor.execute(sql_check_stock, (item['productID'],))
                stock_data = self.cursor.fetchone()
            # ... (Xử lý lỗi)
                sql_update_stock = '''UPDATE product SET stock_quantity = stock_quantity - %s WHERE productID = %s'''
                self.cursor.execute(sql_update_stock, (item['quantity'], item['productID']))
            
                sql_order_detail = '''INSERT INTO orderdetail (orderID, productID, quantity, unitPrice) 
                                  VALUES (%s, %s, %s, %s)'''
                self.cursor.execute(sql_order_detail, (new_order_id, item['productID'], item['quantity'], int(item['unitprice'])))

        # 4. Tạo thông tin Ship (Tên bảng chuyển thành ship)
            sql_ship = '''INSERT INTO ship (orderID, shipAddress, recipient_name, recipient_phone, shipFee) 
                      VALUES (%s, %s, %s, %s, %s)'''
            self.cursor.execute(sql_ship, (
            new_order_id, 
            shipping_info['address'], 
            shipping_info['recipient_name'], 
            shipping_info['recipient_phone'], 
            int(shipping_fee)
            ))
        
        # 5. Tạo thông tin Payment (Đã sửa logic COD)
        # Nếu là COD, trạng thái ban đầu phải là 'Pending' hoặc 'Awaiting Confirmation'
            payment_status = 'Pending' if payment_method == 'Online' else 'Awaiting Receipt' 
            sql_payment = '''INSERT INTO payment (orderID, paymentMethod, amount, status) 
                          VALUES (%s, %s, %s, %s)'''
            self.cursor.execute(sql_payment, (
            new_order_id, 
            payment_method, 
            final_total, 
            payment_status
        ))
        
            self.connection.commit()
            print(f"Đặt hàng thành công! (ID: {new_order_id})")
            return new_order_id 

        except Exception as e:
            print(f"Lỗi khi đặt hàng, đang rollback: {e}")
            self.connection.rollback()
            return None
            
    def get_all_orders(self):
        try:
            sql = '''SELECT o.orderID,
                            o.orderDate,
                            o.totalAmount,
                            o.status,
                            u.username
                    FROM "Order" AS o
                    JOIN "User" AS u ON o.userID = u.userID
                    ORDER BY o.orderDate DESC'''
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            orders = []
            for item in result:
                orders.append({
                    'orderID': item[0],
                    'orderDate': item[1],
                    'totalAmount': item[2],
                    'status': item[3],
                    'userName': item[4]
                })
            return orders
        except Exception as e:
            print(f"Lỗi get_all_orders: {e}")
            return []
            
    def update_orders_status(self, orderID, newStatus):
        try:
            sql = '''UPDATE "order"
                    SET status = %s 
                    WHERE orderID = %s'''
            self.cursor.execute(sql, (newStatus, orderID))
            
            if self.cursor.rowcount == 0:
                print(f"Cảnh báo: Không tìm thấy đơn hàng ID {orderID}")
                return False
                
            self.connection.commit()
            print(f"Đã update status cho đơn hàng {orderID}")
            return True
        except Exception as e:
            print(f"Lỗi update_orders_status: {e}")
            self.connection.rollback()
            return False

    #==========================================================
    def get_member_orders(self, userID):
        try:
            sql = '''SELECT 
                        o.orderID,
                        o.orderDate,
                        o.totalAmount,
                        o.status,
                        s.shipAddress,
                        p.paymentMethod
                     FROM "Order" AS o
                     LEFT JOIN "user" AS u ON o.userID = u.userID
                     LEFT JOIN "ship" AS s ON o.orderID = s.orderID
                     LEFT JOIN "payment" AS p ON o.orderID = p.orderID
                     WHERE o.userID = %s
                     ORDER BY o.orderDate DESC''' 
            
            self.cursor.execute(sql, (userID,))
            orders_data = self.cursor.fetchall()
            orders_list = []
            for item in orders_data:
                orders_list.append({
                    'orderID': item[0],
                    'orderDate': item[1],
                    'totalAmount': item[2],
                    'status': item[3],
                    'shipAddress': item[4],
                    'paymentMethod': item[5]
                })
            return orders_list
        except Exception as e:
            print(f"Lỗi khi truy xuất lịch sử đơn hàng của userID {userID}: {e}")
            return []
            
    def get_order_details_items(self, orderID):
        try:
            sql = '''
                SELECT 
                    p.productName, 
                    p.images, 
                    od.quantity, 
                    od.unitPrice, 
                    o.status
                FROM "orderdetail" AS od
                JOIN "product" AS p ON od.productID = p.productID
                JOIN "Order" AS o ON od.orderID = o.orderID  
                WHERE od.orderID = %s
            '''
            self.cursor.execute(sql, (orderID,))
            result = self.cursor.fetchall()
            
            items = []
            for row in result:
                items.append({
                    'productName': row[0],
                    'images': row[1],
                    'quantity': row[2],
                    'unitPrice': row[3],
                    'orderStatus': row[4]  
                })
            return items
        except Exception as e:
            print(f"Lỗi lấy chi tiết sản phẩm cho đơn hàng {orderID}: {e}")
            return []
            
    #==========================================================================
    def cancel_order(self, orderID, userID):
        try:
            sql_select = '''
                SELECT 
                    o.status, 
                    o.userID, 
                    od.productID, 
                    od.quantity 
                FROM "Order" AS o
                JOIN "OrderDetail" AS od ON o.orderID = od.orderID
                WHERE o.orderID = %s
            '''
            self.cursor.execute(sql_select, (orderID,))
            order_details = self.cursor.fetchall()
            
            if not order_details:
                raise Exception(f"Lỗi: Không tìm thấy đơn hàng ID {orderID}.")

            order_status = order_details[0][0] 
            owner_userID = order_details[0][1] 
            
            if owner_userID != userID:
                raise Exception("Lỗi: Bạn không có quyền truy cập đơn hàng này.")
                
            if order_status not in ['New Order', 'Awaiting Payment']:
                raise Exception(f"Lỗi: Đơn hàng đang ở trạng thái '{order_status}'. Không thể hủy.")
            
            sql_update_status = '''UPDATE "Order" SET status = 'Cancelled' WHERE orderID = %s'''
            self.cursor.execute(sql_update_status, (orderID,))
            
            print(f"Đang hoàn nhập tồn kho cho đơn hàng ID {orderID}...")
            
            for item in order_details:
                product_id = item[2]
                quantity = item[3]
                sql_restock = '''UPDATE "product" 
                             SET stock_quantity = stock_quantity + %s 
                             WHERE productID = %s'''
                self.cursor.execute(sql_restock, (quantity, product_id))
                print(f"-> Hoàn nhập thành công {quantity} sản phẩm ID {product_id}.")

            self.connection.commit()
            print(f"✅ Hủy đơn hàng ID {orderID} thành công và đã hoàn nhập tồn kho.")
            return True
            
        except Exception as e:
            self.connection.rollback()
        # Thông báo lỗi cô đọng hơn
            print(f"❌ LỖI NGHIỆP VỤ: Không thể hủy đơn hàng. {e}") 
            return False