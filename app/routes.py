from app import app
from app import utils
from flask import render_template, request, redirect, url_for
import os
import json
import requests
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from bs4 import BeautifulSoup
from flask import send_file

@app.route('/')
def index():
    return render_template('index.html.jinja')

@app.route('/extract', methods=['POST', 'GET'])
def extract():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        url = f"https://www.ceneo.pl/{product_id}"
        response = requests.get(url)
        if response.status_code == requests.codes['ok']:
            page = BeautifulSoup(response.text, "html.parser")
            opinions_count = page.select_one("a.product-review__link > span")
            if opinions_count:
                product_name = utils.get_data(page,"h1")
                url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
                all_opinions = []
                while(url):
                    print(url)
                    response = requests.get(url)
                    page = BeautifulSoup(response.text, "html.parser")
                    opinions = page.select("div.js_product-review")
                    for opinion in opinions:
                        single_opinion = {
                            key: utils.get_data(opinion, *value)
                                for key, value in utils.selectors.items()
                        }
                        all_opinions.append(single_opinion)
                    try:
                        url = "https://ceneo.pl"+page.select_one("a.pagination__next")["href"]
                    except TypeError:
                        url = None
                if not os.path.exists("app/data"):
                    os.mkdir("app/data")
                if not os.path.exists("app/data/opinions"):
                    os.mkdir("app/data/opinions")
                jf = open(f"app/data/opinions/{product_id}.json", "w", encoding="UTF-8")
                json.dump(all_opinions, jf, indent=4, ensure_ascii=False)
                jf.close()
                opinions = pd.DataFrame.from_dict(all_opinions)
                opinions.stars = opinions.stars.apply(lambda s: s.split('/')[0].replace(',', '.')).astype(float)
                stats = {
                    "product_id": product_id,
                    "product_name": product_name,
                    "opinions_count": opinions.shape[0],
                    "pros_count": int(opinions.pros.astype(bool).sum()),
                    "cons_count": int(opinions.cons.astype(bool).sum()),
                    "average_stars": opinions.stars.mean(),
                    "stars_distr": opinions.stars.value_counts().reindex(np.arange(0,5.5,0.5), fill_value=0).to_dict(),
                    "recommendation_distr": opinions.recommendation.value_counts().reindex(["Polecam", "Nie polecam", None], fill_value=0).to_dict(),
                }
                if not os.path.exists("app/data/products"):
                    os.mkdir("app/data/products")
                jf = open(f"app/data/products/{product_id}.json", "w", encoding="UTF-8")
                json.dump(stats, jf, indent=4, ensure_ascii=False)
                jf.close()
                return redirect(url_for('product', product_id=product_id))
            return render_template('extract.html.jinja', error="Produkt o podanym kodzie nie posiada opinii.")
        return render_template('extract.html.jinja', error="Produkt o podanym kodzie nie istnieje.")
    return render_template('extract.html.jinja')

@app.route('/products')
def products():
    products_list = [filename.split(".")[0] for filename in os.listdir('app/data/opinions')]
    products = []
    for product in products_list:
        jf = open(f"app/data/products/{product}.json", "r", encoding="UTF-8")
        products.append(json.load(jf))
        jf.close()
    return render_template('products.html.jinja', products=products)

@app.route('/about')
def about():
    return render_template('about.html.jinja')

@app.route('/product/<product_id>')
def product(product_id):
    if not os.path.exists("app/data/opinions"):
        return redirect(url_for('extract'))
    jf = open(f"app/data/opinions/{product_id}.json", "r", encoding="UTF-8")
    opinions = json.load(jf)
    jf.close()
    return render_template('product.html.jinja', product_id=product_id, opinions=opinions)
@app.route('/charts')
def charts():
    return render_template('charts.html.jinja')
@app.route('/back')
def back():
    return render_template('product.html.jinja')
from flask import send_file

@app.route('/product_charts/<product_id>')
def product_charts(product_id):
    if not os.path.exists(f"app/data/products/{product_id}.json"):
        return redirect(url_for('extract'))

    with open(f"app/data/products/{product_id}.json", "r", encoding="UTF-8") as jf:
        stats = json.load(jf)


    pie_chart_path = generate_pie_chart(stats['recommendation_distr'], product_id)
    bar_chart_path = generate_bar_chart(stats['stars_distr'], product_id)

    return render_template('charts.html.jinja', 
                            product_id=product_id, 
                            pie_chart=pie_chart_path,
                            bar_chart=bar_chart_path)

def generate_pie_chart(recommendation_distr, product_id):
    labels = recommendation_distr.keys()
    sizes = recommendation_distr.values()
    colors = ['green', 'red', 'grey']
    explode = (0.1, 0, 0)

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  

    pie_chart_path = f"app/static/{product_id}_pie_chart.png"
    plt.savefig(pie_chart_path)
    plt.close()
    return pie_chart_path

def generate_bar_chart(stars_distr, product_id):
    labels = list(stars_distr.keys())
    values = list(stars_distr.values())

    fig, ax = plt.subplots()
    ax.bar(labels, values, color='blue')

    ax.set_xlabel('Number of Stars')
    ax.set_ylabel('Number of Reviews')
    ax.set_title('Distribution of Star Ratings')


    bar_chart_path = f"app/static/{product_id}_bar_chart.png"
    plt.savefig(bar_chart_path)
    plt.close()
    return bar_chart_path
