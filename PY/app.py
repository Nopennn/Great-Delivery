from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Del.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class Order(db.Model):
    __tablename__ = 'order_list'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(30), nullable=False)
    data_created = db.Column(db.DateTime, default=datetime.utcnow)
    data_arrived = db.Column(db.String(20), nullable=False)
    adress = db.Column(db.String(100), nullable=False)
    courier_id = db.Column(db.Integer, db.ForeignKey('courier_info.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer_info.id'))
    order_description = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return '<Order %r>' % self.id


class Customer(db.Model):
    __tablename__ = 'customer_info'
    id = db.Column(db.Integer, primary_key=True)
    FIO = db.Column(db.String(90), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    orders = db.relationship('Order', backref='customer')

    def __repr__(self):
        return '<Customer %r>' % self.id


class Courier(db.Model):
    __tablename__ = 'courier_info'
    id = db.Column(db.Integer, primary_key=True)
    FIO = db.Column(db.String(90), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    orders = db.relationship('Order', backref='courier')

    def __repr__(self):
        return '<Courier %r>' % self.id


@app.route('/')
def home():
    return render_template("GREATDelivery.html")



@app.route('/customer-registration', methods=['POST','GET'])
def cusregis():
    if request.method == "POST":
        fio = request.form['CustomerName']
        phone = request.form['CustomerPhone']
        pas1 = request.form['CustomerPW1']
        pas2 = request.form['CustomerPW2']
        if pas1 == pas2:
            cur = Customer(FIO=fio, phone_number=phone, password=pas1)
            try:
                db.session.add(cur)
                db.session.commit()
                return redirect(url_for('.cusprof', id=cur.id))
            except:
                return render_template("customer-registration.html", error="Ошибка записи в базу данных")
        else:
            return render_template("customer-registration.html", error="Пароли не совпадают")
    else:
        return render_template("customer-registration.html", error="")

@app.route('/customer-authorization', methods=['POST','GET'])
def cust_auth():
    if request.method == "POST":
        phone = request.form['CustomerPhone']
        pas1 = request.form['CustomerPW1']
        cust = db.session.query(Customer).filter_by(phone_number=phone).first()
        if isinstance(cust, Customer):
            pas2 = cust.password
            if pas1 == pas2:
                return redirect(url_for('.cusprof', id=cust.id))
            else:
                return render_template("customer-authorization.html", error="Неверный пароль")
        else:
            return render_template("customer-authorization.html", error="Пользователь не найден")
    else:
        return render_template("customer-authorization.html", error="")

@app.route('/customer-profile/<int:id>', methods=['POST','GET'])
def cusprof(id):
    if request.method == "POST":
        data_arrived = request.form['data_arrived']
        adress = request.form['adress']
        order_description = request.form['buy']
        customer = Customer.query.get(id)
        orders = customer.orders
        cur = Order(status="Не доставлен", data_arrived=data_arrived, adress=adress, order_description=order_description, customer=customer)
        try:
            db.session.add(cur)
            db.session.commit()
            return render_template("customer-profile.html", error="Заказ принят", id=id, orders=orders)
        except:
            return render_template("customer-profile.html", error="Ошибка записи в базу данных", id=id)
    else:
        customer = Customer.query.get(id)
        orders = customer.orders

        return render_template("customer-profile.html", error="", id=id, orders=orders)





@app.route('/courier-registration', methods=['POST','GET'])
def courregis():
    if request.method == "POST":
        fio = request.form['CourierName']
        phone = request.form['CourierPhone']
        pas1 = request.form['CourierPW1']
        pas2 = request.form['CourierPW2']
        if pas1 == pas2:
            cur = Courier(FIO=fio, phone_number=phone, password=pas1)
            try:
                db.session.add(cur)
                db.session.commit()
                return redirect(url_for('.courprof', id=cur.id))
            except:
                return render_template("courier-registration.html", error="Ошибка записи в базу данных")
        else:
            return render_template("courier-registration.html", error="Пароли не совпадают")
    else:
        return render_template("courier-registration.html", error="")

@app.route('/courier-authorization', methods=['POST','GET'])
def cour_auth():
    if request.method == "POST":
        phone = request.form['CourierPhone']
        pas1 = request.form['CourierPW1']
        cour = db.session.query(Courier).filter_by(phone_number=phone).first()
        if isinstance(cour, Courier):
            pas2 = cour.password
            if pas1 == pas2:
                return redirect(url_for('.courprof', id=cour.id))
            else:
                return render_template("courier-authorization.html", error="Неверный пароль")
        else:
            return render_template("courier-authorization.html", error="Пользователь не найден")
    else:
        return render_template("courier-authorization.html", error="")

@app.route('/courier-profile/<int:id>', methods=['GET'])
def courprof(id):
    cour = Courier.query.get(id)
    orders = cour.orders
    return render_template("courier-profile.html", error="", id=id, orders=orders)

@app.route('/courier-profile/<int:id>/order_get', methods=['GET'])
def order_get(id):
    order = Order.query.filter_by(status="Не доставлен").first()
    cour = Courier.query.get(id)
    order.courier = cour
    order.courier_id = id
    order.status = "Взят курьером"
    try:
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('.courprof', id=id))
    except:
        return render_template("courier-profile.html", error="Ошибка записи в бд", id=id, orders=cour.orders)

@app.route('/courier-profile/<int:order_id>/order_close', methods=['GET'])
def order_close(order_id):
    order = Order.query.get(order_id)
    order.status = "Доставлен"
    cour = order.courier
    try:
        db.session.add(order)
        db.session.commit()
        return redirect(url_for('.courprof', id=order.courier_id))
    except:
        return render_template("courier-profile.html", error="Ошибка закрытия заказа", id=order.courier_id, orders=cour.orders)
    return
if __name__ == "__main__":
    app.run(debug=True)