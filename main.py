import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich import box
from rich.table import Table
import getpass
import re
import os
from PIL import Image

# Import Database
from database import db_connection

# Import Repositories
from UserRepository import UserRepository
from ProductRepository import ProductRepository
from CartRepository import CartRepository
from OrderRepository import OrderRepository

# Import UI Modules
import ui_admin
import ui_shop
import ui_bao

console = Console()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def is_valid_email(email):
    """
    Kiểm tra email có hợp lệ không
    """
    if "@" not in email or "." not in email:
        return False
    return True

def print_logo():
    logo = """
    ╔═════════════════════════════════════════════╗
    ║      MINI E-COMMERCE SYSTEM (GROUP 14)      ║
    ╚═════════════════════════════════════════════╝
    """
    console.print(f"[bold cyan]{logo}[/bold cyan]", justify="center")

# USER AUTHENTICATION UI
def handle_register(user_repo):
    clear()
    console.print(Panel("[bold green]ĐĂNG KÝ TÀI KHOẢN MỚI[/bold green]", box=box.ROUNDED))
    
    try:
        print("Vui lòng nhập thông tin:")
        username = Prompt.ask("Username")
        password = getpass.getpass("Password: ").strip()
        re_password = getpass.getpass("Confirm Password: ").strip()
        
        if password != re_password:
            console.print("[bold red]Mật khẩu không khớp![/bold red]")
            console.input("Enter để quay lại...")
            return
        while True:
            email = Prompt.ask("Email")
            if is_valid_email(email):
                break # Email đúng thì thoát vòng lặp
            else:
                console.print("[bold red]Email không hợp lệ! Phải có '@' và tên miền (vd: abc@gmail.com)[/bold red]")
        # --------------------
        phone = Prompt.ask("Số điện thoại")
        address = Prompt.ask("Địa chỉ")
        age = IntPrompt.ask("Tuổi")
        cccd = Prompt.ask("Số CCCD")
        success = user_repo.create_user(username, password, email, phone, address, age, cccd)
        
        if success:
            console.print(f"\n[bold green]✓ Đăng ký thành công! Chào mừng {username}.[/bold green]")
            console.print("[dim]Vui lòng đăng nhập để tiếp tục.[/dim]")
        else:
            console.print("\n[bold red]Đăng ký thất bại (Có thể Email đã tồn tại).[/bold red]")
            
    except Exception as e:
        console.print(f"[red]Lỗi nhập liệu: {e}[/red]")
    
    console.input("Enter để quay lại menu chính...")

def handle_login(user_repo):
    clear()
    console.print(Panel("[bold yellow]ĐĂNG NHẬP HỆ THỐNG[/bold yellow]", box=box.ROUNDED))
    
    email = input("Email: ").strip()
    password = getpass.getpass("Password: ").strip()
    
    user_session = user_repo.authenticate_user(email, password)
    
    if user_session:
        return user_session
    else:
        console.print("\n[bold red]Đăng nhập thất bại! Sai email hoặc mật khẩu.[/bold red]")
        console.input("Enter để thử lại...")
        return None

# MEMBER MENU 
def handle_member_dashboard(current_user, product_repo, cart_repo, user_repo, order_repo):
    """Menu dành cho khách hàng (Member)"""
    while True:
        clear()
        console.print(Panel(f"Xin chào, [bold green]{current_user['username']}[/bold green] (Member)", style="bold white on blue"))
        
        table = Table(box=box.SIMPLE_HEAD)
        table.add_column("Mã", style="cyan", justify="center")
        table.add_column("Chức năng")
        
        table.add_row("1", "Xem & Mua Sản phẩm (Shop)")
        table.add_row("2", "Giỏ hàng của tôi")
        table.add_row("3", "Lịch sử Đơn hàng")
        table.add_row("4", "Cập nhật Hồ sơ")
        table.add_row("0", "Đăng xuất")
        
        console.print(table)
        choice = Prompt.ask("Chọn chức năng", choices=["0", "1", "2", "3", "4"])
        
        if choice == "1":
            ui_shop.handle_view_products(current_user, product_repo, cart_repo)
            
        elif choice == "2":
            is_checkout = ui_bao.handle_cart_menu(current_user['userID'], cart_repo)
            
            if is_checkout:
                handle_checkout_flow(current_user, cart_repo, order_repo)
                
        elif choice == "3":
            ui_bao.handle_view_orders_menu(current_user['userID'], order_repo)
            
        elif choice == "4":
            ui_bao.handle_update_profile_menu(current_user, user_repo)
            
        elif choice == "0":
            break

