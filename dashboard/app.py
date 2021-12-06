from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import json
import time

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index2():
    while True:
        my_orders = []
        r = requests.get('http://api:8000/currentordersv2')
        data= r.json()
        print(data)
        orders_new = []
        orders_ready = []
        for order in data:
            if order['order_status'] == 'new':
                orders_new.append(order)
            if order['order_status'] == 'ready':
                orders_ready.append(order)
        return render_template('index.html', my_orders_new=orders_new,
                            my_orders_ready=orders_ready
                            )
        time.sleep(2)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)