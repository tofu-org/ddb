from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import (db, Order, Receipt, Client, Shop, OrderedGoods, 
                    Invoice, ListOfGoods, Worker, ReceiptPosition)
from config import Config
from datetime import datetime, date
from decimal import Decimal
import random
import string

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

def generate_order_number():
    """Генерация уникального номера заказа"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f'ORD-{timestamp}-{random_suffix}'

def generate_receipt_number():
    """Генерация уникального номера чека"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f'RCP-{timestamp}-{random_suffix}'


@app.route('/')
def index():
    return render_template('base.html')


# ============ ИНТЕРФЕЙС КЛИЕНТА ============

@app.route('/customer')
def customer_orders():
    """Список заказов для клиентов"""
    # Можно добавить фильтрацию по email или phone для конкретного клиента
    email = request.args.get('email', '')
    
    if email:
        client = Client.query.filter_by(email=email).first()
        if client:
            orders = client.orders.order_by(Order.date_of_order.desc()).all()
        else:
            orders = []
            flash('Клиент не найден', 'warning')
    else:
        orders = Order.query.order_by(Order.date_of_order.desc()).limit(50).all()
    
    return render_template('customer_orders.html', orders=orders, search_email=email)


@app.route('/customer/order/<order_number>')
def customer_view_order(order_number):
    """Просмотр заказа клиентом"""
    order = Order.query.get_or_404(order_number)
    ordered_items = order.ordered_goods.all()
    return render_template('edit_order.html', 
                         order=order, 
                         ordered_items=ordered_items,
                         user_type='customer',
                         editable=False)


@app.route('/customer/order/<order_number>/edit', methods=['GET', 'POST'])
def customer_edit_order(order_number):
    """Редактирование заказа клиентом (ограниченные права)"""
    order = Order.query.get_or_404(order_number)
    
    # Клиент может редактировать только заказы в определенных статусах
    editable_statuses = ['Pending', 'Новый', 'Ожидает подтверждения']
    if order.status not in editable_statuses:
        flash('Вы можете редактировать только заказы в статусе "Ожидает подтверждения"', 'warning')
        return redirect(url_for('customer_orders'))
    
    if request.method == 'POST':
        # Клиент может изменить только адрес доставки через магазин
        new_shop_id = request.form.get('shop_id')
        if new_shop_id:
            order.shop_id = int(new_shop_id)
            order.date_of_order = date.today()
            db.session.commit()
            flash('Заказ успешно обновлен!', 'success')
        return redirect(url_for('customer_orders'))
    
    shops = Shop.query.all()
    ordered_items = order.ordered_goods.all()
    return render_template('edit_order.html', 
                         order=order,
                         ordered_items=ordered_items,
                         shops=shops,
                         user_type='customer',
                         editable=True)


@app.route('/customer/order/<order_number>/cancel', methods=['POST'])
def customer_cancel_order(order_number):
    """Отмена заказа клиентом"""
    order = Order.query.get_or_404(order_number)
    
    cancellable_statuses = ['Pending', 'Новый', 'Ожидает подтверждения']
    if order.status in cancellable_statuses:
        order.status = 'Отменен'
        if order.receipt:
            order.receipt.payment_method = 'Возврат'
        db.session.commit()
        flash('Заказ отменен', 'info')
    else:
        flash('Невозможно отменить заказ в текущем статусе', 'warning')
    
    return redirect(url_for('customer_orders'))


# ============ ИНТЕРФЕЙС СОТРУДНИКА ============

