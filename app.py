import datetime
import uuid
import itertools
import operator

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import Flask, render_template, request, redirect, session, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from email_sender import email_sender


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# admin = Admin(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(100), nullable=True)
    img = db.Column(db.Text, nullable=True)
    name = db.Column(db.Text, nullable=True)
    mimetype = db.Column(db.Text, nullable=True)

    isActive = db.Column(db.Boolean, default=True)


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=True)
    auth3rt = db.Column(db.String, nullable=True)
    cdate = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    customer_email = db.Column(db.String, nullable=False)
    purchase_id = db.Column(db.String, nullable=True)
    good_id = db.Column(db.String, nullable=True)
    price = db.Column(db.Integer, nullable=True)
    count = db.Column(db.Integer, nullable=True)
    cdate = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# admin.add_view(ModelView(Item, db.session))
# admin.add_view(ModelView(Customer, db.session))
# admin.add_view(ModelView(Purchase, db.session))


# db.create_all()

# data = []
# data.append(Customer(
#         firstname="Ivan",
#         lastname="Ivanov",
#         email='test@test.com',
#         password="strictly_secret"
#     ))
#
# db.session.add_all(data)
# db.session.commit()


@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    try:
        cart_counter = []
        for i in session['cart_item']:
            cart_counter.append(dict(id=i['id'], count=i['count']))

        button_visible = [i['id'] for i in session['cart_item']]

        try:
            auth_email = session['auth_email'][0]['email']
            return render_template('index.html', data=items, cart_counter=cart_counter, auth_email=auth_email, button_visible=button_visible)
        except:
            return render_template('index.html', data=items, cart_counter=cart_counter, button_visible=button_visible)

    except:
        try:
            auth_email = session['auth_email'][0]['email']
            return render_template('index.html', data=items, auth_email=auth_email)
        except:
            return render_template('index.html', data=items)


@app.route('/about')
def about():
    items = Item.query.order_by(Item.price).all()
    try:
        cart_counter = []
        for i in session['cart_item']:
            cart_counter.append(dict(id=i['id'], count=i['count']))

        button_visible = [i['id'] for i in session['cart_item']]

        try:
            auth_email = session['auth_email'][0]['email']
            return render_template('about.html', data=items, cart_counter=cart_counter, auth_email=auth_email, button_visible=button_visible)
        except:
            return render_template('about.html', data=items, cart_counter=cart_counter, button_visible=button_visible)

    except:
        try:
            auth_email = session['auth_email'][0]['email']
            return render_template('about.html', data=items, auth_email=auth_email)
        except:
            return render_template('about.html', data=items)


@app.route('/shop-list')
def test_payments():
    items = Item.query.order_by(Item.price).all()
    return render_template('shop-list.html', data=items)


@app.route('/to-cart/<int:id>')
def add_product_to_cart_t(id):

    data = []

    try:
        for i in session['cart_item']:
            data.append({'id': i['id'], 'count': 1})

        data.append({'id': id, 'count': 1})
    except:
        data.append({'id': id, 'count': 1})

    cart_item = data
    session['cart_item'] = cart_item

    return redirect('/')


@app.route('/add-count/<int:id>/<int:count>')
def add_quantity(id, count):

    data = session['cart_item']
    for i in data:
        if i['id'] == id:
            i['count'] = count

    session['cart_item'] = data

    return redirect('/cart')


@app.route('/out-cart/<int:id>')
def product_leaves_cart(id):

    if len(session['cart_item']) == 1:
        return redirect('/delete-cart/')
    else:
        data = []
        for i in session['cart_item']:
            if i['id'] == id:
                pass
            else:
                data.append(i)

        session['cart_item'] = data

        return redirect('/cart')


@app.route('/cart/')
def cart():

    try:
        cart_counter = []

        for i in session['cart_item']:
            cart_counter.append(dict(id=i['id'], count=i['count']))

        cart_item = [i['id'] for i in session['cart_item']]

        data_set = Item.query.filter(Item.id.in_(cart_item)).all()
        try:
            auth_email = session['auth_email'][0]['email']
            cart_product = []
            for i in data_set:
                cart_product.append(dict(id=i.id, price=i.price))

            data = []
            for i in cart_product:
                for j in cart_counter:
                    if i['id'] == j['id']:
                        data.append(i['price'] * j['count'])
            product_sum = sum(data)
            product_sum_formated = '{0:,}'.format(int(product_sum)).replace(',', ' ')

            return render_template('cart.html', data=data_set, cart_counter=cart_counter, auth_email=auth_email, product_sum_formated=product_sum_formated)
        except:

            cart_product = []
            for i in data_set:
                cart_product.append(dict(id=i.id, price=i.price))

            data = []
            for i in cart_product:
                for j in cart_counter:
                    if i['id'] == j['id']:
                        data.append(i['price'] * j['count'])
            product_sum = sum(data)
            product_sum_formated = '{0:,}'.format(int(product_sum)).replace(',', ' ')
            return render_template('cart.html', data=data_set, cart_counter=cart_counter, product_sum_formated=product_sum_formated)

    except:
        try:
            auth_email = session['auth_email'][0]['email']
            return render_template('cart.html', auth_email=auth_email)
        except:
            return render_template('cart.html')


