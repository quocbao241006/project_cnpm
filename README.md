# Hướng dẫn chạy Project (Với Docker)

Hệ thống yêu cầu Docker để chạy Database và Python để chạy ứng dụng.

## Bước 1: Chuẩn bị Database (Dùng Docker)
Thay vì cài đặt PostgreSQL thủ công, bạn chỉ cần chạy lệnh sau tại thư mục dự án:

docker-compose up -d

*(Lệnh này sẽ tự động tải và khởi chạy server PostgreSQL trên cổng 5433)*

## Bước 2: Cài đặt môi trường Python
1. Tạo môi trường ảo (khuyến nghị):
   python -m venv venv
  ## Cấp quyền chạy script
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    ## kich hoat moi truong ao
   .\venv\Scripts\activate


2. Cài đặt các thư viện cần thiết:
   pip install -r requirement.txt

## Tạo tài khoản Admin
    python create_admin.py
## Bước 3: Chạy ứng dụng
python main.py

## Thông tin truy cập
- Database: localhost:5433
- User/Pass: group14 / 1234
- Admin App: Đăng nhập bằng tài khoản Admin.
Email: admin@gmail.com

Pass: 1234