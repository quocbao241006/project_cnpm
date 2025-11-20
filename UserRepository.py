import psycopg2
import bcrypt
from database import db_connection
import random
import datetime
class UserRepository:
    def __init__(self, _connection):
        self.connection = _connection
        self.cursor = self.connection.cursor()
        print("UserReposity đã được khởi tạo")
        pass
    # hàm tạo tài khoản mới 
    def create_user(self, username, _password, _email, _phonenumber, _address, _age, _cccd):
        try:
            salt = bcrypt.gensalt() 
            password_bytes = _password.encode('utf-8') # chuẩn hóa ra byte
            hashed_password = bcrypt.hashpw(password_bytes, salt) # hash, băm mật khẩu
            password = hashed_password.decode('utf-8')
            sql = '''INSERT INTO "User"(username, password, email, phonenumber, address, age, cccd, user_role)
                    VALUES (%s,%s,%s,%s,%s,%s,%s, %s)'''
            data = (username, password, _email,_phonenumber,_address,_age,_cccd, 'Member')
            self.cursor.execute(sql, data)
            self.connection.commit()
            return True
        except psycopg2.errors.UniqueViolation as e:
            print("lỗi tạo")
            self.connection.rollback()
            return False
    #===================================================================
    def authenticate_user(self, _email, _password):
        sql = '''SELECT username, user_role, password
                    FROM "User" 
                    WHERE email = %s'''
        data = (_email,)
        self.cursor.execute(sql, data)
        user_data = self.cursor.fetchone()
        if user_data is None:
            print(f"Lỗi đăng nhập thất bại, không tìm thấy Email: {_email}")
            return None
        db_userName = user_data[0]
        db_userRole = user_data[1]
        db_hashed_password = user_data[2]
        password_byte = _password.encode('utf-8')
        hashed_pw = db_hashed_password.encode('utf-8')

        is_correct = bcrypt.checkpw(password_byte, hashed_pw)
        if is_correct:
            print(f'Đăng nhập thành công vào tài khoản của: {db_userName}')
            return {
            'username': db_userName,
            'user_role': db_userRole
            }
        else:
            print(f"Lỗi đăng nhập: Sai mật khẩu của tài khoản {_email}")
            return None
    #===========================================================
    def update_user_profile(self, _userID, _username, _phonenumber, _address, _age, _new_password,_cccd):    
        try:
            if _new_password:
                salt = bcrypt.gensalt()
                password_bytes = _new_password.encode('utf-8')
                hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
                new_hashed_password = hashed_password_bytes.decode('utf-8')
                sql = '''update "user" 
                    set username = %s,
                        password = %s,
                        phonenumber = %s,
                        address = %s,
                        age = %s,
                        cccd = %s
                    where userID = %s'''
                self.cursor.execute(sql, (_username, new_hashed_password, _phonenumber, _address, _age, _cccd, _userID))
            else:
                sql = '''update "user" 
                    set username = %s,
                        phonenumber = %s,
                        address = %s,
                        age = %s,
                        cccd = %s,
                    where userID = %s'''
                self.cursor.execute(sql, (_username, _phonenumber, _address, _age, _cccd, _userID))
            self.connection.commit()
        except Exception as e:
            print(f'lỗi: {e}')
            self.connection.rollback()
    #==================================================================
    def send_otp(self, email):
        otp_code = f"{random.randint(0, 999999):06d}"
        otp_expires_at = datetime.datetime.now() + datetime.timedelta(minutes=5)
        try:
            sql = '''UPDATE "User"
                     SET otp_code = %s,
                         otp_expires_at = %s
                     WHERE email = %s'''
            
            self.cursor.execute(sql, (otp_code, otp_expires_at, email))  
            self.connection.commit()         
            print(f"Giả lập: Đã gửi OTP thành công tới email {email}. (OTP: {otp_code})")
            print(f"Thời gian hết hạn: {otp_expires_at}")
            return True  
        except Exception as e:
            self.connection.rollback()
            print(f"Lỗi hệ thống khi tạo OTP: {e}")
            return False
    import datetime # Cần thiết cho việc kiểm tra thời gian hết hạn

