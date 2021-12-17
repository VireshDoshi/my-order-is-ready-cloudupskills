from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)
# app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/", methods=['GET'])
def index():
    shop_name = request.args.get('shop')
    if shop_name is None:
        shop_name = 'pret'
    return render_template('index.html', shop_name=shop_name)


@app.route('/getorders/<shop_name>', methods=['GET'])
def getOrders(shop_name: str):
    r = requests.get('http://api:8000/currentordersv2/' + shop_name)
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
    app.run(host='0.0.0.0', port='5001', debug=True)
