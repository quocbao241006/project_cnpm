import psycopg2

class OrderRepository:
    
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor() 
        print("OrderRepository đã được khởi tạo")

    def place_order(self, user_id, cart_items, shipping_info, payment_method):  
        try:
            # 1. Tính toán tiền
            shipping_fee = 30000
            total_product_amount = sum(item['quantity'] * item['unitprice'] for item in cart_items)
            final_total = int(total_product_amount + shipping_fee)
            
            status = 'Awaiting Payment' if payment_method == 'Online' else 'New Order'
            
            # 2. Tạo Order
            sql_order = '''INSERT INTO "Order" (userID, totalAmount, status) 
                           VALUES (%s, %s, %s) RETURNING orderID'''
            
            self.cursor.execute(sql_order, (user_id, final_total, status))
            new_order_id = self.cursor.fetchone()[0]

            # 3. Tạo Order Detail & Trừ kho
            for item in cart_items:
                # Check kho
                sql_check_stock = '''SELECT stock_quantity FROM product 
                                     WHERE productID = %s FOR UPDATE'''
                self.cursor.execute(sql_check_stock, (item['productID'],))
                stock_data = self.cursor.fetchone()
                
                if stock_data is None:
                    raise Exception(f"Không tìm thấy sản phẩm ID {item['productID']}")
                
                current_stock = stock_data[0]
                if current_stock < item['quantity']:
                    raise Exception(f"Hết hàng SP {item['productID']}. Còn {current_stock}, cần {item['quantity']}")
                
                # Update kho
                sql_update_stock = '''UPDATE product SET stock_quantity = stock_quantity - %s 
                                      WHERE productID = %s'''
                self.cursor.execute(sql_update_stock, (item['quantity'], item['productID']))
                
                sql_order_detail = '''INSERT INTO orderdetail (orderID, productID, quantity, unitPrice) 
                                      VALUES (%s, %s, %s, %s)'''
                self.cursor.execute(sql_order_detail, (new_order_id, item['productID'], item['quantity'], int(item['unitprice'])))

            # 4. Tạo thông tin Ship
            sql_ship = '''INSERT INTO ship (orderID, shipAddress, recipient_name, recipient_phone, shipFee) 
                          VALUES (%s, %s, %s, %s, %s)'''
            self.cursor.execute(sql_ship, (
                new_order_id, 
                shipping_info['address'], 
                shipping_info['recipient_name'], 
                shipping_info['recipient_phone'], 
                int(shipping_fee)
            ))
            
            # 5. Tạo thông tin Payment
            payment_status = 'Pending' if payment_method == 'Online' else 'Success'
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
                     LEFT JOIN "User" AS u ON o.userID = u.userID
                     LEFT JOIN ship AS s ON o.orderID = s.orderID
                     LEFT JOIN payment AS p ON o.orderID = p.orderID
                     WHERE o.userID = %s
                     ORDER BY o.orderDate DESC;''' 
            
            self.cursor.execute(sql, (userID,))
            orders_data = self.cursor.fetchall()
            orders_list = []
            for item in orders_data:
                orders_list.append({
                    'orderID': item[0],
                    'orderDate': item[1],
                    'totalAmount': item[2],
                    'status': item[3],
                    'shipAddress': item[4] if item[4] else "N/A",
                    'paymentMethod': item[5] if item[5] else "N/A"
                })
            return orders_list
        except Exception as e:
            print(f"Lỗi lấy lịch sử: {e}")
            return []

    def cancel_order(self, orderID, userID):
        try:
            sql_select = '''
                SELECT o.status, o.userID, od.productID, od.quantity 
                FROM "Order" AS o
                JOIN orderdetail AS od ON o.orderID = od.orderID
                WHERE o.orderID = %s;
            '''
            self.cursor.execute(sql_select, (orderID,))
            order_details = self.cursor.fetchall()
            
            if not order_details:
                raise Exception(f"Không tìm thấy đơn hàng ID {orderID}.")

            order_status = order_details[0][0] 
            owner_userID = order_details[0][1] 
            
            if owner_userID != userID:
                raise Exception("Bạn không sở hữu đơn hàng này.")
            if order_status not in ['New Order', 'Awaiting Payment']:
                raise Exception(f"Đơn hàng trạng thái '{order_status}' không thể hủy.")

            # Cập nhật trạng thái
            self.cursor.execute('UPDATE "Order" SET status = %s WHERE orderID = %s', ('Cancelled', orderID))
            
            # Hoàn tồn kho
            for item in order_details:
                product_id = item[2]
                qty = item[3]
                self.cursor.execute('UPDATE product SET stock_quantity = stock_quantity + %s WHERE productID = %s', (qty, product_id))

            self.connection.commit()
            print(f"Đã hủy đơn hàng {orderID}.")
            return True
            
        except Exception as e:
            self.connection.rollback()
            print(f"Lỗi hủy đơn: {e}")
            return False