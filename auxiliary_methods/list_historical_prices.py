# python -m auxiliary_methods.list_historical_prices

from dotenv import load_dotenv
import os
# import datetime
# import pytz

from folder_bybit.http_bybit import ClientBybit
from pybit import exceptions

load_dotenv()

api_key = os.getenv("BYBIT_API_KEY")
secret_key = os.getenv("BYBIT_SECRET_KEY")

SYMBOL = "XRPUSDT"
CATEGORY = "linear"
HISTORY_PRICE = []

try:
    bb = ClientBybit(ApiKey=api_key,ApiSecret=secret_key,category=CATEGORY,symbol=SYMBOL)
    TIME_SERVER = bb._time_server()

    # start_date_str = input("Введите дату и время начала в формате YYYY-MM-DD HH:MM:SS (UTC): ")
    # try:
    #     start_datetime_utc = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
    #     # Убедитесь, что datetime объект имеет информацию о часовом поясе UTC
    #     start_datetime_utc = pytz.utc.localize(start_datetime_utc)
    #     START_MS = int(start_datetime_utc.timestamp() * 1000)
    #     print(f"Временная метка начала (ms): {START_MS}")
    # except ValueError:
    #     print("Неверный формат даты и времени. Пожалуйста, используйте YYYY-MM-DD HH:MM:SS (UTC).")
    #     exit()
    LIMIT = int(input("Введите количество свечей(например 3000 свечей): "))
    INTERVAL = input("Введите интервал свечей (например: 1,3,5,15,30,60,120,240,360,720,D,W,M): ")
    bb_INTERVAL = INTERVAL

    if INTERVAL == "D":
        INTERVAL = 24 * 60 * 60 * 1000
    elif INTERVAL == "W":
        INTERVAL = 7 * 24 * 60 * 60 * 1000
    elif INTERVAL == "M":
        INTERVAL = 30 * 24 * 60 * 60 * 1000
    else:
        INTERVAL = int(INTERVAL) * 60 * 1000

    if LIMIT <=1000:
        his_price = bb.get_kline(bb_INTERVAL, LIMIT)
        HISTORY_PRICE.append(his_price)
    else:
        end_time = TIME_SERVER
        start_time = TIME_SERVER - 1000 * INTERVAL
        while True:
            if LIMIT <=1000:
                his_price = bb.get_kline(bb_INTERVAL, LIMIT, start=start_time, end=end_time)
                print(his_price)
                HISTORY_PRICE.append(his_price)
                break
            his_price = bb.get_kline(bb_INTERVAL, 1000, start=start_time, end=end_time)
            HISTORY_PRICE.append(his_price)
            end_time = TIME_SERVER - 1000 * INTERVAL
            start_time = end_time - 1000 * INTERVAL
            LIMIT = LIMIT - 1000

    list_price = [item for sublist in HISTORY_PRICE for item in sublist]

    print(list_price)
except exceptions.InvalidRequestError as e:
    print("ByBit API Request Error", e.status_code, e.message, sep=" | ")
except exceptions.FailedRequestError as e:
    print("HTTP Request Failed", e.status_code, e.message, sep=" | ")
except Exception as e:
    raise e