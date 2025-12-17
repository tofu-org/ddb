from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

# Справочник категорий товаров
class NSICategoryOfGoods(db.Model):
    __tablename__ = 'nsi_category_of_goods'
    
    id = db.Column(db.Integer, primary_key=True)
    category_of_goods = db.Column(db.String)

# Справочник единиц измерения
class NSIUnitOfMeasure(db.Model):
    __tablename__ = 'nsi_unit_of_measure'
    
    id = db.Column(db.Integer, primary_key=True)
    unit_name = db.Column(db.String)

# Справочник поставщиков
class NSIOfSupplies(db.Model):
    __tablename__ = 'nsi_of_supplies'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier = db.Column('supplier', db.String)
    phone_number = db.Column(db.String)

# Складские помещения
class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    capacity = db.Column(db.Integer)
    opened_at = db.Column(db.Date)

# Магазины
class Shop(db.Model):
    __tablename__ = 'shops'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String)
    opened_at = db.Column(db.Date)
    phone_number = db.Column(db.String)
    working_hours_start = db.Column(db.Time)
    working_hours_end = db.Column(db.Time)

# Список товаров
class ListOfGoods(db.Model):
    __tablename__ = 'list_of_goods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('nsi_category_of_goods.id'), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('nsi_unit_of_measure.id'), nullable=False)
    volume_or_weight = db.Column(db.BigInteger, nullable=False)
    price = db.Column(db.Numeric)
    
    category = db.relationship('NSICategoryOfGoods', backref='goods')
    unit = db.relationship('NSIUnitOfMeasure', backref='goods')

# Клиенты
class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    
    orders = db.relationship('Order', backref='client', lazy='dynamic')

# Работники
class Worker(db.Model):
    __tablename__ = 'workers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))
    position = db.Column(db.String)
    hire_date = db.Column(db.Date)
    salary = db.Column(db.Numeric)
    
    warehouse = db.relationship('Warehouse', backref='workers')
    shop = db.relationship('Shop', backref='workers')

# Поставки со склада
class SupplyFromWarehouse(db.Model):
    __tablename__ = 'supplies_from_warehouse'
    
    serial_id = db.Column(db.Integer, primary_key=True)
    delivery_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Numeric)
    nsi_of_supplies_id = db.Column(db.Integer, db.ForeignKey('nsi_of_supplies.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))
    
    supplier = db.relationship('NSIOfSupplies', backref='supplies')
    warehouse = db.relationship('Warehouse', backref='supplies')

# Заказы
class Order(db.Model):
    __tablename__ = 'orders'
    
    order_number = db.Column(db.String, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))
    date_of_order = db.Column(db.Date)
    total_price = db.Column(db.Numeric)
    status = db.Column(db.String)
    
    shop = db.relationship('Shop', backref='orders')
    receipt = db.relationship('Receipt', backref='order', uselist=False)
    ordered_goods = db.relationship('OrderedGoods', backref='order', lazy='dynamic')
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

# Счета
class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    invoicenumber = db.Column(db.String, primary_key=True)
    total_price = db.Column(db.Numeric)
    dispatch_date = db.Column(db.Date, nullable=False)
    receipt_date = db.Column(db.Date)
    supply_id = db.Column(db.Integer, db.ForeignKey('supplies_from_warehouse.serial_id'), nullable=False)
    goodid = db.Column(db.Integer, db.ForeignKey('list_of_goods.id'))
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'))
    status = db.Column(db.String)
    
    supply = db.relationship('SupplyFromWarehouse', backref='invoices')
    good = db.relationship('ListOfGoods', backref='invoices')
    shop = db.relationship('Shop', backref='invoices')

# Позиции заказанных товаров
class OrderedGoods(db.Model):
    __tablename__ = 'ordered_goods'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Numeric)
    subtotal = db.Column(db.Numeric)
    order_id = db.Column(db.String, db.ForeignKey('orders.order_number'), nullable=False)
    invoice_id = db.Column(db.String, db.ForeignKey('invoices.invoicenumber'), nullable=False)
    
    invoice = db.relationship('Invoice', backref='ordered_goods')

# Чеки
class Receipt(db.Model):
    __tablename__ = 'receipts'
    
    receipt_number = db.Column(db.String, primary_key=True)
    date_oforder = db.Column(db.Date)
    total_price = db.Column(db.Numeric)
    payment_method = db.Column(db.String)
    shop_workerid = db.Column(db.Integer, db.ForeignKey('workers.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    orders_id = db.Column(db.String, db.ForeignKey('orders.order_number'), unique=True)
    
    worker = db.relationship('Worker', backref='receipts')
    client = db.relationship('Client', backref='receipts')
    receipt_positions = db.relationship('ReceiptPosition', backref='receipt', lazy='dynamic')
    
    def __repr__(self):
        return f'<Receipt {self.receipt_number}>'

# Позиции в чеке
class ReceiptPosition(db.Model):
    __tablename__ = 'receipt_positions'
    
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Numeric)
    subtotal = db.Column(db.Numeric)
    receipt_id = db.Column(db.String, db.ForeignKey('receipts.receipt_number'), nullable=False)
    invoice_id = db.Column(db.String, db.ForeignKey('invoices.invoicenumber'), nullable=False)
    
    invoice = db.relationship('Invoice', backref='receipt_positions')