@app.route('/img/<int:id>')
def get_img(id):
    img = Item.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)


@app.route('/pay_mock/', methods=['GET'])
def pay_mock():

    items = session['cart_item'][0]['id']
    data_set = Item.query.filter(Item.id.in_(items)).all()

    data = []
    for i in data_set:
        data.append(dict(title=i.title, price=i.price, description=i.description))

    return render_template('pay_mock.html', data=data_set)


@app.route('/mock_result/', methods=['GET'])
def mock_result():
    return render_template('mock_result.html')


@app.route('/delete-cart/')
def delete_cart():
    session.pop('cart_item', None)
    return redirect('/')


@app.route('/delete-auth/')
def delete_auth():
    session.pop('auth_email', None)
    return redirect('/')


@app.route('/signin', methods=['POST', 'GET'])
def sign_in():
    if request.method == "POST":
        email = request.form['email']
        print(email)
        password = request.form['password']
        print(password)
        query_email = Customer.query.filter(Customer.email == email).all()

        data = []
        for i in query_email:
            data.append(dict(email=i.email, password=i.password))
        if data:

            if data[0]["email"] == email and data[0]["password"] == password:
                auth_email = [{'email': email}]
                session['auth_email'] = auth_email

                return redirect('/orders')

            else:
                return "ты не авторизован"
        else:
            return "остынь парниш :) таких нет..."

    else:
        return render_template('signin.html')


@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    if request.method == "POST":
        firstname = request.form['lastname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        country = request.form['country']
        city = request.form['city']
        postalcode = request.form['postalcode']
        address = request.form['address']
        address2 = request.form['address2']

        items = session['cart_item'][0]['id']
        data_set = Item.query.filter(Item.id.in_(items)).all()

        data = []
        for i in data_set:
            data.append(dict(title=i.title, price=i.price, description=i.description))

        message = render_template('email_order.html', data=data_set, email=email)
        email_sender(email, message)


        purchase_id = str(uuid.uuid4())

        for i in data_set:
            purchase = Purchase(customer_email=email, purchase_id=purchase_id, good_id=i.id, price=i.price, count=1)
            db.session.add(purchase)
            db.session.commit()

        return redirect('/pay_mock/')


    items = session['cart_item'][0]['id']
    data_set = Item.query.filter(Item.id.in_(items)).all()
    return render_template('checkout.html', data=data_set)


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        pic = request.files['pic']
        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype
        if not filename or not mimetype:
            return 'Bad upload!', 400

        item = Item(title=title, price=price, description=description, img=pic.read(), name=filename, mimetype=mimetype)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/shop-list')
        except:
            return "Получилась ошибка"
    else:
        return render_template('create.html')


@app.route('/posts/<int:id>')
def posts_detail(id):
    item = Item.query.get(id)
    return render_template("posts_detail.html", item=item)


@app.route('/posts/<int:id>/delete')
def posts_delete(id):
    item = Item.query.get_or_404(id)

    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/shop-list')
    except:
        return "При удалении статьи произошла ошибка"


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    item = Item.query.get(id)
    if request.method == "POST":
        item.title = request.form['title']
        item.description = request.form['description']
        item.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/shop-list')
        except:
            return "При редактировании статьи произошла ошибка"

    else:
        return render_template("posts_update.html", item=item)


@app.route('/orders')
def get_orders():
    try:
        cart_counter = []
        for i in session['cart_item']:
            cart_counter.append(dict(id=i['id'], count=i['count']))
        try:
            auth_email = session['auth_email'][0]['email']
            query_order = Purchase.query.filter(Purchase.customer_email == auth_email).all()
            orders=[]
            for i in query_order:
                orders.append(dict(purchase_id=i.purchase_id, good_id=i.good_id, price=i.price, count=i.count, cdate=i.cdate))

            def groupid_purchase(d):
                del d['purchase_id']
                return d

            data = [{'purchase_id': i, 'data': list(map(groupid_purchase, grp))} for i, grp in itertools.groupby(orders, operator.itemgetter('purchase_id'))]

            date = data[0]['data'][0]['cdate']
            date = str(date)[:-10]

            return render_template("orders.html", data=data, date=date, auth_email=auth_email, cart_counter=cart_counter)

        except:
            return render_template('orders.html', cart_counter=cart_counter)

    except:
        try:
            auth_email = session['auth_email'][0]['email']
            query_order = Purchase.query.filter(Purchase.customer_email == auth_email).all()
            orders = []
            for i in query_order:
                orders.append(
                    dict(purchase_id=i.purchase_id, good_id=i.good_id, price=i.price, count=i.count, cdate=i.cdate))

            def groupid_purchase(d):
                del d['purchase_id']
                return d

            data = [{'purchase_id': i, 'data': list(map(groupid_purchase, grp))} for i, grp in
                    itertools.groupby(orders, operator.itemgetter('purchase_id'))]

            date = data[0]['data'][0]['cdate']
            date = str(date)[:-10]

            return render_template("orders.html", data=data, date=date, auth_email=auth_email)
        except:
            return render_template("orders.html", memo='memo')


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run()