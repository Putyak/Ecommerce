from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
import requests
from email_sender import email_sender
import uuid
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

    isActive = db.Column(db.Boolean, default=True)


@app.route('/')
def index():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)


@app.route('/about')
def about():
    return render_template('about.html')


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

    return redirect('/cart')


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


@app.route('/test/')
def test():
    id = session['cart_item'][0]['id']
    print(session['cart_item'][0]['id'])

    return str(id)


@app.route('/cart/')
def cart():

    try:
        items = session['cart_item'][0]['id']
        data_set = Item.query.filter(Item.id.in_(items)).all()
        return render_template('cart.html', data=data_set)
    except:
        return render_template('cart.html')


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
        if email == 'admin@test.com' and password == '123':
            return redirect('/shop-list')
        else:
            return ('ты не авторизован -_-')
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

        message = 'Name: ' + firstname + '\n' + 'Last name:' + lastname + '\n' + 'User name: ' + username + '\n' + 'Products: ' + str(data)
        email_sender(email, message)

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

        item = Item(title=title, price=price, description=description)

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


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == "__main__":
    app.run()