#========================================..

    def reset_password_otp(self, email, otp_code_input, new_password_plain):
        try:
            sql_select = '''SELECT otp_code, otp_expires_at FROM "User" WHERE email = %s'''
            self.cursor.execute(sql_select, (email,))
            otp_data = self.cursor.fetchone()
            if otp_data is None:
                return True 
            otp_code_from_db = otp_data[0]
            otp_expires_at = otp_data[1]
            if otp_code_from_db is None or otp_expires_at is None:
                 raise Exception("Bạn chưa gửi yêu cầu reset mật khẩu.")
            if otp_expires_at < datetime.datetime.now():
                 raise Exception("Mã OTP đã hết hạn. Vui lòng gửi yêu cầu mới.")
            if otp_code_from_db != otp_code_input:
                 raise Exception("Mã OTP không đúng.")
            salt = bcrypt.gensalt()
            password_bytes = new_password_plain.encode('utf-8')
            hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
            new_hashed_password = hashed_password_bytes.decode('utf-8')
            sql_update = '''UPDATE "User"
                            SET password = %s,
                                otp_code = NULL,
                                otp_expires_at = NULL
                            WHERE email = %s'''         
            self.cursor.execute(sql_update, (new_hashed_password, email))
            self.connection.commit()
            print(f"✅ Reset mật khẩu cho email {email} thành công.")
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"❌ Lỗi Reset: {e}")
            return False
        
    #===============================================================
    def admin_get_all_users(self):
        try:
            sql = '''
                SELECT 
                    userID, 
                    username, 
                    email, 
                    phonenumber, 
                    user_role,
                    address,
                    age,
                    cccd
                FROM "User"
                ORDER BY userID ASC; -- Sắp xếp theo ID
            '''
            
            self.cursor.execute(sql)
            users_data = self.cursor.fetchall()
            users_list = []
            for item in users_data:
                users_list.append({
                    'userID': item[0],
                    'username': item[1],
                    'email': item[2],
                    'phonenumber': item[3],
                    'user_role': item[4],
                    'address': item[5],
                    'age': item[6],
                    'cccd': item[7]
                })

            return users_list
            
        except Exception as e:
            print(f"Lỗi khi truy xuất danh sách người dùng cho Admin: {e}")
            return []
    #==================================================
    def get_user_by_id(self, _userID):
        try:
            sql = '''SELECT userID, username, email, phonenumber, address, age, cccd, user_role, is_active 
                     FROM "User" 
                     WHERE userID = %s'''
            
            self.cursor.execute(sql, (_userID,))
            row = self.cursor.fetchone()
            
            if row:
                return {
                    'userID': row[0],
                    'username': row[1],
                    'email': row[2],
                    'phonenumber': row[3],
                    'address': row[4],
                    'age': row[5],
                    'cccd': row[6],
                    'user_role': row[7],
                    'is_active': row[8] # Lấy cả trạng thái khóa
                }
            return None
        except Exception as e:
            print(f"Lỗi lấy thông tin user ID {_userID}: {e}")
            return None
        
    def admin_update_user_status(self, target_userID, new_username, new_role, new_phone, new_address, new_age, new_cccd):
        try:
            sql = '''UPDATE "User" 
                     SET username = %s,
                         user_role = %s, 
                         phonenumber = %s,
                         address = %s,
                         age = %s,
                         cccd = %s
                     WHERE userID = %s'''
            self.cursor.execute(sql, (
                new_username, 
                new_role, 
                new_phone, 
                new_address, 
                new_age, 
                new_cccd, 
                target_userID 
            ))
            
            if self.cursor.rowcount == 0:
                self.connection.rollback()
                raise Exception(f"Không tìm thấy người dùng có userID: {target_userID} để cập nhật.")

            self.connection.commit()
            print(f"✅ Admin: Cập nhật thành công thông tin và Role cho User ID {target_userID}.")
            return True

        except Exception as e:
            self.connection.rollback()
            print(f"❌ LỖI HỆ THỐNG/SQL: Không thể cập nhật thông tin user: {e}")
            return False
    def admin_delete_user(self, target_userID):
        try:
            sql = '''UPDATE "User" 
                     SET is_active = FALSE
                     WHERE userID = %s'''
            
            self.cursor.execute(sql, (target_userID,))
        
            if self.cursor.rowcount == 0:
                self.connection.rollback()
                raise Exception(f"Không tìm thấy người dùng ID: {target_userID} để khóa.")

            self.connection.commit()
            print(f"✅ Admin: Khóa tài khoản User ID {target_userID} thành công.")
            return True

        except Exception as e:
            self.connection.rollback()
            print(f"❌ LỖI HỆ THỐNG/SQL: Không thể khóa tài khoản: {e}")
            return False