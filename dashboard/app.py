from flask import Flask, render_template
import requests
import json

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/getorders/')
def getOrders():
    r = requests.get('http://api:8000/currentordersv2')
    data = r.json()
    print(data)
    orders_new = []
    orders_ready = []
    for order in data:
        if order['order_status'] == 'new':
            orders_new.append(order)
        if order['order_status'] == 'ready':
            orders_ready.append(order)
    return json.dumps(data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)
