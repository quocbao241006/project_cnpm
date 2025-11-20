import bcrypt
import psycopg2
from database import db_connection

def create_default_admin():
    print("Dang ket noi Database de tao Admin...")
    conn = db_connection()
    
    if not conn:
        print("Loi: Khong the ket noi Database.")
        return

    try:
        cursor = conn.cursor()
        
        # 1. Thông tin Admin mặc định
        admin_email = "admin@gmail.com"
        admin_pass_raw = "1234"
        admin_name = "Super Admin"
        
        # 2. Hash mật khẩu
        salt = bcrypt.gensalt()
        hashed_pass = bcrypt.hashpw(admin_pass_raw.encode('utf-8'), salt).decode('utf-8')
        
        # 3. Câu lệnh SQL chèn Admin
        sql = """
            INSERT INTO "User" (username, password, email, phonenumber, address, age, cccd, user_role)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING;
        """
    
        data = (
            admin_name, 
            hashed_pass, 
            admin_email, 
            "0909123456",   
            "System HQ",    
            30,             
            "001090123456", 
            "Admin"         # Set Role là Admin
        )
        
        cursor.execute(sql, data)
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Đã tạo thành công Admin: {admin_email} / Pass: {admin_pass_raw}")
        else:
            print(f"⚠️ Tài khoản {admin_email} đã tồn tại (có thể do trùng email).")
            cursor.execute('UPDATE "User" SET user_role = %s WHERE email = %s', ('Admin', admin_email))
            conn.commit()
            print(f"-> Đã cập nhật quyền Admin cho {admin_email}")
            
    except Exception as e:
        print(f"❌ Lỗi khi tạo Admin: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_default_admin()