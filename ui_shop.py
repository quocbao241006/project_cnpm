import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from PIL import Image 

console = Console()

def clear(): 
    os.system('cls' if os.name == 'nt' else 'clear')


# 1. HÀM HIỂN THỊ ẢNH

def show_image(image_name, width=60, max_height=30):
    """Mở ảnh bằng trình xem ảnh mặc định của Windows"""
    if not image_name: return

    image_path = os.path.join("images", image_name)

    if not os.path.exists(image_path):
        console.print(f"[dim italic](Không tìm thấy file ảnh: {image_name})[/dim italic]")
        return

    try:
        img = Image.open(image_path)
        
        img.show()
        
        console.print(f"[bold green]>> Đang mở ảnh: {image_name} (Kiểm tra cửa sổ mới bật lên)[/bold green]")
        
    except Exception as e:
        console.print(f"[red]Lỗi hiển thị ảnh: {e}[/red]")

# 2. HÀM XEM CHI TIẾT & MUA

def view_product_detail(current_user, product, cart_repo):
    clear()
    # 1. Hiển thị thông tin text
    console.print(f"[bold green]{product['productName'].upper()}[/bold green]", justify="center")
    console.print(f"Giá: [bold red]{float(product['price']):,.0f} đ[/bold red]", justify="center")
    console.print(f"Tồn kho: {product['stock_quantity']}")
    console.print(Panel(product['description'], title="Mô tả"))
    
    # 2. Mở ảnh Popup
    show_image(product['images']) 
    
    # 3. Menu mua hàng
    console.print("\n[bold yellow]1. Thêm vào giỏ hàng (UC-6)[/bold yellow]")
    console.print("0. Quay lại")
    
    choice = input("Chọn: ").strip()
    
    if choice == '1':
        if not current_user:
            console.print("[red]Vui lòng Đăng nhập để mua hàng![/red]")
            console.input("Enter...")
            return

        try:
            qty_input = input("Nhập số lượng mua: ")
            if not qty_input.isdigit():
                console.print("[red]Vui lòng nhập số![/red]")
                console.input("Enter...")
                return
                
            qty = int(qty_input)
            if qty > 0:
                if qty > product['stock_quantity']:
                     console.print("[red]Số lượng tồn kho không đủ![/red]")
                else:
                    # Thêm vào giỏ
                    cart_repo.add_to_cart(
                        current_user['userID'], 
                        product['productID'], 
                        qty, 
                        product['price']
                    )
                    console.print("[green]Đã thêm vào giỏ thành công![/green]")
            else:
                console.print("[red]Số lượng phải > 0[/red]")
        except Exception as e:
            console.print(f"[red]Lỗi: {e}[/red]")
        
        console.input("Enter...")

# 3. HÀM MENU DANH SÁCH
def handle_view_products(current_user, product_repo, cart_repo):
    while True:
        clear()
        console.print("[bold cyan]DANH SÁCH SẢN PHẨM (UC-5)[/bold cyan]")
        
        products = product_repo.get_all_product()
        
        if not products:
            console.print("[red]Chưa có sản phẩm nào trong Database.[/red]")
            console.input("Enter...")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=5)
        table.add_column("Tên sản phẩm", min_width=20)
        table.add_column("Giá", justify="right", style="green")
        table.add_column("Kho", justify="right")
        
        valid_ids = []
        for p in products:
            valid_ids.append(str(p['productID']))
            table.add_row(
                str(p['productID']),
                p['productName'],
                f"{float(p['price']):,.0f} đ",
                str(p['stock_quantity'])
            )
        
        console.print(table)
        console.print("\n[bold yellow]Nhập ID sản phẩm để xem chi tiết[/bold yellow]")
        console.print("[dim](Gõ 's' để tìm kiếm, '0' để quay lại)[/dim]")
        
        choice = input("Lựa chọn: ").strip().lower()
        
        if choice == '0':
            break
        elif choice == 's':
            kw = input("Nhập từ khóa: ")
            results = product_repo.search_product(kw)
            console.print(f"Tìm thấy {len(results)} kết quả.")
            console.input("Enter...")
            
        elif choice in valid_ids:
            selected_p = next((p for p in products if str(p['productID']) == choice), None)
            if selected_p:
                view_product_detail(current_user, selected_p, cart_repo)