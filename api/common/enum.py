from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderTypeEnum(str, Enum):
    COFFEE = 'coffee'
    SMOOTHIE = 'smoothie'
    TOASTIE = 'toastie'
    DONUT = 'donut'


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
        return self.value == string

    def __str__(self):
        return str(self.value)


# pydantic model used to define the order
# the order is converted to a dict and stored
# as the ORder object is not iterable
class Order(BaseModel):
    order_id: int
    order_time: Optional[datetime]
    order_time_ready: Optional[datetime]
    order_temp: Optional[OrderTempEnum] = OrderTempEnum.NOT_SET
    order_status: Optional[OrderStatusEnum] = OrderStatusEnum.NOT_SET
    order_type: Optional[OrderTypeEnum] = OrderTypeEnum.COFFEE

    # I don't know what this does?
    class Config:
        use_enum_values = True
