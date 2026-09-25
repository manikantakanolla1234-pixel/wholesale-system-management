CREATE DATABASE wholesale_management;

USE wholesale_management;

CREATE TABLE products(
product_id INT AUTO_INCREMENT PRIMARY KEY,
product_name VARCHAR(100),
category VARCHAR(50),
quantity INT,
purchase_price DECIMAL(10,2),
selling_price DECIMAL(10,2),
supplier VARCHAR(100),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE buyers(
buyer_id INT AUTO_INCREMENT PRIMARY KEY,
buyer_name VARCHAR(100),
phone VARCHAR(15),
email VARCHAR(100),
address VARCHAR(200)
);

CREATE TABLE customers(
customer_id INT AUTO_INCREMENT PRIMARY KEY,
customer_name VARCHAR(100),
phone VARCHAR(15),
city VARCHAR(50)
);

CREATE TABLE sales(
sale_id INT AUTO_INCREMENT PRIMARY KEY,
customer_id INT,
product_id INT,
quantity INT,
sale_date DATE,
total_amount DECIMAL(10,2),
FOREIGN KEY(customer_id)REFERENCES customers(customer_id),
FOREIGN KEY(product_id)REFERENCES products(product_id)
);

CREATE TABLE payments(
payment_id INT AUTO_INCREMENT PRIMARY KEY,
customer_id INT,
amount DECIMAL(10,2),
payment_status ENUM('Paid','Pending'),
payment_date DATE,
FOREIGN KEY(customer_id)REFERENCES customers(customer_id)
);

INSERT INTO products(product_name,category,quantity,purchase_price,selling_price,supplier)VALUES
('Rice','Food',500,40,55,'RambabuTraders'),('Sugar','Food',300,35,50,'Sunil Suppliers'),('Oil','Grocery',200,90,120,'Fresh Mart');

INSERT INTO customers(customer_name,phone,city)VALUES
('Chandra','9876543210','Tirupathi'),('Harsha Reddy','8765432109','Bangalore');

INSERT INTO sales(customer_id,product_id,quantity,sale_date,total_amount)VALUES
(1,1,50,'2026-08-01',2750),(2,2,30,'2026-08-02',1500);

INSERT INTO payments(customer_id,amount,payment_status,payment_date)VALUES
(1,2750,'Paid','2026-08-01'),(2,1500,'Pending','2026-08-02');

INSERT INTO buyers(buyer_name,phone,email,address)
VALUES
('Rambabu Traders','9876500000','abc@gmail.com','Tirupati'),
('Sunil Suppliers','9999988888','xyz@gmail.com','Bangalore');

CREATE INDEX idx_product_name ON products(product_name);

CREATE INDEX idx_customer_phone ON customers(phone);

CREATE VIEW customer_payment_view AS SELECT
customers.customer_name,
payments.amount,
payments.payment_status,
payments.payment_date
FROM customers
JOIN payments
ON customers.customer_id = payments.customer_id;

SELECT * FROM customer_payment_view;

SELECT
MONTH(s.sale_date) AS Month,
SUM(
(p.selling_price-p.purchase_price)
*s.quantity
) AS Profit
FROM sales s
JOIN products p
ON s.product_id=p.product_id GROUP BY MONTH(s.sale_date);

SELECT 
SUM(quantity) AS Total_Stock
FROM products;

SELECT
SUM(total_amount)
AS Total_Sales
FROM sales;

SELECT *
FROM payments
WHERE payment_status='Pending';

CREATE TABLE admin (
admin_id INT AUTO_INCREMENT PRIMARY KEY,
username VARCHAR(50) UNIQUE NOT NULL,
password VARCHAR(100) NOT NULL
);

INSERT INTO admin (username, password)
VALUES ('admin', 'admin123');
select *from sales;
CREATE TABLE IF NOT EXISTS admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);
SELECT
    DATE_FORMAT(sale_date, '%Y-%m') AS month,
    SUM(total_amount) AS total
FROM sales
GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
ORDER BY month;