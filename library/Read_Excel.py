from openpyxl import load_workbook
import datetime
from .types import Order 
from .Exchange import Exchange


def read_excel_file(file_path):

    # Fresh heaps for every upload
    buy_heap = []
    sell_heap = []

    resource_id = 1

    workbook = load_workbook(file_path)
    sheet = workbook.active

    for row in sheet.iter_rows(min_row=2, values_only=True):

        user_id = row[0]
        side = row[1]
        quantity = row[2]
        price = row[3]
        order_type = 1 if side.upper() == "BUY" else 0

        order = (
            float(price),
            datetime.datetime.now(),
            None,
            user_id,
            resource_id,
            int(quantity),
            order_type
        )

        print("Processing order:", order)

        Exchange.exchange(order, buy_heap, sell_heap)

    workbook.close()

    return buy_heap, sell_heap