@app.route('/staff')
def staff_orders():
    """Список заказов для сотрудников"""
    status_filter = request.args.get('status', 'all')
    shop_filter = request.args.get('shop', 'all')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = Order.query
    
    # Фильтр по статусу
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Фильтр по магазину
    if shop_filter != 'all':
        query = query.filter_by(shop_id=int(shop_filter))
    
    # Фильтр по дате
    if date_from:
        query = query.filter(Order.date_of_order >= datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        query = query.filter(Order.date_of_order <= datetime.strptime(date_to, '%Y-%m-%d').date())
    
    orders = query.order_by(Order.date_of_order.desc()).all()
    
    # Получаем уникальные статусы и магазины для фильтров
    all_statuses = db.session.query(Order.status).distinct().all()
    statuses = [s[0] for s in all_statuses if s[0]]
    shops = Shop.query.all()
    
    return render_template('staff_orders.html', 
                         orders=orders,
                         statuses=statuses,
                         shops=shops,
                         status_filter=status_filter,
                         shop_filter=shop_filter,
                         date_from=date_from,
                         date_to=date_to)


@app.route('/staff/order/create', methods=['GET', 'POST'])
def staff_create_order():
    """Создание нового заказа сотрудником"""
    if request.method == 'POST':
        try:
            # Получаем или создаем клиента
            client_email = request.form['client_email']
            client = Client.query.filter_by(email=client_email).first()
            
            if not client:
                # Создаем нового клиента
                client = Client(
                    name=request.form['client_name'],
                    phone_number=request.form['client_phone'],
                    email=client_email
                )
                db.session.add(client)
                db.session.flush()
            
            # Создаем заказ
            order_number = generate_order_number()
            order = Order(
                order_number=order_number,
                client_id=client.id,
                shop_id=int(request.form['shop_id']) if request.form.get('shop_id') else None,
                date_of_order=date.today(),
                total_price=Decimal(request.form['total_price']),
                status=request.form.get('status', 'Новый')
            )
            
            db.session.add(order)
            db.session.flush()
            
            # Создаем чек
            receipt_number = generate_receipt_number()
            receipt = Receipt(
                receipt_number=receipt_number,
                date_oforder=date.today(),
                total_price=Decimal(request.form['total_price']),
                payment_method=request.form.get('payment_method', 'Не оплачен'),
                client_id=client.id,
                orders_id=order_number,
                shop_workerid=int(request.form['worker_id']) if request.form.get('worker_id') else None
            )
            
            db.session.add(receipt)
            db.session.commit()
            
            flash(f'Заказ {order_number} успешно создан!', 'success')
            return redirect(url_for('staff_edit_order', order_number=order_number))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании заказа: {str(e)}', 'danger')
            return redirect(url_for('staff_create_order'))
    
    # GET запрос - показываем форму
    shops = Shop.query.all()
    workers = Worker.query.all()
    clients = Client.query.all()
    
    return render_template('create_order.html',
                         shops=shops,
                         workers=workers,
                         clients=clients,
                         user_type='staff')


@app.route('/staff/order/<order_number>/edit', methods=['GET', 'POST'])
def staff_edit_order(order_number):
    """Редактирование заказа сотрудником (полные права)"""
    order = Order.query.get_or_404(order_number)
    
    if request.method == 'POST':
        try:
            # Обновление основной информации заказа
            order.shop_id = int(request.form['shop_id']) if request.form.get('shop_id') else None
            order.status = request.form['status']
            order.total_price = Decimal(request.form['total_price'])
            
            # Обновление чека
            if order.receipt:
                order.receipt.payment_method = request.form['payment_method']
                order.receipt.total_price = Decimal(request.form['total_price'])
                if request.form.get('worker_id'):
                    order.receipt.shop_workerid = int(request.form['worker_id'])
            
            db.session.commit()
            flash('Заказ успешно обновлен!', 'success')
            return redirect(url_for('staff_orders'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении заказа: {str(e)}', 'danger')
    
    shops = Shop.query.all()
    workers = Worker.query.all()
    ordered_items = order.ordered_goods.all()
    
    return render_template('edit_order.html',
                         order=order,
                         ordered_items=ordered_items,
                         shops=shops,
                         workers=workers,
                         user_type='staff',
                         editable=True)


@app.route('/staff/order/<order_number>/delete', methods=['POST'])
def staff_delete_order(order_number):
    """Удаление заказа сотрудником"""
    try:
        order = Order.query.get_or_404(order_number)
        
        # Удаляем связанный чек
        if order.receipt:
            db.session.delete(order.receipt)
        
        # Удаляем позиции заказа
        for item in order.ordered_goods:
            db.session.delete(item)
        
        db.session.delete(order)
        db.session.commit()
        flash('Заказ удален', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении заказа: {str(e)}', 'danger')
    
    return redirect(url_for('staff_orders'))


# ============ API для получения данных ============

@app.route('/api/clients/search')
def api_search_clients():
    """API для поиска клиентов"""
    query = request.args.get('q', '')
    if query:
        clients = Client.query.filter(
            (Client.name.ilike(f'%{query}%')) | 
            (Client.email.ilike(f'%{query}%')) |
            (Client.phone_number.ilike(f'%{query}%'))
        ).limit(10).all()
        
        return jsonify([{
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'phone': c.phone_number
        } for c in clients])
    return jsonify([])


@app.route('/api/goods/search')
def api_search_goods():
    """API для поиска товаров"""
    query = request.args.get('q', '')
    if query:
        goods = ListOfGoods.query.filter(
            ListOfGoods.name.ilike(f'%{query}%')
        ).limit(10).all()
        
        return jsonify([{
            'id': g.id,
            'name': g.name,
            'price': float(g.price) if g.price else 0
        } for g in goods])
    return jsonify([])


# ============ Обработка ошибок ============

@app.errorhandler(404)
def not_found(error):
    flash('Страница не найдена', 'warning')
    return redirect(url_for('index'))


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash('Внутренняя ошибка сервера', 'danger')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
