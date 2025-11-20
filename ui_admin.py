import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

#from ProductRepository import ProductRepository
from database import db_connection
from ProductRepository import ProductRepository
from OrderRepository import OrderRepository
from UserRepository import UserRepository

class Admin:
    def __init__(self, connection):
        self.conn = connection
        self.console = Console()
        self.productRepo = ProductRepository(self.conn)
        self.orderRepo = OrderRepository(self.conn)
        self.userRepo = UserRepository(self.conn)
    def mainView(self):
        while True:
            self.console.clear()
            self.console.print("[bright_blue]===== Quản trị hệ thống =====[/bright_blue]")
            self.console.print("\t[1] Quản lý sản phẩm và danh mục ")
            self.console.print("\t[2] Quản lý đơn hàng ")
            self.console.print("\t[3] Quản lý người dùng ")
            self.console.print("\t[0] Đăng xuất")
            choice = Prompt.ask("Chọn chức năng: ", choices=["1","2","3","0"])
            if choice == "1":
                self.manager_product_menu()
            elif choice == "2":
                self.manager_order()
            elif choice =="3":
                self.manager_user()
            elif choice == "0":
                self.console.print("[bright_yellow] Bạn đã đăng xuất!, tạm biệt [/bright_yellow]")
                break
    def manager_product_menu(self):
        while True:
            self.console.clear()
            self.console.print("[bright_blue] ======== Quản lý sản phẩm và danh mục ======== [/bright_blue]")
            self.display_category()
            try:
                categoryID = Prompt.ask("Chọn danh mục để quản lý sản phẩm hoặc [0] để quay lại:")
                if categoryID == "0":
                    break
                categoryID = int(categoryID)
                self.mangager_product(categoryID)
            except Exception as e:
                print(f'lỗi: {e}')
                Prompt.ask("Nhấn enter để tiếp tục")
    #===============================================================================================================
    def mangager_product(self, _categoryID):
        while True:
            self.console.clear()
            self.console.print(f"các sản phẩm thuộc danh mục: {_categoryID}")
            products = self.productRepo.get_product_by_categoryID(_categoryID)
            if not products:
                self.console.print("không có sản phẩm nào trong danh mục")
            table = Table()
            table.add_column("ID",justify="center")
            table.add_column("Name",justify="center")
            table.add_column("Description",justify="center")
            table.add_column("Product Code",justify="center")
            table.add_column("Price",justify="center")
            table.add_column("Stock",justify="center")
            table.add_column("Images",justify="center")
            for item in products:
                table.add_row(
                str(item['productID']),
                item['productName'],
                str(item['description']),
                str(item['product_code']),
                str(item['price']),
                str(item['stock_quantity']),
                str(item['images'])
            )
            self.console.print(table)
            self.console.print("\n[1] Thêm sản phẩm MỚI vào danh mục này  [2] Sửa sản phẩm CŨ  [3] Xóa sản phẩm  [0] Quay lại")
            action = Prompt.ask("Chọn tác vụ", choices=["1", "2", "3", "0"])
            
            if action == "0":
                break
            elif action == "1":
                self.ui_add_product(_categoryID) 
            elif action == "2":
                self.ui_update_product() 
            elif action == "3":
                self.ui_delete_product()
    #==================================================
    def ui_update_product(self):
        self.console.clear()
        self.console.print(Panel("[bold yellow]CẬP NHẬT SẢN PHẨM (EDIT)[/bold yellow]"))

        try:
            product_id = int(Prompt.ask("Nhập ID sản phẩm cần sửa"))
            
 
            old_data = self.productRepo.get_product_by_id(product_id)
            
            if old_data is None:
                self.console.print("LỖI: Không tìm thấy sản phẩm với ID này.[/red]")
                Prompt.ask("Nhấn Enter để quay lại")
                return

            self.console.print(f"\n[bold green]Đang sửa: {old_data['productName']} (ID: {product_id})[/bold green]")     
            new_name = Prompt.ask("Tên mới", default=old_data['productName'])
            new_category_id = int(Prompt.ask("Category ID mới", default=str(old_data['categoryID'])))

            new_code = Prompt.ask("Mã sản phẩm mới", default=old_data['product_code'])
            new_desc = Prompt.ask("Mô tả mới", default=old_data['description'])
            new_images = Prompt.ask("URL Ảnh mới", default=old_data['images'])
            
            new_price = int(Prompt.ask("Giá mới (> 0)", default=str(old_data['price'])))
            new_stock = int(Prompt.ask("Tồn kho mới (>= 0)", default=str(old_data['stock_quantity'])))
            
            success = self.productRepo.update_product(
                product_id, new_name, new_category_id, new_code, new_desc, 
                new_price, new_stock, new_images
            )

            if success:
                self.console.print(f"\n[bold green]✅ THÀNH CÔNG:[/bold green] Đã cập nhật sản phẩm ID {product_id}.")
            else:
                self.console.print(f"\n[bold red]❌ THẤT BẠI:[/bold red] Vui lòng kiểm tra log lỗi CSDL.")
                
        except Exception as e:
            self.console.print(f"\n[bold red]❌ LỖI HỆ THỐNG:[/bold red] {e}")
            
        Prompt.ask("Nhấn Enter để quay lại Menu Sản phẩm")
    #==================================================
    def ui_delete_product(self):
        self.console.print("Xóa sản phẩm")
        try:
            product_id = int(Prompt.ask("Nhập [cyan]ID[/cyan] sản phẩm cần XÓA"))
            old_data = self.productRepo.get_product_by_id(product_id)
            if old_data is None:
                self.console.print("[red]❌ LỖI: Không tìm thấy sản phẩm với ID này.[/red]")
                Prompt.ask("Nhấn Enter để quay lại")
                return
            confirmation = Confirm.ask(
                f"\n[bold yellow]CẢNH BÁO: Bạn có chắc chắn muốn xóa sản phẩm '{old_data['productName']}' (ID: {product_id})? Việc này không thể hoàn tác."
            )
            if not confirmation:
                self.console.print("[yellow]Hủy thao tác.[/yellow]")
                return
            success = self.productRepo.delete_product(product_id)
            if success:
                self.console.print(f"\n✅ THÀNH CÔNG: Đã xóa sản phẩm ID {product_id}.")
            else:
                self.console.print(f"\n❌ THẤT BẠI: Lỗi xóa sản phẩm. (Có thể do còn trong lịch sử đơn hàng).")
        except Exception as e:
            self.console.print(f"\n❌ LỖI HỆ THỐNG: Đã xảy ra lỗi: {e}")
            
        Prompt.ask("Nhấn Enter để quay lại Menu Sản phẩm")   
    #==================================================
    def display_category(self): # hàm bổ trợ của ui_add_product
        categories = self.productRepo.get_all_categories()
        if not categories:
            self.console.print("[bright_yellow]Chưa có danh mục nào. Vui lòng thêm danh mục vào DB")
            return None 
        table = Table(title="Danh sách danh mục")
        table.add_column("ID", justify="center")
        table.add_column("Tên danh mục", justify="center")
        for c in categories:
            table.add_row(str(c['categoryID']),str(c['categoryName']))
        self.console.print(table)
        return categories
    def ui_add_product(self, categoryID):
        self.console.clear()
        self.console.print(f"Thêm sản phẩm mới (cat :{categoryID})")
        try:
            productName = Prompt.ask("Nhập tên sản phẩm mới: ",default= "Sản phẩm mới")
            productCode = Prompt.ask("Nhập mã sản phẩm: ",default="SPM")
            description = Prompt.ask("Nhập mô tả sản phẩm: ",default="......")
            while True:
                try:
                    price = int(Prompt.ask("Nhập giá (VND): ", default="100000"))
                    stock_quantity = int(Prompt.ask("Nhập tồn kho: ", default="0"))
                    if price <= 0 or stock_quantity <= 0:
                        self.console.print("Lỗi dữ liệu, Vui lòng nhập số nguyên > 0")
                        continue
                    break
                except Exception as e:
                    self.console.print("Nhập số nguyên")
            images = Prompt.ask("Nhập URL ảnh: ",default="http://Link-to-defaul" )
            success_id = self.productRepo.add_new_product(productName, categoryID, productCode,description, price, stock_quantity,images)
            if success_id:
                self.console.print(f"Thêm thành công sản phẩm với ID: {success_id}")
            else:
                self.console.print(f"đã xảy ra lỗi")
        except Exception as e:
            self.console.print(f"Lỗi hệ thống: {e}")
        Prompt.ask("Nhấn enter để quay lại menu sản phẩm")
    def manager_order(self):
        while True:
            self.console.clear()
            self.console.print(Panel("[bold yellow]QUẢN LÝ ĐƠN HÀNG[/bold yellow]", border_style="yellow"))

            # BƯỚC 1: Lấy và hiển thị Danh sách Đơn hàng (UC-14)
            orders = self.orderRepo.get_all_orders()
            
            if not orders:
                self.console.print("[yellow]Chưa có đơn hàng nào trong hệ thống.[/yellow]")
                Prompt.ask("Nhấn Enter để quay lại")
                return

            table = Table(title="Danh sách Đơn hàng (Mới nhất)", show_header=True)
            table.add_column("ID", style="cyan", justify="right")
            table.add_column("Ngày đặt", style="white")
            table.add_column("Tổng tiền", style="green", justify="right")
            table.add_column("Trạng thái", style="magenta")
            table.add_column("Khách hàng", style="yellow")

            for o in orders:
                # Giả sử totalAmount là BIGINT, format không có thập phân
                
                table.add_row(
                    str(o['orderID']), 
                    str(o['orderDate'].strftime('%Y-%m-%d %H:%M')), # Định dạng datetime
                    str(o['totalAmount']), 
                    o['status'],
                    o['userName']
                )    
            self.console.print(table)
            self.console.print("\n[1] Xem Chi tiết & Cập nhật Trạng thái  [0] Quay lại")
            action = Prompt.ask("Chọn tác vụ", choices=["1", "0"])

            if action == "0":
                break
            elif action == "1":
                self.ui_view_and_update_order()
    def ui_view_and_update_order(self):
        try:
            orderID = int(Prompt.ask("Nhập ID đơn hàng cần xem chi tiết/ cập nhập: "))
            item = self.orderRepo.get_order_details_items(orderID)
            if not item:
                self.console.print("LỖI: không tìm thấy đơn hàng")
                Prompt.ask("Nhấn Enter để quay lại")
                return 
            self.console.print(f"Chi tiết đơn hàng ID: {orderID}")
            detail_order = Table()
            detail_order.add_column("Tên sản phẩm")
            detail_order.add_column("Ảnh")
            detail_order.add_column("Số lượng")
            detail_order.add_column("Đơn giá")
            for i in item:
                detail_order.add_row(
                    i['productName'],
                    str(i['images']),
                    str(i['quantity']),
                    str(i['unitPrice'])
                )
            self.console.print(detail_order)
            valid_statuses = ["Processing", "Shipped", "Cancelled", "New Order"]
            self.console.print(f"Trạng thái hiện tại: {item[0]['orderStatus'] if item else 'N/A'}")
            new_status = Prompt.ask(
                "Chọn Trạng thái mới", 
                choices=valid_statuses,
                default=valid_statuses[0]
            )
            success = self.orderRepo.update_orders_status(orderID, new_status)
            if success:
                self.console.print(f"✅ CẬP NHẬT THÀNH CÔNG: Trạng thái đơn hàng {orderID} đã chuyển sang '{new_status}'.")
            else:
                self.console.print(f"❌ THẤT BẠI: Lỗi cập nhật trạng thái đơn hàng.")
        except Exception as e:
            self.console.print(f"❌ LỖI HỆ THỐNG: {e}")
        Prompt.ask("Nhấn Enter để quay lại Menu Đơn hàng")
    #============================================================
    def manager_user(self):
        while True:
            self.console.clear()
            self.console.print(Panel("Quản lý người dùng"))
            users = self.userRepo.admin_get_all_users()
            if not users:
                self.console.print("Chưa có người dùng nào ngoài Admin")
                Prompt.ask("Nhấn Enter để quay lại")
                return
            table = Table()
            table.add_column("ID")
            table.add_column("User Name")
            table.add_column("Email")
            table.add_column("Phone")
            table.add_column("Role")
            table.add_column("Address")
            table.add_column("Age")
            table.add_column("MA")
            for user in users:
                table.add_row(
                    str(user['userID']),
                    user['username'],
                    user['email'],
                    str(user['phonenumber']),
                    str(user['user_role']),
                    str(user['address']),
                    str(user['age']),
                    str(user['cccd'])
                )
            self.console.print(table)
            self.console.print("\n[1] Sửa thông tin & Role  [2] Khóa tài khoản  [0] Quay lại")
            action = Prompt.ask("Chọn tác vụ", choices=["1", "2", "0"])
            if action == "0":
                break
            elif action == "1":
                self.ui_admin_edit_user() 
            elif action == "2":
                self.ui_admin_lock_user()
    def ui_admin_edit_user(self):
        self.console.print("Cập nhập thông tin người dùng")
        try:
            target_user_id = int(Prompt.ask("Nhập ID người dùng cần sửa: "))
            user_data = self.userRepo.get_user_by_id(target_user_id)
            if user_data is None:
                self.console.print("Lỗi không tìm thấy người dùng")
                Prompt.ask("Nhấn Enter để quay lại: ")
                return
            self.console.print(f"Đang sửa người dùng {user_data['username']}: ")
            new_username = Prompt.ask("Tên mới", default=user_data['username'])
            new_phone = Prompt.ask("SĐT mới", default=user_data['phonenumber'])
            new_address = Prompt.ask("Địa chỉ mới", default=user_data['address'])
            new_cccd = Prompt.ask("CCCD mới", default=user_data['cccd'])
            while True:
                try:
                    new_age = int(Prompt.ask("Tuổi mới", default=str(user_data['age'])))
                    break
                except ValueError:
                    self.console.print("[red]❌ LỖI DỮ LIỆU: Tuổi phải là số nguyên.[/red]")
            
            valid_roles = ["Admin", "Member"]
            new_role = Prompt.ask(
                "Chọn Role MỚI", 
                choices=valid_roles, 
                default=user_data['user_role']
            )
            success = self.userRepo.admin_update_user_status(
                target_user_id, new_username, new_role, new_phone, new_address, new_age, new_cccd
            )
            if success:
                self.console.print(f"\n✅ THÀNH CÔNG: Đã cập nhật thông tin User ID {target_user_id}.")
            else:
                self.console.print(f"\n❌ THẤT BẠI: Lỗi cập nhật User. Vui lòng kiểm tra log lỗi CSDL.")
        except Exception as e:
            self.console.print(f"\n❌ LỖI HỆ THỐNG: {e}")
            
        Prompt.ask("Nhấn Enter để quay lại Menu Quản lý Người dùng")
    def ui_admin_lock_user(self):
        self.console.print(Panel("KHÓA TÀI KHOẢN NGƯỜI DÙNG")) 
        try:
            target_user_id = int(Prompt.ask("Nhập ID người dùng cần KHÓA/VÔ HIỆU HÓA"))
            
            confirmation = Confirm.ask(
                f"\nCẢNH BÁO: Bạn có chắc chắn muốn KHÓA tài khoản ID {target_user_id} không? (Việc này chỉ có Admin mới có thể mở lại)."
            )
            if not confirmation:
                self.console.print("Hủy thao tác khóa.")
                return
            success = self.userRepo.admin_delete_user(target_user_id)
            if success:
                self.console.print(f"\n✅ THÀNH CÔNG: Đã KHÓA tài khoản User ID {target_user_id}.")
            else:
                self.console.print(f"\n❌ THẤT BẠI: Lỗi khóa tài khoản. ID có thể không tồn tại.")               
        except Exception as e:
            self.console.print(f"\n❌ LỖI HỆ THỐNG: {e}")
            
        Prompt.ask("Nhấn Enter để quay lại Menu Quản lý Người dùng")
if __name__ == "__main__":
    conn = db_connection()
    if conn:
        admin_app = Admin(conn)
        admin_app.mainView()
        conn.close()