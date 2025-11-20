from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich import box
import os

console = Console()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Quản lý Sản phẩm
def manage_products(product_repo):
    while True:
        clear()
        console.rule("[bold blue]QUẢN LÝ SẢN PHẨM[/]")
        
        # 1. Lấy dữ liệu từ DB thật
        products = product_repo.get_all_product()
        
        table = Table(title="Danh sách Sản phẩm", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Tên sản phẩm", style="green")
        table.add_column("Giá", justify="right", style="magenta")
        table.add_column("Tồn kho", justify="center")
        table.add_column("Ảnh", style="dim")

        for p in products:
            table.add_row(
                str(p['productID']), 
                p['productName'],
                f"{float(p['price']):,.0f}đ", 
                str(p['stock_quantity']),
                p['images'] if p['images'] else "N/A"
            )
        console.print(table)
        
        menu = Prompt.ask(
            "\n[bold]Tác vụ[/]: 1.Thêm | 0.Quay lại",
            choices=["0","1"], default="0"
        )
        
        if menu == "1":  # Thêm sản phẩm
            console.print(Panel("[bold green]THÊM SẢN PHẨM MỚI[/]"))
            name = Prompt.ask("Tên sản phẩm")
            code = Prompt.ask("Mã sản phẩm (Code)")
            desc = Prompt.ask("Mô tả")
            price = IntPrompt.ask("Giá (VNĐ)")
            stock = IntPrompt.ask("Số lượng tồn", default=0)
            cat_id = IntPrompt.ask("ID Danh mục (1: Điện thoại, 2: Laptop...)") 
            image = Prompt.ask("Tên file ảnh (vd: iphone.jpg)")
            
            # Gọi Repo thêm mới
            res = product_repo.add_new_product(name, cat_id, code, desc, price, stock, image)
            if res:
                console.print(f"[green]✓ Đã thêm sản phẩm ID={res}[/]")
            else:
                console.print("[red]Thêm thất bại![/red]")
            console.input("Enter...")
            
        elif menu == "0":
            break

# ============================= UC-15: Quản lý Người dùng =============================
def manage_users(user_repo):
    while True:
        clear()
        console.rule("[bold green]QUẢN LÝ NGƯỜI DÙNG[/]")
        
        # Gọi hàm lấy list user (cần đảm bảo UserRepository có hàm này)
        try:
            users = user_repo.admin_get_all_users()
        except AttributeError:
            console.print("[red]Lỗi: UserRepository chưa có hàm 'admin_get_all_users'.[/red]")
            console.input("Enter...")
            return

        table = Table(title="Danh sách Người dùng", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("ID", style="dim")
        table.add_column("Username", style="cyan")
        table.add_column("Email")
        table.add_column("SĐT")
        table.add_column("Vai trò", style="bold")
        
        for u in users:
            role_color = "red" if u["user_role"] == "Admin" else "green"
            table.add_row(
                str(u["userID"]), 
                u["username"], 
                u["email"], 
                u["phonenumber"] if u["phonenumber"] else "",
                f"[{role_color}]{u['user_role']}[/]"
            )
        console.print(table)
        
        # Phần logic xóa/sửa user có thể thêm sau
        console.input("Enter để quay lại...")
        break

# ============================= MENU CHÍNH ADMIN =============================
def handle_admin_menu(user_repo, product_repo, order_repo):
    while True:
        clear()
        console.print(Panel.fit("[bold red]HỆ THỐNG QUẢN TRỊ (ADMIN)[/]", style="bold white on blue"))
        
        table = Table(box=box.DOUBLE, show_header=False)
        table.add_row("1", "Quản lý Sản phẩm (UC-12)")
        table.add_row("2", "Quản lý Người dùng (UC-15)")
        # table.add_row("3", "Quản lý Đơn hàng (UC-14)") 
        table.add_row("0", "Đăng xuất")
        console.print(table)
        
        choice = Prompt.ask("Lựa chọn", choices=["0","1","2"])
        
        if choice == "1":
            manage_products(product_repo)
        elif choice == "2":
            manage_users(user_repo)
        elif choice == "0":
            break