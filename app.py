from flask import Flask, render_template, request, redirect, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = "goldify123"

DATABASE = 'products.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/login', methods=['GET','POST'])
def login():
    return render_template('login.html')

@app.route('/set_login')
def set_login():
    phone = request.args.get('phone')
    if phone:
        session['logged_in'] = True
        session['phone'] = phone
        if 'cart' not in session:
            session['cart'] = []
    return redirect('/')

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect('/login')
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    prod_list = [{'id':p['id'],'name':p['name'],'price':p['price'],'image':p['image']} for p in products]
    return render_template('index.html', products=prod_list, cart_count=len(session.get('cart',[])))

@app.route('/add_to_cart/<int:pid>')
def add_to_cart(pid):
    if not session.get('logged_in'):
        return redirect('/login')
    cart = session.get('cart', [])
    cart.append(pid)
    session['cart'] = cart
    return redirect('/')

@app.route('/cart')
def cart():
    if not session.get('logged_in'):
        return redirect('/login')
    cart_ids = session.get('cart', [])
    db = get_db()
    products = []
    total = 0
    for pid in cart_ids:
        p = db.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
        if p:
            products.append({'name':p['name'],'price':p['price'],'image':p['image']})
            total += p['price']
    return render_template('cart.html', products=products, total=total)

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []
    return redirect('/cart')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)