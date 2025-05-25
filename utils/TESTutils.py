# python -m utils.TESTutils

import asyncio
from dotenv import load_dotenv
import os

from folder_bybit.http_bybit import ClientBybit
from utils.temporary_warrant import temporary_order, temporary_position

from pybit import exceptions


load_dotenv()

api_key = os.getenv("BYBIT_API_KEY")
secret_key = os.getenv("BYBIT_SECRET_KEY")

SYMBOL = "XRPUSDT"
CATEGORY = "linear"
TAKEPROFIT = 1.005
STOPLOSS = 0.995
TIMEORDER = 10 # секунд
TIMEPOSITION = 10 # секунд

try:
    bb = ClientBybit(ApiKey=api_key,ApiSecret=secret_key,category=CATEGORY,symbol=SYMBOL)

    lastTime, lastPrice = bb.get_ticker()
    print(lastTime, lastPrice)

    orderId = bb.place_order(side="Buy", orderType="Market", lastPrice=lastPrice, takeProfit=TAKEPROFIT, stopLoss=STOPLOSS)
    print(orderId)

    # asyncio.run(temporary_order(orderId, TIMEORDER, bb))
    asyncio.run(temporary_position(orderId, TIMEPOSITION, bb))


except exceptions.InvalidRequestError as e:
    print("ByBit API Request Error", e.status_code, e.message, sep=" | ")
except exceptions.FailedRequestError as e:
    print("HTTP Request Failed", e.status_code, e.message, sep=" | ")
except Exception as e:
    raise e