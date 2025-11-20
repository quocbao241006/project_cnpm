-- 1. Xóa bảng cũ để tránh lỗi
DROP TABLE IF EXISTS "payment", "ship", "orderdetail", "Order", "cartdetail", "cart", "admin", "product", "category", "User" CASCADE;

-- 2. Tạo bảng Category
CREATE TABLE category (
    categoryID serial primary key,
    categoryName varchar(100) not null
);

-- 3. Tạo bảng Product
CREATE TABLE product (
    productID serial primary key,
    categoryID int references category(categoryID) on delete set null,
    productName varchar(100) not null,
    description text,
    price bigint,
    product_code varchar(50),
    number_of_sale int default 0,
    images text,
    stock_quantity int not null default 0,
    check(stock_quantity >= 0)
);

-- 4. Tạo bảng User
CREATE TABLE "User" (
    userID SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phonenumber VARCHAR(15),
    address TEXT,
    age INT,
    cccd varchar(13),
    user_role VARCHAR(10) NOT NULL DEFAULT 'Member' CHECK (user_role IN ('Member', 'Admin')),
    otp_code VARCHAR(10),
    otp_expires_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- 5. Tạo bảng Admin
CREATE TABLE admin (
    adminID int primary key references "User"(userID) on delete cascade,
    adminLevel int default 1
);

-- 6. Tạo bảng Cart
CREATE TABLE Cart (
    cartID SERIAL PRIMARY KEY,
    userID INT UNIQUE NOT NULL REFERENCES "User"(userID) ON DELETE CASCADE
);

CREATE TABLE CartDetail (
    cartDetailID SERIAL PRIMARY KEY,
    cartID INT NOT NULL REFERENCES Cart(cartID) ON DELETE CASCADE,
    productID INT NOT NULL REFERENCES product(productID) ON DELETE CASCADE,
    quantity INT NOT NULL CHECK (quantity > 0),
    unitPrice bigint NOT NULL 
);

-- 7. Tạo bảng Order
CREATE TABLE "Order" (
    orderID SERIAL PRIMARY KEY,
    userID INT REFERENCES "User"(userID) ON DELETE SET NULL, 
    orderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    totalAmount BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'New Order'
);

CREATE TABLE OrderDetail (
    orderDetailID SERIAL PRIMARY KEY,
    orderID INT NOT NULL REFERENCES "Order"(orderID) ON DELETE CASCADE,
    productID INT REFERENCES product(productID) ON DELETE SET NULL, 
    quantity INT NOT NULL CHECK (quantity > 0),
    unitPrice BIGINT NOT NULL 
);

-- 8. Tạo bảng Ship
CREATE TABLE Ship (
    shipID SERIAL PRIMARY KEY,
    orderID INT UNIQUE NOT NULL REFERENCES "Order"(orderID) ON DELETE CASCADE,
    shipAddress TEXT NOT NULL, 
    recipient_name VARCHAR(100) NOT NULL, 
    recipient_phone VARCHAR(20) NOT NULL, 
    shipDate TIMESTAMP,
    shipFee BIGINT NOT NULL DEFAULT 0
);

-- 9. Tạo bảng Payment
CREATE TABLE Payment (
    paymentID SERIAL PRIMARY KEY,
    orderID INT NOT NULL REFERENCES "Order"(orderID),
    paymentMethod VARCHAR(30) NOT NULL, 
    amount BIGINT NOT NULL,
    paymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) DEFAULT 'Pending'
);

INSERT INTO category(categoryName) VALUES 
('Điện thoại'), 
('Laptop'), 
('Phụ kiện');

INSERT INTO product(productName, categoryID, product_code, description, price, stock_quantity, images) VALUES 
('iPhone 15 Pro Max', 1, 'IP15', 'Titanium, 256GB', 34000000, 50, 'iphone.png'),
('MacBook Air M2', 2, 'MACM2', 'Apple M2 Chip', 26000000, 20, 'macbook.png'),
('Samsung Galaxy S24 Ultra', 1, 'SS-S24U', 'Chip Snapdragon 8 Gen 3, Camera 200MP, Bút S-Pen tích hợp AI.', 31990000, 50, 's24ultra.jpg'),
('Xiaomi 14 Ultra', 1, 'MI-14U', 'Ống kính Leica thế hệ mới, cảm biến 1 inch, sạc nhanh 90W.', 24990000, 30, 'xiaomi14.jpg'),
('Google Pixel 8 Pro', 1, 'PIXEL8', 'Camera AI chụp đêm siêu đỉnh, Android gốc mượt mà.', 18500000, 20, 'pixel8.jpg'),

-- 2. LAPTOP
('Asus ROG Zephyrus G14', 2, 'ROG-G14', 'Laptop Gaming 14 inch mạnh nhất thế giới, màn hình OLED 120Hz.', 42000000, 15, 'rog_g14.jpg'),
('Dell XPS 13 Plus', 2, 'XPS-13P', 'Thiết kế tương lai, bàn phím vô hình, màn hình 4K cảm ứng.', 38900000, 10, 'dell_xps.jpg'),
('Lenovo ThinkPad X1 Carbon', 2, 'TP-X1', 'Ông vua văn phòng, siêu nhẹ, bàn phím gõ sướng nhất.', 32500000, 25, 'thinkpad.jpg'),
('MacBook Air M2', 2, 'MACM2', 'Apple M2 Chip', 26000000, 20, 'macbook.png'),
-- 3. PHỤ KIỆN
('Sony WH-1000XM5', 3, 'SONY-HP', 'Tai nghe chống ồn chủ động tốt nhất thị trường.', 6990000, 40, 'sony_xm5.jpg'),
('Chuột Logitech MX Master 3S', 3, 'MX-3S', 'Chuột văn phòng yên tĩnh, cuộn vô cực, kết nối 3 thiết bị.', 2100000, 100, 'mx_master3.jpg'),
('Bàn phím cơ Keychron Q1 Pro', 3, 'KEY-Q1', 'Bàn phím cơ Custom, khung nhôm nguyên khối, kết nối Bluetooth.', 4500000, 30, 'keychron.jpg'),
('Sạc dự phòng Anker 737', 3, 'ANKER-737', 'Công suất 140W, sạc được cho cả Laptop, màn hình hiển thị thông số.', 2800000, 60, 'anker737.jpg');