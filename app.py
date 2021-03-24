import datetime

from flask import Flask, render_template, request, redirect, session, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import uuid
from email_sender import email_sender
import itertools
import operator

#from cloudipsp import Api, Checkout

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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


db.create_all()

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
        cart_counter = session['cart_item'][0]['id']
        cart_counter = list(set(cart_counter))
        try:
            auth_email = session['auth_email'][0]['email']
            a = session['cart_item']
            print(a)
            return render_template('index.html', data=items, cart_counter=cart_counter, auth_email=auth_email)
        except:
            return render_template('index.html', data=items, cart_counter=cart_counter)

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
        cart_counter = session['cart_item'][0]['id']
        cart_counter = list(set(cart_counter))
        try:
            auth_email = session['auth_email'][0]['email']
            return render_template('about.html', data=items, cart_counter=cart_counter, auth_email=auth_email)
        except:
            return render_template('about.html', data=items, cart_counter=cart_counter)

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
def add_product_to_cart(id):

    data = []
    try:
        for i in session['cart_item'][0]['id']:
            data.append(i)
            data.append(id)
    except:
        data.append(id)

    cart_item = [{'id': data}]
    session['cart_item'] = cart_item

    return redirect('/')


@app.route('/to-cart-t/<int:id>')
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
    print(session)

    return redirect('/')


@app.route('/out-cart/<int:id>')
def product_leaves_cart(id):

    data = []
    for i in session['cart_item'][0]['id']:
        data.append(i)

    data = list(set(data))
    data.remove(id)
    if len(data) < 1:
        return redirect('/delete-cart/')
    else:
        cart_item = [{'id': data}]
        session['cart_item'] = cart_item
        return redirect('/cart')


@app.route('/cart/')
def cart():

    try:
        items = session['cart_item'][0]['id']
        items = list(set(items))
        data_set = Item.query.filter(Item.id.in_(items)).all()
        try:
            auth_email = session['auth_email'][0]['email']
            return render_template('cart.html', data=data_set, cart_counter=items, auth_email=auth_email)
        except:
            return render_template('cart.html', data=data_set, cart_counter=items)

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

# @app.route('/pay/<int:id>')
# def item_pay(id):
#     item = Item.query.get(id)
#     title = str(item.title)
#     amount = str(item.price)
#     orderId = "https://sandbox3.payture.com/apim/Init?Key=Merchant&Data=SessionType%3DPay%3BOrderId%3D" + str(
#         uuid.uuid4()) + "%3BProduct%3D" + title + "%3BTotal%3D" + amount + "%3BAmount%3D" + amount + "00"
#     xml_string = requests.get(orderId)
#     soup = BeautifulSoup(str(xml_string.text), 'xml')
#     tag = soup.Init
#     url = "https://sandbox3.payture.com/apim/Pay?SessionId=" + tag['SessionId']
#
#     return redirect(url)
#
#
# @app.route('/buy/<int:id>')
# def item_buy(id):
#     item = Item.query.get(id)
#
#     api = Api(merchant_id=1396424,
#               secret_key='test')
#     checkout = Checkout(api=api)
#     data = {
#         "currency": "RUB",
#         "amount": str(item.price) + "00"
#     }
#     url = checkout.url(data).get('checkout_url')
#     return redirect(url)


@app.route('/signin', methods=['POST', 'GET'])
def sign_in():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        query_email = Customer.query.filter(Customer.email == email).all()

        data = []
        for i in query_email:
            data.append(dict(email=i.email, password=i.password))

        if data[0]["email"] == email and data[0]["password"] == password:
            auth_email = [{'email': email}]
            session['auth_email'] = auth_email

            return redirect('/orders')
        else:
            return "ты не авторизован"
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
        cart_counter = session['cart_item'][0]['id']
        cart_counter = list(set(cart_counter))
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
            print(data)
            date = data[0]['data'][0]['cdate']
            date = str(date)[:-10]
            print(date)

            return render_template("orders.html", data=data, date=date, auth_email=auth_email, cart_counter=cart_counter)

        except:
            return render_template('orders.html', data=data, cart_counter=cart_counter)


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
            print(data)
            date = data[0]['data'][0]['cdate']
            date = str(date)[:-10]
            print(date)

            return render_template("orders.html", data=data, date=date, auth_email=auth_email)
        except:
            memo = 'memo'
            return render_template("orders.html", memo='memo')


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run(debug=True)