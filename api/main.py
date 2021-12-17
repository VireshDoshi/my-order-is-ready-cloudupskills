from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import json

SHOWLAST_ORDERS_INT = 99
ORDER_READY_TIME_MAX_SECS = 60
PROBLEM_ORDERS_SECS = 180
# just remove orders if they are in problem state after set time
PROBLEM_ORDERS_MAX_SECS = 300
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

class OrderStatusEnum(str, Enum):
    NEW = 'new'
    PREPARING = 'preparing'
    PROBLEM = 'problem'
    READY = 'ready'
    COMPLETE = 'complete'
    NOT_SET = 'not_set'

    def equals(self, string):
        return self.value  == string
    
    def __str__(self):
        return str(self.value)



class Order(BaseModel):
    order_id: int
    order_time: Optional[datetime]
    order_time_ready: Optional[datetime]
    order_temp: Optional[OrderTempEnum] = OrderTempEnum.NOT_SET
    order_status: Optional[OrderStatusEnum] = OrderStatusEnum.NOT_SET
    order_type: Optional[OrderTypeEnum] = OrderTypeEnum.COFFEE

    class Config:
        use_enum_values = True


shopsDict = {'windsor': [], 'heathrow': [] }

app = FastAPI()


def remove_old_orders(shop_name: str) -> int:
    shop_orders = shopsDict[shop_name]
    new_existing_orders = []
    remove_count = 0
    for cur_order in shop_orders:
        if OrderStatusEnum.READY.equals(cur_order['order_status']):
            cur_order_time = cur_order['order_time_ready']
            time_now = datetime.now()
            total_secs = (time_now - cur_order_time)
            diff_secs = total_secs.total_seconds()
            # print("diff_secs={0} order_id={1}".format(diff_secs,
            #                                           cur_order['order_id']))
            if diff_secs < ORDER_READY_TIME_MAX_SECS:
                new_existing_orders.append(cur_order)
            else:
                shop_orders.remove(cur_order)
            # print("existing orders size={0}".format(len(shop_orders)))
        if OrderStatusEnum.PROBLEM.equals(cur_order['order_status']):
            cur_order_time = cur_order['order_time']
            time_now = datetime.now()
            total_secs = (time_now - cur_order_time)
            diff_secs = total_secs.total_seconds()
            # print("diff_secs={0} order_id={1}".format(diff_secs,
            #                                           cur_order['order_id']))
            if diff_secs > PROBLEM_ORDERS_MAX_SECS:
                shop_orders.remove(cur_order)
    return remove_count

def set_order_state_to_problem(shop_name: str) -> int:
    shop_orders = shopsDict[shop_name]
    # print(shop_orders)
    updated_orders = []
    for order in shop_orders:
        # print(order['order_status'])
        if OrderStatusEnum.NEW.equals(order['order_status']):
            order_time = order['order_time']
            time_now = datetime.now()
            total_secs = (time_now - order_time)
            diff_secs = total_secs.total_seconds()
            # print("set_order_state_to_problem  - diff_secs={0} order_id={1}".format(diff_secs,
            #                                           order['order_id']))
            if diff_secs > PROBLEM_ORDERS_SECS:
                update_order = Order(
                    order_id=order['order_id'],
                    order_time=order['order_time'],
                    order_time_ready=order['order_time_ready'],
                    order_temp=order['order_temp'],
                    order_status=OrderStatusEnum.PROBLEM,
                    order_type=order['order_type']
                )
                # update the list with the existing order
                # Order object Model is converted to a dict!
                updated_orders.append(update_order.dict())
            else:
                # don't update the order
                # take the existing order where status is NEW and
                # still inside the PROBLEM_ORDER_SECS
                updated_orders.append(order)
        else:
            # just take the existing order where status is not NEW
            updated_orders.append(order)
    # set global db dict
    shopsDict[shop_name] = updated_orders
    return len(updated_orders)

def set_food_temp(shop_name: str) -> int:
    shop_orders = shopsDict[shop_name]
    updated_orders = []
    for order in shop_orders:
        # only set the temp when the order is in ready state
        if OrderStatusEnum.READY.equals(order['order_status']):
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
                updated_orders.append(update_order.dict())
            else:
                # don't update the order
                updated_orders.append(order)
        else:
            updated_orders.append(order)
    # set global db dict
    shopsDict[shop_name] = updated_orders
    return len(updated_orders)


@app.post('/order/{shop_name}', response_model=Order)
async def create_order(*, shop_name: str, order: Order) -> dict:
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


@app.get('/currentordersv2/{shop_name}', response_model=List[Order])
async def get_all_current_orders_v2(shop_name: str):
    try:
        # Get the exising shop orders
        shop_orders = shopsDict[shop_name]
        set_order_state_to_problem(shop_name)
        remove_old_orders(shop_name)
        set_food_temp(shop_name)
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
            order['order_status'] = OrderStatusEnum.READY
            order['order_temp'] = OrderTempEnum.HOT
    return {"update": "success"}


@app.put('/addshop/{shop_name}')
async def addShop(shop_name: str)-> dict:
    shopsDict[shop_name]= []
    return {"shop added": "success"}

@app.get('/shops')
async def listShops()-> json:
    return json.dumps(shopsDict.keys(), sort_keys=True, default=str)