def handle_checkout_flow(current_user, cart_repo, order_repo):
    """Xử lý thanh toán (Dùng ảnh QR có sẵn)"""
    clear()
    console.print(Panel("[bold green]THANH TOÁN ĐƠN HÀNG[/bold green]"))
    
    cart_items = cart_repo.get_cart_detail(current_user['userID'])
    if not cart_items:
        console.print("[red]Giỏ hàng đang trống![/red]")
        console.input("Enter...")
        return

    total_goods = sum(item['quantity'] * item['unitprice'] for item in cart_items)
    shipping_fee = 30000
    final_total = total_goods + shipping_fee
    
    console.print(f"Tổng tiền hàng: {total_goods:,.0f} VND")
    console.print(f"Phí vận chuyển: {shipping_fee:,.0f} VND")
    console.print(Panel(f"[bold yellow]TỔNG THANH TOÁN: {final_total:,.0f} VND[/bold yellow]"))
    
    console.print("\n[dim]--- Thông tin giao hàng ---[/dim]")
    ship_info = {}
    use_default = Prompt.ask("Dùng thông tin mặc định? (y/n)", choices=['y', 'n'], default='y')
    
    if use_default == 'y':
        ship_info['recipient_name'] = current_user['username']
        ship_info['recipient_phone'] = '0909xxxxxx' 
        ship_info['address'] = 'Địa chỉ mặc định'
    else:
        ship_info['recipient_name'] = Prompt.ask("Tên người nhận")
        ship_info['recipient_phone'] = Prompt.ask("SĐT người nhận")
        ship_info['address'] = Prompt.ask("Địa chỉ giao hàng")

    payment_method = Prompt.ask("Phương thức", choices=["COD", "Online"], default="COD")
    
    # --- HIỂN THỊ ẢNH QR CÓ SẴN ---
    if payment_method == "Online":
        console.print("\n[bold cyan]Đang mở mã QR thanh toán...[/bold cyan]")
        
        qr_filename = "qr_thanhtoan.jpg" 
        qr_path = os.path.join("images", qr_filename)
        
        if os.path.exists(qr_path):
            try:
                img = Image.open(qr_path)
                img.show()
                console.print(f"[green]>> Đã bật ảnh QR: {qr_filename}[/green]")
                console.print(f"[yellow]Vui lòng chuyển khoản số tiền: {final_total:,.0f} VND[/yellow]")
            except Exception as e:
                console.print(f"[red]Lỗi mở ảnh QR: {e}[/red]")
        else:
            console.print(f"[red]Lỗi: Không tìm thấy file ảnh '{qr_filename}' trong thư mục images![/red]")
        
        confirm_pay = Prompt.ask("\nBạn đã chuyển khoản thành công chưa?", choices=['y', 'n'])
        if confirm_pay == 'n':
            console.print("[red]Giao dịch bị hủy.[/red]")
            console.input("Enter...")
            return

    confirm = Prompt.ask("Xác nhận đặt hàng?", choices=['y', 'n'])
    if confirm == 'y':
        order_id = order_repo.place_order(
            current_user['userID'], 
            cart_items, 
            ship_info, 
            payment_method
        )
        if order_id:
            for item in cart_items:
                cart_repo.remove_from_cart(item['cartdetailID'])
            console.print(f"\n[bold green]ĐẶT HÀNG THÀNH CÔNG! Mã đơn: {order_id}[/bold green]")
        else:
            console.print("\n[bold red]Đặt hàng thất bại![/bold red]")
    
    console.input("Enter...")

# MAIN PROGRAM
def main():
    # 1. Kết nối Database
    conn = db_connection()
    if not conn:
        console.print("[bold red]Không thể kết nối Database. Chương trình dừng lại![/bold red]")
        sys.exit(1)
    
    # 2. Khởi tạo các Repository
    user_repo = UserRepository(conn)
    product_repo = ProductRepository(conn)
    cart_repo = CartRepository(conn)
    order_repo = OrderRepository(conn)
    
    while True:
        clear()
        print_logo()
        
        console.print("\n[bold]Vui lòng chọn:[/bold]")
        console.print("1. [green]Đăng nhập[/green]")
        console.print("2. [cyan]Đăng ký[/cyan]")
        console.print("3. [yellow]Quên mật khẩu (OTP)[/yellow]")
        console.print("0. [red]Thoát[/red]")
        
        choice = Prompt.ask("Lựa chọn", choices=["0", "1", "2", "3"])
        
        if choice == "1":
            # Thực hiện đăng nhập
            user_session = handle_login(user_repo)
            
            if user_session:
                role = user_session.get('user_role')
                
                if role == 'Admin':
                    # Vào UI Admin
                    admin_app = ui_admin.Admin(conn) 
                    admin_app.mainView()
                else:
                    # Vào UI Member
                    handle_member_dashboard(user_session, product_repo, cart_repo, user_repo, order_repo)

        elif choice == "2":
            handle_register(user_repo)
            
        elif choice == "3":
            ui_bao.handle_reset_password_menu(user_repo)
            
        elif choice == "0":
            console.print("[bold]Cảm ơn đã sử dụng hệ thống![/bold]")
            conn.close()
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình.")
        sys.exit(0)