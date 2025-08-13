from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB Connection
client = MongoClient('mongodb+srv://abishekuser:abishek.p@cluster1.dwlvyto.mongodb.net/')
db = client['bookstore']
books_collection = db['books']
orders_collection = db['orders']

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/browse')
def browse():
    books = list(books_collection.find())
    return render_template('browse.html', books=books)

@app.route('/add_to_cart/<book_id>')
def add_to_cart(book_id):
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(book_id)
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_books = [books_collection.find_one({'_id': ObjectId(book_id)}) for book_id in session.get('cart', [])]
    return render_template('cart.html', cart_books=cart_books)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'cart' in session and session['cart']:
        order = {'books': session['cart'], 'date': '2025-08-12', 'status': 'pending'}
        orders_collection.insert_one(order)
        session.pop('cart', None)
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    books = list(books_collection.find())
    orders = list(orders_collection.find())
    daily_sales = orders_collection.count_documents({'date': '2025-08-12'})
    weekly_sales = orders_collection.count_documents({'date': {'$gte': '2025-08-05'}})
    return render_template('admin.html', books=books, orders=orders, daily_sales=daily_sales, weekly_sales=weekly_sales)

@app.route('/add_book', methods=['POST'])
def add_book():
    book = {'title': request.form['title'], 'price': float(request.form['price'])}
    books_collection.insert_one(book)
    return redirect(url_for('admin'))

@app.route('/edit_book/<book_id>', methods=['POST'])
def edit_book(book_id):
    books_collection.update_one({'_id': ObjectId(book_id)}, {'$set': {'title': request.form['title'], 'price': float(request.form['price'])}})
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)