import getpass
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# KHÔI PHỤC MẬT KHẨU

def handle_reset_password_menu(user_repo):
    clear_screen()
    console.print(Panel("[bold yellow]Khôi phục Mật khẩu (UC-3)[/bold yellow]", padding=1))
    
    email = input("Nhập email đã đăng ký: ").strip()
    
    try:
        if user_repo.send_otp(email):
            console.print("[green]Mã OTP đã được gửi (Xem console của server).[/green]")
            
            otp_input = input("Nhập mã OTP: ").strip()
            new_pass = getpass.getpass("Nhập mật khẩu mới: ").strip()
            confirm_pass = getpass.getpass("Xác nhận mật khẩu: ").strip()
            
            if new_pass != confirm_pass:
                console.print("[red]Mật khẩu không khớp![/red]")
                console.input("Enter...")
                return

            if user_repo.reset_password_otp(email, otp_input, new_pass):
                console.print("[bold green]Reset thành công! Hãy đăng nhập lại.[/bold green]")
                console.input("Enter...")
            else:
                console.print("[red]Reset thất bại.[/red]")
                console.input("Enter...")
        else:
            console.print("[red]Gửi OTP thất bại (Email không tồn tại?).[/red]")
            console.input("Enter...")
            
    except Exception as e:
        console.print(f"[red]Lỗi: {e}[/red]")
        console.input("Enter...")

#QUẢN LÝ GIỎ HÀNG
def handle_cart_menu(user_id, cart_repo):
    while True:
        clear_screen()
        console.print(Panel("[bold cyan]Giỏ hàng của bạn (UC-7)[/bold cyan]", padding=1))

        cart_items = cart_repo.get_cart_detail(user_id)

        if not cart_items:
            console.print("[yellow]Giỏ hàng trống.[/yellow]")
            console.print("\n1. Quay lại")
            if input("Chọn: ").strip() == '1': return False
            continue

        # In bảng
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID Chi tiết", style="dim", width=5)
        table.add_column("Sản phẩm", style="white")
        table.add_column("Đơn giá", justify="right", style="green")
        table.add_column("SL", justify="center", style="cyan")
        table.add_column("Thành tiền", justify="right", style="bold green")

        total_cart = 0
        for item in cart_items:
            price = float(item['unitprice'])
            qty = int(item['quantity'])
            subtotal = price * qty
            total_cart += subtotal
            
            table.add_row(
                str(item['cartdetailID']),
                item['productName'],
                f"{price:,.0f}",
                str(qty),
                f"{subtotal:,.0f}"
            )

        console.print(table)
        console.print(f"\n[bold]TỔNG CỘNG: {total_cart:,.0f} VND[/bold]")

        console.print("\n[bold yellow]Hành động:[/bold yellow]")
        console.print("1. Sửa số lượng (Nhập ID Chi tiết)")
        console.print("2. Xóa sản phẩm (Nhập ID Chi tiết)")
        console.print("3. THANH TOÁN")
        console.print("0. Quay lại")

        choice = input("Chọn: ").strip()

        if choice == '1':
            try:
                cid = int(input("Nhập ID Chi tiết (cột đầu tiên): "))
                new_qty = int(input("Số lượng mới (0 để xóa): "))
                cart_repo.update_cart_quantity(cid, new_qty)
                console.print("[green]Đã cập nhật![/green]")
            except: console.print("[red]Lỗi nhập liệu[/red]")
            console.input("Enter...")

        elif choice == '2':
            try:
                cid = int(input("Nhập ID Chi tiết: "))
                cart_repo.remove_from_cart(cid)
                console.print("[green]Đã xóa![/green]")
            except: console.print("[red]Lỗi nhập liệu[/red]")
            console.input("Enter...")

        elif choice == '3':
            return True
            
        elif choice == '0':
            return False


# LỊCH SỬ & HỦY ĐƠN
def handle_view_orders_menu(user_id, order_repo):
    while True:
        clear_screen()
        console.print(Panel("[bold cyan]Lịch sử Đơn hàng (UC-10)[/bold cyan]", padding=1))

        orders = order_repo.get_member_orders(user_id)

        if not orders:
            console.print("[yellow]Bạn chưa có đơn hàng nào.[/yellow]")
            console.input("Enter để quay lại...")
            return

        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Ngày đặt", style="dim")
        table.add_column("Tổng tiền", justify="right", style="green")
        table.add_column("Trạng thái", style="bold yellow")

        for o in orders:
            table.add_row(
                str(o['orderID']),
                str(o['orderDate']),
                f"{float(o['totalAmount']):,.0f}",
                o['status']
            )
        console.print(table)
        
        console.print("\n[bold yellow]1. Hủy đơn hàng (Chỉ đơn 'New Order')[/bold yellow]")
        console.print("0. Quay lại")
        
        c = input("Chọn: ").strip()
        if c == '1':
            try:
                oid = int(input("Nhập ID Đơn hàng: "))
                if order_repo.cancel_order(oid, user_id):
                    console.print("[bold green]Đã hủy thành công![/bold green]")
                else:
                    console.print("[bold red]Hủy thất bại (Sai trạng thái hoặc không phải đơn của bạn).[/bold red]")
            except: console.print("[red]Lỗi nhập ID.[/red]")
            console.input("Enter...")
        elif c == '0':
            break

# CẬP NHẬT HỒ SƠ
def handle_update_profile_menu(current_user, user_repo):
    while True:
        clear_screen()
        uid = current_user['userID']
        console.print(Panel(f"Cập nhật Hồ sơ (UC-11)", padding=1))
        
        # Lấy thông tin mới nhất từ DB
        info = user_repo.get_user_by_id(uid)
        if not info:
            console.print("[red]Lỗi lấy thông tin user.[/red]")
            return

        console.print(f"Username: [green]{info['username']}[/green]")
        console.print(f"SĐT: {info['phone']}")
        console.print(f"Địa chỉ: {info['address']}")
        console.print(f"Tuổi: {info['age']}")
        
        print("\n1. Cập nhật thông tin")
        print("0. Quay lại")
        
        if input("Chọn: ").strip() == '1':
            print("\n--- Nhập thông tin mới (Enter để giữ nguyên) ---")
            new_user = input(f"Username ({info['username']}): ").strip() or info['username']
            new_phone = input(f"SĐT ({info['phone']}): ").strip() or info['phone']
            new_addr = input(f"Địa chỉ ({info['address']}): ").strip() or info['address']
            new_age = input(f"Tuổi ({info['age']}): ").strip() or str(info['age'])
            new_cccd = input(f"CCCD ({info['cccd']}): ").strip() or info['cccd']
            new_pass = getpass.getpass("Mật khẩu mới (Bỏ trống để giữ nguyên): ").strip()
            
            try:
                user_repo.update_user_profile(
                    uid, new_user, new_phone, new_addr, int(new_age), 
                    new_pass if new_pass else None, new_cccd
                )
                console.print("[green]Đã cập nhật![/green]")
            except Exception as e:
                console.print(f"[red]Lỗi: {e}[/red]")
            console.input("Enter...")
        else:
            break