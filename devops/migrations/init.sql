-- Справочник категорий товаров
CREATE TABLE NSI_category_of_goods (
    id SERIAL PRIMARY KEY,
    category_of_goods VARCHAR
);

-- Справочник единиц измерения
CREATE TABLE NSI_unit_of_measure (
    id SERIAL PRIMARY KEY,
    unit_name VARCHAR
);

-- Справочник поставщиков
CREATE TABLE NSI_of_supplies (
    id SERIAL PRIMARY KEY,
    Supplier VARCHAR,
    phone_number VARCHAR
);

-- Складские помещения
CREATE TABLE Warehouses (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    address VARCHAR,
    capacity INT,
    opened_at DATE
);

-- Магазины
CREATE TABLE Shops (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    address VARCHAR,
    opened_at DATE,
    phone_number VARCHAR,
    working_hours_start TIME,
    working_hours_end TIME
);

-- Список товаров
CREATE TABLE List_of_goods (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    category_id INT NOT NULL,
    unit_id INT NOT NULL,
    volume_or_weight BIGINT NOT NULL,
    price DECIMAL,
    FOREIGN KEY (category_id) REFERENCES NSI_category_of_goods(id),
    FOREIGN KEY (unit_id) REFERENCES NSI_unit_of_measure(id)
);

-- Клиенты
CREATE TABLE Clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    phone_number VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    date_of_birth DATE
);

-- Работники
CREATE TABLE Workers (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    warehouse_id INT,
    shop_id INT,
    position VARCHAR,
    hire_date DATE,
    salary DECIMAL,
    FOREIGN KEY (warehouse_id) REFERENCES Warehouses(id),
    FOREIGN KEY (shop_id) REFERENCES Shops(id)
);

-- Поставки со склада
CREATE TABLE Supplies_from_warehouse (
    serial_id SERIAL PRIMARY KEY,
    delivery_date DATE NOT NULL,
    total_price DECIMAL,
    nsi_of_supplies_id INT NOT NULL,
    warehouse_id INT,
    FOREIGN KEY (nsi_of_supplies_id) REFERENCES NSI_of_supplies(id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouses(id)
);

-- Заказы
CREATE TABLE Orders (
    order_number VARCHAR UNIQUE NOT NULL,
    client_id INT NOT NULL,
    shop_id INT,
    date_of_order DATE,
    total_price DECIMAL,
    status VARCHAR,
    PRIMARY KEY (order_number),
    FOREIGN KEY (client_id) REFERENCES Clients(id),
    FOREIGN KEY (shop_id) REFERENCES Shops(id)
);

-- Счета
CREATE TABLE Invoices (
    invoicenumber VARCHAR UNIQUE NOT NULL,
    total_price DECIMAL,
    dispatch_date DATE NOT NULL,
    receipt_date DATE,
    supply_id INT NOT NULL,
    goodid INT,
    shop_id INT,
    status VARCHAR,
    PRIMARY KEY (invoicenumber),
    FOREIGN KEY (supply_id) REFERENCES Supplies_from_warehouse(serial_id),
    FOREIGN KEY (goodid) REFERENCES List_of_goods(id),
    FOREIGN KEY (shop_id) REFERENCES Shops(id)
);

-- Позиции заказанных товаров
CREATE TABLE Ordered_goods (
    id SERIAL PRIMARY KEY,
    quantity INT NOT NULL,
    price_per_unit DECIMAL,
    subtotal DECIMAL,
    order_id VARCHAR NOT NULL,
    invoice_id VARCHAR NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_number),
    FOREIGN KEY (invoice_id) REFERENCES Invoices(invoicenumber)
);

-- Чеки (ИСПРАВЛЕНО: orders_id теперь VARCHAR)
CREATE TABLE Receipts (
    receipt_number VARCHAR UNIQUE NOT NULL,
    date_oforder DATE,
    total_price DECIMAL,
    payment_method VARCHAR,
    shop_workerid INT,
    client_id INT,
    orders_id VARCHAR UNIQUE,
    PRIMARY KEY (receipt_number),
    FOREIGN KEY (shop_workerid) REFERENCES Workers(id),
    FOREIGN KEY (client_id) REFERENCES Clients(id),
    FOREIGN KEY (orders_id) REFERENCES Orders(order_number)
);

-- Позиции в чеке
CREATE TABLE Receipt_positions (
    id SERIAL PRIMARY KEY,
    quantity INT NOT NULL,
    price_per_unit DECIMAL,
    subtotal DECIMAL,
    receipt_id VARCHAR NOT NULL,
    invoice_id VARCHAR NOT NULL,
    FOREIGN KEY (receipt_id) REFERENCES Receipts(receipt_number),
    FOREIGN KEY (invoice_id) REFERENCES Invoices(invoicenumber)
);

CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'replicator';

GRANT USAGE ON SCHEMA public TO replicator;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO replicator;

GRANT CONNECT ON DATABASE vinlab TO replicator;