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
        sql = '''SELECT userID, username, user_role, password
                    FROM "User" 
                    WHERE email = %s'''
        data = (_email,)
        self.cursor.execute(sql, data)
        user_data = self.cursor.fetchone()
        if user_data is None:
            print(f"Lỗi đăng nhập thất bại, không tìm thấy Email: {_email}")
            return None
        
        # Lấy userID từ kết quả query
        db_userID = user_data[0]
        db_userName = user_data[1]
        db_userRole = user_data[2]
        db_hashed_password = user_data[3]
        
        password_byte = _password.encode('utf-8')
        hashed_pw = db_hashed_password.encode('utf-8')

        is_correct = bcrypt.checkpw(password_byte, hashed_pw)
        if is_correct:
            print(f'Đăng nhập thành công vào tài khoản của: {db_userName}')
            return {
                'userID': db_userID,
                'username': db_userName,
                'user_role': db_userRole
            }
        else:
            print(f"Lỗi đăng nhập: Sai mật khẩu của tài khoản {_email}")
            return None
            
    def get_user_by_id(self, user_id):
        try:
            sql = '''SELECT username, email, phonenumber, address, age, cccd FROM "User" WHERE userID = %s'''
            self.cursor.execute(sql, (user_id,))
            res = self.cursor.fetchone()
            if res:
                return {
                    'username': res[0], 
                    'email': res[1], 
                    'phone': res[2],
                    'address': res[3], 
                    'age': res[4], 
                    'cccd': res[5]
                }
            return None
        except Exception as e:
            print(f"Lỗi get_user_by_id: {e}")
            return None

    #===========================================================
    def update_user_profile(self, _userID, _username, _phonenumber, _address, _age, _new_password,_cccd):    
        try:
            if _new_password:
                salt = bcrypt.gensalt()
                password_bytes = _new_password.encode('utf-8')
                hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
                new_hashed_password = hashed_password_bytes.decode('utf-8')
                sql = '''update "User" 
                    set username = %s,
                        password = %s,
                        phonenumber = %s,
                        address = %s,
                        age = %s,
                        cccd = %s
                    where userID = %s'''
                self.cursor.execute(sql, (_username, new_hashed_password, _phonenumber, _address, _age, _cccd, _userID))
            else:
                sql = '''update "User" 
                    set username = %s,
                        phonenumber = %s,
                        address = %s,
                        age = %s,
                        cccd = %s
                    where userID = %s'''
                self.cursor.execute(sql, (_username, _phonenumber, _address, _age, _cccd, _userID))
            self.connection.commit()
            return True # Thêm return True để UI biết thành công
        except Exception as e:
            print(f'lỗi update profile: {e}')
            self.connection.rollback()
            return False
            
    #==================================================================
    def send_otp(self, email):
        otp_code = f"{random.randint(0, 999999):06d}"
        otp_expires_at = datetime.datetime.now() + datetime.timedelta(minutes=5)
        try:
            # Kiểm tra xem email có tồn tại không trước khi update
            check_sql = 'SELECT 1 FROM "User" WHERE email = %s'
            self.cursor.execute(check_sql, (email,))
            if not self.cursor.fetchone():
                return False

            sql = '''UPDATE "User"
                     SET otp_code = %s,
                         otp_expires_at = %s
                     WHERE email = %s'''
            
            self.cursor.execute(sql, (otp_code, otp_expires_at, email))  
            self.connection.commit()         
            print(f"Giả lập: Đã gửi OTP thành công tới email {email}. (OTP: {otp_code})")
            # print(f"Thời gian hết hạn: {otp_expires_at}")
            return True  
        except Exception as e:
            self.connection.rollback()
            print(f"Lỗi hệ thống khi tạo OTP: {e}")
            return False

#========================================..

    def reset_password_otp(self, email, otp_code_input, new_password_plain):
        try:
            sql_select = '''SELECT otp_code, otp_expires_at FROM "User" WHERE email = %s'''
            self.cursor.execute(sql_select, (email,))
            otp_data = self.cursor.fetchone()
            
            if otp_data is None:
                return False # Email không tồn tại

            otp_code_from_db = otp_data[0]
            otp_expires_at = otp_data[1]
            
            if otp_code_from_db is None or otp_expires_at is None:
                 print("Chưa có OTP.")
                 return False
                 
            if otp_expires_at < datetime.datetime.now():
                 print("OTP hết hạn.")
                 return False
                 
            if otp_code_from_db != otp_code_input:
                 print("OTP sai.")
                 return False

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
            sql = '''DELETE FROM "User" WHERE userID = %s'''
            
            self.cursor.execute(sql, (target_userID,))
        
            if self.cursor.rowcount == 0:
                self.connection.rollback()
                raise Exception(f"Không tìm thấy người dùng ID: {target_userID} để xóa.")

            self.connection.commit()
            print(f"✅ Admin: Xóa tài khoản User ID {target_userID} thành công.")
            return True

        except Exception as e:
            self.connection.rollback()
            print(f"❌ LỖI HỆ THỐNG/SQL: Không thể xóa tài khoản: {e}")
            return False