from fastapi import FastAPI
from typing import List
from datetime import datetime
import json
from common.structlog import config_structlog
from orders.order import shopsDict
from orders.order import SHOWLAST_ORDERS_INT
from orders.order import (remove_old_orders,
                          set_order_state_to_problem, set_food_temp)
from common.enum import OrderTempEnum, OrderStatusEnum, Order
import structlog
import os

config_structlog
log = structlog.get_logger()

app = FastAPI()
SHOP_NAME = os.environ['SHOP_NAME']
BRAND_NAME = os.environ['BRAND_NAME']


@app.post('/order', response_model=Order)
async def create_order(*, order: Order) -> dict:
    shop_name = SHOP_NAME
    # get the orders from that shop
    shop_orders = shopsDict[shop_name]
    new_order = Order(
        order_id=order.order_id,
        order_time=datetime.now(),
        order_time_ready=datetime.now(),
        order_temp=OrderTempEnum.NOT_SET,
        order_status=OrderStatusEnum.NEW,
        order_type=order.order_type
    )
    # print(new_order)
    # if the order id is greater than 99 then ignore it!
    is_between = int(order.order_id) in range(0, 100)
    # get the last order and if the new order is the same then ignore it!
    if is_between:
        if len(shop_orders) >= 1:
            last_order = shop_orders[-1]
            if last_order['order_id'] != order.order_id:
                shop_orders.append(new_order.dict())
        elif len(shop_orders) == 0:
            shop_orders.append(new_order.dict())
    return order


@app.get('/currentordersv2', response_model=List[Order])
async def get_all_current_orders_v2():
    shop_name = SHOP_NAME
    try:
        # Get the exising shop orders
        shop_orders = shopsDict[shop_name]
        set_order_state_to_problem(shop_name)
        remove_old_orders(shop_name)
        set_food_temp(shop_name)
    except KeyError:
        # Shop does not exist. How about we add it?
        shopsDict[shop_name] = []
        shop_orders = shopsDict[shop_name]

    return shop_orders[-SHOWLAST_ORDERS_INT:]


@app.put('/orderready/{order_id}')
async def order_ready(order_id: int) -> dict:
    shop_name = SHOP_NAME
    for order in shopsDict[shop_name]:
        if order['order_id'] == order_id:
            order['order_time_ready'] = datetime.now()
            order['order_status'] = OrderStatusEnum.READY
            order['order_temp'] = OrderTempEnum.HOT
    return {"update": "success"}


@app.put('/addshop/{shop_name}')
async def addShop(shop_name: str) -> dict:
    shopsDict[shop_name] = []
    return {"shop added": "success"}


@app.get('/shops')
async def listShops() -> json:
    return json.dumps(shopsDict.keys(), sort_keys=True, default=str)
