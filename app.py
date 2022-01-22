import datetime
import uuid
import itertools
import operator
import stripe

from flask import Flask, render_template, request, redirect, session, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from email_sender import email_sender
from configparser import ConfigParser


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
    role = db.Column(db.String, nullable=True)
    cdate = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    customer_email = db.Column(db.String, nullable=False)
    purchase_id = db.Column(db.String, nullable=True)
    product_id = db.Column(db.String, nullable=True)
    product_name = db.Column(db.String, nullable=True)
    product_description = db.Column(db.String, nullable=True)
    price = db.Column(db.Integer, nullable=True)
    count = db.Column(db.Integer, nullable=True)
    cdate = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Billing(db.Model):
    __tablename__ = 'billing'
    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.String(100), nullable=False)
    sessionId = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), nullable=True)
    currency_code = db.Column(db.String(3), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# admin.add_view(ModelView(Item, db.session))
# admin.add_view(ModelView(Customer, db.session))
# admin.add_view(ModelView(Purchase, db.session))

#db.create_all()

# data = []
# data.append(Customer(
#         firstname="Ivan",
#         lastname="Ivanov",
#         email='test@test.com',
#         password="test123"
#     ))
#
# db.session.add_all(data)
# db.session.commit()


file = 'config_dev.ini'
config = ConfigParser()
config.read(file)


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


@app.route('/test')
def test():
    items = Item.query.order_by(Item.price).all()
    try:
        cart_counter = []
        for i in session['cart_item']:
            cart_counter.append(dict(id=i['id'], count=i['count']))

        button_visible = [i['id'] for i in session['cart_item']]

        try:
            auth_email = session['auth_email'][0]['email']
            return render_template('index_old.html', data=items, cart_counter=cart_counter, auth_email=auth_email, button_visible=button_visible)
        except:
            return render_template('index_old.html', data=items, cart_counter=cart_counter, button_visible=button_visible)

    except:
        try:
            auth_email = session['auth_email'][0]['email']
            return render_template('index_old.html', data=items, auth_email=auth_email)
        except:
            return render_template('index_old.html', data=items)


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
    #
    # items = session['cart_item'][0]['id']
    # data_set = Item.query.filter(Item.id.in_(items)).all()
    #
    # data = []
    # for i in data_set:
    #     data.append(dict(title=i.title, price=i.price, description=i.description))

    return render_template('pay_mock.html')


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


@app.route('/delete-admin-auth/')
def delete_admin_auth():
    session.pop('auth_admin', None)
    return redirect('/')


@app.route('/signin', methods=['POST', 'GET'])
def sign_in():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        query_email = Customer.query.filter(Customer.email == email).all()

        data = []
        for i in query_email:
            data.append(dict(email=i.email, password=i.password, role=i.role))
        if data:

            if data[0]["email"] == email and data[0]["password"] == password and data[0]["role"] == "admin":
                auth_admin = [{'email': email}]
                session['auth_admin'] = auth_admin

                return redirect('/admin/dashboard')

            elif data[0]["email"] == email and data[0]["password"] == password:
                auth_email = [{'email': email}]
                session['auth_email'] = auth_email

                return redirect('/orders')

            else:
                return "ты не авторизован"
        else:
            return "остынь парниш :) таких нет..."

    else:
        return render_template('signin.html')


@app.route('/signin_link/<string:email>/<string:password>', methods=['GET'])
def sign_in_link(email, password):
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


@app.route('/checkout', methods=['POST', 'GET'])
def checkout_cart():
    cart_counter = []
    for i in session['cart_item']:
        cart_counter.append(dict(id=i['id'], count=i['count']))


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

        items = [i['id'] for i in session['cart_item']]
        data_set = Item.query.filter(Item.id.in_(items)).all()

        data = []
        for i in data_set:
            data.append(dict(id=i.id, title=i.title, price=i.price, description=i.description))

        purchase_id = str(uuid.uuid4())

        purchase = []
        for i in data:
            for j in cart_counter:
                if i['id'] == j['id']:
                    purchase.append(dict(customer_email=email, purchase_id=purchase_id, product_id=i['id'], product_name=i['title'], product_description=i['description'], price=i['price'], count=j['count']))

        email_order = []
        for i in purchase:
            email_order.append(dict(customer_email=email, purchase_id=purchase_id, product_id=i['product_id'], product_name=i['product_name'], product_description=i['product_description'], price=i['price'], count=i['count']))
            purchase = Purchase(customer_email=email, purchase_id=purchase_id, product_id=i['product_id'], product_name=i['product_name'], product_description=i['product_description'], price=i['price'], count=i['count'])
            db.session.add(purchase)
            db.session.commit()

        cart_product = []
        for i in data_set:
            cart_product.append(dict(id=i.id, price=i.price))

        data_sum = []
        for i in cart_product:
            for j in cart_counter:
                if i['id'] == j['id']:
                    data_sum.append(i['price'] * j['count'])
        product_sum = sum(data_sum)
        product_sum_formated = '{0:,}'.format(int(product_sum)).replace(',', ' ')

        customer = Customer(firstname='customer', email=email, password='0123')

        try:
            db.session.add(customer)
            db.session.commit()
        except:
            pass

        try:
            message = render_template('email_order.html', data=email_order, total=product_sum_formated, email=email)
            email_sender(email, message)
        except:
            pass

        url = '/stripe/' + purchase_id + '/' + 'OrderId: ' + purchase_id + '/' + str(product_sum) + '00'

        try:
            session.pop('purchase_id', None)
            session['purchase_id'] = [{'purchase_id': purchase_id}]
        except:
            session['purchase_id'] = [{'purchase_id': purchase_id}]

        return redirect(url)

    items = [i['id'] for i in session['cart_item']]
    data_set = Item.query.filter(Item.id.in_(items)).all()

    cart_product = []
    for i in data_set:
        cart_product.append(dict(id=i.id, price=i.price))

    data_sum = []
    for i in cart_product:
        for j in cart_counter:
            if i['id'] == j['id']:
                data_sum.append(i['price'] * j['count'])
    product_sum = sum(data_sum)
    product_sum_formated = '{0:,}'.format(int(product_sum)).replace(',', ' ')

    return render_template('checkout_cart.html', data=data_set, cart_counter=cart_counter, product_sum_formated=product_sum_formated)


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

            orders = []
            for i in query_order:
                orders.append(dict(purchase_id=i.purchase_id, product_id=i.product_id, product_name=i.product_name, product_description=i.product_description, price=i.price, count=i.count, cdate=i.cdate))

            def groupid_purchase(d):
                del d['purchase_id']
                return d

            data = [{'purchase_id': i, 'data': list(map(groupid_purchase, grp))} for i, grp in itertools.groupby(orders, operator.itemgetter('purchase_id'))]

            cdate = []
            for p_time in data:
                date = []
                for data_time in p_time['data']:
                    datat_t = str(data_time['cdate'])
                    date.append(datat_t[:-10])
                cdate.append(dict(purchase_id=p_time['purchase_id'], cdate=date[0]))

            p_total = []
            for purchase in data:
                p_total_sum = []
                for p_summ in purchase['data']:
                    p_total_sum.append(p_summ['price'] * p_summ['count'])

                s_total = sum(p_total_sum)
                p_total.append(dict(purchase_id=purchase['purchase_id'], total=s_total))

            return render_template("orders.html", data=data, date=cdate, auth_email=auth_email, cart_counter=cart_counter, total=p_total)

        except:
            return render_template('orders.html', cart_counter=cart_counter)

    except:
        try:
            auth_email = session['auth_email'][0]['email']
            query_order = Purchase.query.filter(Purchase.customer_email == auth_email).all()
            orders = []
            for i in query_order:
                orders.append(
                    dict(purchase_id=i.purchase_id, product_id=i.product_id, product_name=i.product_name, product_description=i.product_description, price=i.price, count=i.count, cdate=i.cdate))

            def groupid_purchase(d):
                del d['purchase_id']
                return d

            data = [{'purchase_id': i, 'data': list(map(groupid_purchase, grp))} for i, grp in
                    itertools.groupby(orders, operator.itemgetter('purchase_id'))]

            cdate=[]
            for p_time in data:
                date = []
                for data_time in p_time['data']:
                    datat_t = str(data_time['cdate'])
                    date.append(datat_t[:-10])
                cdate.append(dict(purchase_id=p_time['purchase_id'], cdate=date[0]))

            p_total = []
            for purchase in data:
                p_total_sum = []
                for p_summ in purchase['data']:
                    p_total_sum.append(p_summ['price'] * p_summ['count'])

                s_total = sum(p_total_sum)
                p_total.append(dict(purchase_id=purchase['purchase_id'], total=s_total))

            return render_template("orders.html", data=data, date=cdate, auth_email=auth_email, total=p_total)
        except:
            return render_template("orders.html", memo='memo')


@app.route('/admin/dashboard')
def admin_dashboard():

    try:
        session['auth_admin']
        return render_template('admin_dashboard.html')

    except:
        return render_template('admin_dashboard.html', memo='memo')


@app.route('/admin/orders')
def admin_orders():
    try:
        session['auth_admin']
        query_orders = Purchase.query.all()
        orders = []
        for i in query_orders:
            orders.append(dict(id=i.id, customer_email=i.customer_email, purchase_id=i.purchase_id, product_id=i.product_id, product_name=i.product_name,
                               product_description=i.product_description, price=i.price, count=i.count, cdate=i.cdate))

        sample_query = db.session.query(Purchase.purchase_id).distinct().all()
        unique_purchase_id = [i[0] for i in sample_query]

        order_data = []
        for j in orders:
            for f in unique_purchase_id:
                if f == j['purchase_id']:
                    order_data.append(dict(purchase_id=j['purchase_id'], customer_email=j['customer_email'], cdate=j['cdate']))
                else:
                    pass

        return render_template('admin_orders.html', orders=order_data)
    except:
        return render_template('admin_dashboard.html', memo='memo')


@app.route('/admin/orders/details/<string:purchase_id>')
def admin_orders_details(purchase_id):
    try:
        session['auth_admin']
        query_orders = Purchase.query.filter(Purchase.purchase_id == purchase_id).all()
        orders_details = []
        for i in query_orders:
            orders_details.append(dict(id=i.id, customer_email=i.customer_email, purchase_id=i.purchase_id, product_id=i.product_id, product_name=i.product_name,
                               product_description=i.product_description, price=i.price, count=i.count, cdate=i.cdate))

        return render_template('admin_orders_details.html', orders_details=orders_details)
    except:
        return render_template('admin_dashboard.html', memo='memo')


@app.route('/admin/products', methods=['POST', 'GET'])
def admin_products():
    try:
        session['auth_admin']
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
                return redirect('/admin/products')
            except:
                return "Получилась ошибка"
        else:
            query_products = Item.query.all()
            products = []
            for i in query_products:
                products.append(dict(id=i.id, title=i.title, price=i.price, description=i.description, img=i.img, name=i.name, mimetype=i.mimetype, isActive=i.isActive))
            return render_template('admin_products.html', products=products)
    except:
        return render_template('admin_dashboard.html', memo='memo')


@app.route('/admin/customers')
def admin_customers():
    try:
        session['auth_admin']
        query_customers = Customer.query.all()
        customers = []
        for i in query_customers:
            customers.append(dict(id=i.id, firstname=i.firstname, email=i.email, password=i.password, auth3rt=i.auth3rt, role=i.role, cdate=i.cdate))
        return render_template('admin_customers.html', customers=customers)
    except:
        return render_template('admin_dashboard.html', memo='memo')


@app.route('/admin/customers/purchase/<string:email>')
def admin_customers_purchase(email):
    try:
        session['auth_admin']
        query_order = Purchase.query.filter(Purchase.customer_email == email).all()
        orders = []
        for i in query_order:
            orders.append(
                dict(purchase_id=i.purchase_id, product_id=i.product_id, product_name=i.product_name,
                     product_description=i.product_description, price=i.price, count=i.count, cdate=i.cdate))

        def groupid_purchase(d):
            del d['purchase_id']
            return d

        data = [{'purchase_id': i, 'data': list(map(groupid_purchase, grp))} for i, grp in
                itertools.groupby(orders, operator.itemgetter('purchase_id'))]

        cdate = []
        for p_time in data:
            date = []
            for data_time in p_time['data']:
                datat_t = str(data_time['cdate'])
                date.append(datat_t[:-10])
            cdate.append(dict(purchase_id=p_time['purchase_id'], cdate=date[0]))

        p_total = []
        for purchase in data:
            p_total_sum = []
            for p_summ in purchase['data']:
                p_total_sum.append(p_summ['price'] * p_summ['count'])

            s_total = sum(p_total_sum)
            p_total.append(dict(purchase_id=purchase['purchase_id'], total=s_total))

        return render_template("admin_customers_orders.html", data=data, date=cdate, total=p_total)
    except:
        return render_template('admin_dashboard.html', memo='memo')


DOMAIN = config['url']['DOMAIN']


@app.route('/stripe/<purchase_id>/<description>/<amount>', methods=['GET'])
def payment_page(purchase_id, description, amount):
    return render_template('checkout.html', purchase_id=purchase_id, description=description, amount=amount)


@app.route('/stripe/create-checkout-session/<purchase_id>/<description>/<amount>', methods=['GET'])
def create_checkout_session(purchase_id, description, amount):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': amount,
                        'product_data': {
                            'name': description,
                            #'images': ['https://i.imgur.com/EHyR2nP.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=DOMAIN + '/stripe/success',
            cancel_url=DOMAIN + '/stripe/cancel',
        )
        item = Billing(purchase_id=purchase_id, sessionId=checkout_session.id, status='Pending', currency_code='USD', amount=amount[:-2], description=description)
        db.session.add(item)
        db.session.commit()
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403


@app.route('/stripe/status/<sessionId>', methods=['GET'])
def check_status_session(sessionId):
    payment_status = stripe.checkout.Session.retrieve(sessionId)
    return jsonify({'sessionId': sessionId, 'payment_status': payment_status.payment_status})


@app.route('/stripe/cancel', methods=['GET'])
def cancel():
    return render_template('cancel.html')


@app.route('/stripe/success', methods=['GET'])
def success():
    purchase_id = []
    for i in session['purchase_id']:
        purchase_id.append(dict(purchase_id=i['purchase_id']))

    bill = Billing.query.filter_by(purchase_id=purchase_id[0]['purchase_id']).first()
    bill_status = db.session.query(Billing).filter_by(purchase_id=purchase_id[0]['purchase_id']).all()
    sessionId = []
    for i in bill_status:
        sessionId.append(dict(sessionId=i.sessionId))

    payment = stripe.checkout.Session.retrieve(sessionId[0]['sessionId'])
    payment_status = payment.payment_status
    bill.status = payment_status
    db.session.commit()
    if payment_status == 'paid':
        customer_orders = db.session.query(Purchase).filter_by(purchase_id=purchase_id[0]['purchase_id']).all()
        customer_email = []
        for i in customer_orders:
            customer_email.append(dict(customer_email=i.customer_email))
        session['auth_email'] = [{'email': customer_email[0]['customer_email']}]
        session.pop('cart_item', None)
        session.pop('purchase_id', None)
        return render_template('success.html')
    else:
        return render_template('cancel.html')


stripe.api_key = config['key']['stripe']
app.secret_key = config['key']['app']


if __name__ == "__main__":
    app.run()