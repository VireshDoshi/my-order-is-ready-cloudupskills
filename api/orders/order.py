from common.enum import OrderTempEnum, OrderStatusEnum, Order
import structlog
from common.structlog import config_structlog
from datetime import datetime


config_structlog
log = structlog.get_logger()

SHOWLAST_ORDERS_INT = 99
ORDER_READY_TIME_MAX_SECS = 60
PROBLEM_ORDERS_SECS = 180
# just remove orders if they are in problem state after set time
PROBLEM_ORDERS_MAX_SECS = 300

# Main in memory database
shopsDict = {'windsor': [], 'heathrow': []}


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
            log.msg("remove_old_orders in READY state",
                    shop_name=shop_name, order_id=cur_order['order_id'],
                    order_age=diff_secs, order_status="READY")
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
            log.msg("remove_old_orders",
                    shop_name=shop_name, order_id=cur_order['order_id'],
                    order_age=diff_secs, order_status="PROBLEM")
            if diff_secs > PROBLEM_ORDERS_MAX_SECS:
                shop_orders.remove(cur_order)
                remove_count = remove_count + 1
    log.msg("remove_old_orders", remove_count=remove_count)
    return remove_count


def set_order_state_to_problem(shop_name: str) -> int:
    shop_orders = shopsDict[shop_name]
    updated_orders = []
    for order in shop_orders:
        if OrderStatusEnum.NEW.equals(order['order_status']):
            order_time = order['order_time']
            time_now = datetime.now()
            total_secs = (time_now - order_time)
            diff_secs = total_secs.total_seconds()
            log.msg("set_order_state_to_problem",
                    shop_name=shop_name, order_id=order['order_id'],
                    order_age=diff_secs)
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
