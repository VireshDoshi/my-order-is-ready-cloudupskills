from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import json

SHOWLAST_ORDERS_INT = 99
ORDER_READY_TIME_MAX_SECS = 60
SHOP_NAME = "pret"

class OrderTypeEnum(str, Enum):
    COFFEE = 'coffee'
    SMOOTHIE = 'smoothie'
    TOASTIE  = 'toastie'
    DONUT    = 'donut'

class OrderTempEnum(str, Enum):
    HOT = 'hot'
    COLD = 'cold'
    VERY_COLD = 'very_cold'
    NOT_SET = 'not_set'


class Order(BaseModel):
    order_id: int
    order_time: Optional[datetime]
    order_time_ready: Optional[datetime]
    order_temp: Optional[OrderTempEnum] = OrderTempEnum.NOT_SET
    order_status: Optional[str]
    order_type: Optional[OrderTypeEnum] = OrderTypeEnum.COFFEE

    class Config:
        use_enum_values = True


shopsDict = {'windsor': [], 'heathrow': [] }

app = FastAPI()


def remove_old_orders(shop_orders: List) -> List:
    new_existing_orders = []
    for cur_order in shop_orders:
        if cur_order['order_status'] == 'ready':
            cur_order_time = cur_order['order_time_ready']
            time_now = datetime.now()
            total_secs = (time_now - cur_order_time)
            diff_secs = total_secs.total_seconds()
            print("diff_secs={0} order_id={1}".format(diff_secs,
                                                      cur_order['order_id']))
            if diff_secs < ORDER_READY_TIME_MAX_SECS:
                new_existing_orders.append(cur_order)
            else:
                shop_orders.remove(cur_order)
            print("existing orders size={0}".format(len(shop_orders)))
    return shop_orders


def set_food_temp(shop_orders: List) -> List:
    updated_orders = []
    for order in shop_orders:
        # only set the temp when the order is in ready state
        if order['order_status'] == 'ready':
            order_time = order['order_time_ready']
            time_now = datetime.now()
            total_secs = (time_now - order_time)
            diff_secs = total_secs.total_seconds()
            if diff_secs > ORDER_READY_TIME_MAX_SECS / 2:
                update_order = Order(
                    order_id=order['order_id'],
                    order_time=order['order_time'],
                    order_time_ready=order['order_time_ready'],
                    order_temp=OrderTempEnum.COLD,
                    order_status=order['order_status'],
                    order_type=order['order_type']
                )
                # update the list with the existing order
                updated_orders.append(update_order)
            else:
                # don't update the order
                updated_orders.append(order)
        else:
            updated_orders.append(order)
    return updated_orders


@app.post('/order/{shop_name}', response_model=Order)
async def create_order(*, shop_name: str, order: Order) -> dict:
    # get the orders from that shop
    shop_orders = shopsDict[shop_name]
    new_order = Order(
        order_id=order.order_id,
        order_time=datetime.now(),
        order_time_ready=datetime.now(),
        order_temp=OrderTempEnum.NOT_SET,
        order_status="new",
        order_type=order.order_type
    )
    print(new_order)
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


@app.get('/currentordersv2/{shop_name}', response_model=List[Order])
async def get_all_current_orders_v2(shop_name: str):
    try:
        # Get the exising shop orders
        shop_orders = shopsDict[shop_name]
        shop_orders = remove_old_orders(shop_orders)
        shop_orders = set_food_temp(shop_orders)
    except KeyError:
        # Shop does not exist. How about we add it?
        shopsDict[shop_name]= []
        shop_orders = shopsDict[shop_name]

    return shop_orders[-SHOWLAST_ORDERS_INT:]


@app.put('/orderready/{shop_name}/{order_id}')
async def order_ready(shop_name: str, order_id: int) -> dict:
    for order in shopsDict[shop_name]:
        if order['order_id'] == order_id:
            order['order_time_ready'] = datetime.now()
            order['order_status'] = "ready"
            order['order_temp'] = OrderTempEnum.HOT
    return {"update": "success"}


@app.put('/addshop/{shop_name}')
async def addShop(shop_name: str)-> dict:
    shopsDict[shop_name]= []
    return {"shop added": "success"}

@app.get('/shops')
async def listShops()-> json:
    return json.dumps(shopsDict.keys(), sort_keys=True, default=str)