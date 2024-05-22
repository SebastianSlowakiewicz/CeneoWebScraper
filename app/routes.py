from app import app
from flask import render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup

@app.route('/')
def index():
    return render_template('index.html.jinja')
@app.route('/extract', methods=['POST', 'GET'])
def extract():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        #walidacja
        url = f"https://www.ceneo.pl/{product_id}"
        response = requests.get(url)
        print(product_id)
        if response.status_code == requests.codes['ok']:
            page = BeautifulSoup(response.text, "html.parser")
            opinions_count = page.select_one("a.product-review__link > span")
            if opinions_count:
            #ekstrakcja
                return redirect(url_for('product', product_id=product_id))
            return render_template('extract.html.jinja', error="Produkt o podanym kodzie nie ma opinii")
        return render_template('extract.html.jinja', error="Produkt o podanym kodzie nie istnieje")
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

