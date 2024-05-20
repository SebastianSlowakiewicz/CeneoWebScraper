from app import app
from flask import render_template

@app.route('/')
def index():
    return render_template('index.html.jinja')
@app.route('/extract')
def extract():
    return render_template('extract.html.jinja')
@app.route('/products')
def products():
    return render_template('products.html.jinja')
@app.route('/about')
def about():
    return render_template('about.html.jinja')
@app.route('/product/product_id')
def product():
    return render_template('product.html.jinja')

