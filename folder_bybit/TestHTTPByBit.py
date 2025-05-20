from dotenv import load_dotenv
import os

from http_bybit import ClientBybit
from pybit import exceptions

load_dotenv()

api_key = os.getenv("BYBIT_API_KEY")
secret_key = os.getenv("BYBIT_SECRET_KEY")

SYMBOL = "XRPUSDT"
CATEGORY = "linear"
TAKEPROFIT = 1.03
STOPLOSS = 0.97

try:
    bb = ClientBybit(ApiKey=api_key,ApiSecret=secret_key,category=CATEGORY,symbol=SYMBOL)

    list_history_price = bb.get_kline("1", 15)
    print(list_history_price)

    # lastTime, lastPrice = bb.get_ticker()
    # print(lastTime, lastPrice)

    # orderId = bb.place_order(side="Sell", orderType="Market", lastPrice=lastPrice, takeProfit=TAKEPROFIT, stopLoss=STOPLOSS)
    # print(orderId)



except exceptions.InvalidRequestError as e:
    print("ByBit API Request Error", e.status_code, e.message, sep=" | ")
except exceptions.FailedRequestError as e:
    print("HTTP Request Failed", e.status_code, e.message, sep=" | ")
except Exception as e:
    raise e