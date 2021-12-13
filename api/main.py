from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

SHOWLAST_ORDERS_INT = 99
ORDER_READY_TIME_MAX_SECS = 60
SHOP_NAME = "pret"


class OrderTempEnum(str, Enum):
    HOT = 'hot'
    COLD = 'cold'
    VERY_COLD = 'very_cold'
    NOT_SET = 'not_set'


class Order(BaseModel):
    source: Optional[str]
    order_id: int
    order_time: Optional[datetime]
    order_time_ready: Optional[datetime]
    order_temp: Optional[OrderTempEnum] = OrderTempEnum.NOT_SET
    order_status: Optional[str]

    class Config:
        use_enum_values = True


existing_orders = [
    {
        "source": SHOP_NAME,
        "order_id": 9,
        "order_time": datetime.now(),
        "order_time_ready": datetime.now(),
        "order_temp": OrderTempEnum.NOT_SET,
        "order_status": "new"},
    {
        "source": SHOP_NAME,
        "order_id": 10,
        "order_time": datetime.now(),
        "order_time_ready": datetime.now(),
        "order_temp": OrderTempEnum.NOT_SET,
        "order_status": "new"}
]

app = FastAPI()


def remove_old_orders() -> List:
    new_existing_orders = []
    for cur_order in existing_orders:
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
                existing_orders.remove(cur_order)
            print("existing orders size={0}".format(len(existing_orders)))
    return existing_orders


def set_food_temp():
    updated_orders = []
    for order in existing_orders:
        # only set the temp when the order is in ready state
        if order['order_status'] == 'ready':
            order_time = order['order_time_ready']
            time_now = datetime.now()
            total_secs = (time_now - order_time)
            diff_secs = total_secs.total_seconds()
            if diff_secs > ORDER_READY_TIME_MAX_SECS / 2:
                update_order = Order(
                    source=order['source'],
                    order_id=order['order_id'],
                    order_time=order['order_time'],
                    order_time_ready=order['order_time_ready'],
                    order_temp=OrderTempEnum.COLD,
                    order_status=order['order_status']
                )
                # update the list with the existing order
                updated_orders.append(update_order)
            else:
                # don't update the order
                updated_orders.append(order)
        else:
            updated_orders.append(order)
    return updated_orders


@app.post('/order/', response_model=Order)
async def create_order(*, order: Order) -> dict:

    new_order = Order(
        source=SHOP_NAME,
        order_id=order.order_id,
        order_time=datetime.now(),
        order_time_ready=datetime.now(),
        order_temp=OrderTempEnum.NOT_SET,
        order_status="new"
    )
    print(new_order)
    # if the order id is greater than 99 then ignore it!
    is_between = int(order.order_id) in range(0, 100)
    # get the last order and if the new order is the same then ignore it!
    if is_between:
        if len(existing_orders) >= 1:
            last_order = existing_orders[-1]
            if last_order['order_id'] != order.order_id:
                existing_orders.append(new_order.dict())
        elif len(existing_orders) == 0:
            existing_orders.append(new_order.dict())
    return order


@app.get('/orders', response_model=List[Order])
async def get_all_orders():
    return existing_orders


@app.get('/currentordersv2', response_model=List[Order])
async def get_all_current_orders_v2():
    existing_orders = remove_old_orders()
    existing_orders = set_food_temp()
    return existing_orders[-SHOWLAST_ORDERS_INT:]


@app.put('/orderready/{order_id}')
async def order_ready(order_id: int) -> dict:
    for order in existing_orders:
        if order['order_id'] == order_id:
            order['order_time_ready'] = datetime.now()
            order['order_status'] = "ready"
            order['order_temp'] = OrderTempEnum.HOT
    return {"update": "success"}
