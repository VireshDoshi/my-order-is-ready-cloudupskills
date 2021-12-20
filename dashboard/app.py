from flask import Flask, render_template
import requests
import json
import os

app = Flask(__name__)
API_PORT = os.environ['API_PORT']
SHOP_NAME = os.environ['SHOP_NAME']


@app.route("/", methods=['GET'])
def index():
    shop_name = SHOP_NAME
    # shop_name = request.args.get('shop')
    # if shop_name is None:
    #     shop_name = 'pret'
    return render_template('index.html', shop_name=shop_name)


@app.route('/getorders/<shop_name>', methods=['GET'])
def getOrders(shop_name: str):
    shopapi = "http://api-{}:{}/currentordersv2/{}".format(
              shop_name, API_PORT, shop_name)
    r = requests.get(shopapi)
    data = r.json()
    # print(data)
    # orders_new = []
    # orders_ready = []
    # for order in data:
    #     if order['order_status'] == 'new':
    #         orders_new.append(order)
    #     if order['order_status'] == 'ready':
    #         orders_ready.append(order)
    return json.dumps(data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
