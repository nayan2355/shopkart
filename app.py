from flask import Flask, render_template, session, redirect, request
import sqlite3, os

app = Flask(__name__)
app.secret_key = 'shopkart_secret_123'

def init_db():
    conn = sqlite3.connect('products.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, price INTEGER, image TEXT)')
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        data = [
            ('iPhone 15 - 128GB', 70999, 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=300'),
            ('MacBook Air M2', 95999, 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=300'),
            ('Sony Headphone', 26990, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300'),
            ('Apple Watch S9', 41900, 'https://images.unsplash.com/photo-1555421689-3f034debb7a6?w=300')
        ]
        c.executemany("INSERT INTO products (name, price, image) VALUES (?,?,?)", data)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    cart_count = len(session.get('cart', []))
    return render_template('index.html', products=products, cart_count=cart_count)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', [])
    cart.append(product_id)
    session['cart'] = cart
    return redirect('/')

@app.route('/cart')
def cart():
    cart_ids = session.get('cart', [])
    if not cart_ids:
        return render_template('cart.html', products=[], total=0)

    conn = sqlite3.connect('products.db')
    conn.row_factory = sqlite3.Row
    placeholders = ','.join('?'*len(cart_ids))
    products = conn.execute(f"SELECT * FROM products WHERE id IN ({placeholders})", cart_ids).fetchall()
    conn.close()
    total = sum([p['price'] for p in products])
    return render_template('cart.html', products=products, total=total)

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []
    return redirect('/cart')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)