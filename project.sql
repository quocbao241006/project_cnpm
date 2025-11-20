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
('MacBook Air M2', 2, 'MACM2', 'Apple M2 Chip', 26000000, 20, 'macbook.png');
