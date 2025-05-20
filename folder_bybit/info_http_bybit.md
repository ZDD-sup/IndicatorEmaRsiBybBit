# Руководство по работе с классом `ClientBybit`

Данный документ предоставляет подробное описание класса `ClientBybit` и объясняет, как использовать его для взаимодействия с API Bybit Unified Trading.

## Описание класса

Класс `ClientBybit` предназначен для упрощения взаимодействия с API Bybit Unified Trading. Он инкапсулирует основные функции, такие как подключение, получение информации о торговых инструментах, получение исторических данных, получение текущей цены и размещение ордеров.

## Импорт библиотек

В начале кода импортируются необходимые библиотеки:

```python
from pybit.unified_trading import HTTP
from math import ceil
```

  * `pybit.unified_trading.HTTP`: Основной класс из библиотеки `pybit` для выполнения HTTP-запросов к API Bybit Unified Trading.
  * `math.ceil`: Функция для округления числа вверх до ближайшего целого.

## Инициализация класса (`__init__`)

Конструктор класса `__init__` принимает следующие аргументы:

```python
def __init__(self, ApiKey, ApiSecret, category, symbol):
```

  * `ApiKey` (str): Ваш API ключ от Bybit.
  * `ApiSecret` (str): Ваш секретный ключ API от Bybit.
  * `category` (str): Категория торгов (`"spot"`, `"linear"`, `"inverse"`). В текущей версии основная функциональность реализована для `"linear"`.
  * `symbol` (str): Торговый символ (например, `"BTCUSDT"`, `"XRPUSDT"`).

В процессе инициализации выполняются следующие действия:

1.  Создается сессия HTTP-клиента Bybit:
    ```python
    self.session = HTTP(
        demo=True,  # По умолчанию используется демо-режим. Для реальной торговли установите False.
        api_key=ApiKey,
        api_secret=ApiSecret,
    )
    ```
    **Важно:** По умолчанию установлен `demo=True`, что означает использование демо-аккаунта Bybit. Для работы с реальным аккаунтом необходимо изменить на `demo=False`.
2.  Сохраняются переданные `symbol` и `category`.
3.  Инициализируются атрибуты для хранения торговых фильтров: `minPrice`, `maxPrice`, `minOrderQty`, `maxOrderQty`, `qtyStep`, `tickSize`.
4.  Если `category` установлено в `"linear"`, вызывается метод `_instrument_info()` для получения информации о торговом инструменте (минимальная/максимальная цена/количество, шаг цены/количества, минимальная номинальная стоимость).
5.  Выводится сообщение об успешном подключении и основные параметры инструмента.

## Второстепенные (Информирующие) функции

### `_time_server()`

```python
def _time_server(self):
    result = self.session.get_server_time()
    return result["time"]
```

  * Получает текущее время сервера Bybit в миллисекундах.
  * Использует метод `get_server_time()` из объекта `self.session`.
  * Возвращает значение ключа `"time"` из полученного JSON-ответа.

### `_instrument_info()`

```python
def _instrument_info(self):
    data = self.session.get_instruments_info(
        category = self.category,
        symbol = self.symbol
    )
    instrument_data = data["result"]["list"][0]
    self.minPrice = float(instrument_data["priceFilter"]["minPrice"])
    self.maxPrice = float(instrument_data["priceFilter"]["maxPrice"])
    self.minOrderQty = float(instrument_data["lotSizeFilter"]["minOrderQty"])
    self.maxOrderQty = float(instrument_data["lotSizeFilter"]["maxOrderQty"])
    self.qtyStep = float(instrument_data["lotSizeFilter"]["qtyStep"])
    self.tickSize = float(instrument_data["priceFilter"]["tickSize"])
    self.minNotionalValue = float(instrument_data["lotSizeFilter"]["minNotionalValue"])
```

  * Получает информацию о торговом инструменте (для категории `"linear"`).
  * Использует метод `get_instruments_info()` из `self.session`, передавая `category` и `symbol`.
  * Извлекает необходимые значения (минимальную/максимальную цену/количество, шаг цены/количества, минимальную номинальную стоимость) из полученных данных и сохраняет их в соответствующих атрибутах класса.

### `_caluc_TP_SL(lastPrice, takeProfit, storLoss)`

```python
def _caluc_TP_SL(self, lastPrice: float, takeProfit: float, storLoss: float):
    if self.tickSize is None:
        print("Ошибка: tickSize не определен. Убедитесь, что _instrument_info() была вызвана.")
        return None, None

    take_profit_price_unrounded = lastPrice * takeProfit
    stop_loss_price_unrounded = lastPrice * storLoss

    num_decimals = self._get_decimal_places(self.tickSize)

    take_profit_price = round(take_profit_price_unrounded, num_decimals)
    stop_loss_price = round(stop_loss_price_unrounded, num_decimals)

    return take_profit_price, stop_loss_price
```

  * Рассчитывает цены Take Profit и Stop Loss на основе множителей относительно `lastPrice`.
  * Использует `self.tickSize` для определения количества знаков после запятой при округлении цен.
  * Возвращает кортеж из округленных цен Take Profit и Stop Loss.

### `_get_decimal_places(tick_size)`

```python
def _get_decimal_places(self, tick_size: float) -> int:
    s = str(tick_size)
    if '.' in s:
        return len(s) - s.find('.') - 1
    else:
        return 0
```

  * Вспомогательная функция для определения количества знаков после запятой в значении `tickSize`.

### `_calcul_min_qty(lastPrice)`

```python
def _calcul_min_qty(self, lastPrice):
    if lastPrice == 0:
        return float('inf')  # Избегаем деления на ноль

    calculated_min_qty_unrounded = self.minNotionalValue / lastPrice

    # Округляем вверх до ближайшего кратного qtyStep
    calculated_min_qty_rounded = ceil(calculated_min_qty_unrounded / self.qtyStep) * self.qtyStep

    if calculated_min_qty_rounded < self.minOrderQty:
        return self.minOrderQty
    else:
        return calculated_min_qty_rounded
```

  * Вычисляет минимальное количество для ордера, учитывая `self.minNotionalValue`, `lastPrice` и округление в соответствии с `self.qtyStep`.
  * Возвращает наибольшее значение между рассчитанным минимальным количеством (на основе номинальной стоимости) и `self.minOrderQty`.

## Основные (Торговые) функции

### `get_kline(interval, limit, start=None, end=None)`

```python
def get_kline(self, interval: str, limit: int, start: int=None, end: int=None):
    data = self.session.get_kline(
        symbol = self.symbol,
        category = self.category,
        interval=interval,
        start=start,
        end=end,
        limit=limit
    )
    return [(int(item[0]), float(item[4])) for item in data["result"]["list"]]
```

  * Получает исторические данные (свечи) для указанного символа и категории.
  * `interval` (str): Временной интервал свечей (например, `"1m"`, `"5m"`, `"1h"`).
  * `limit` (int): Максимальное количество свечей для запроса.
  * `start` (int, optional): Начальная временная метка (в миллисекундах).
  * `end` (int, optional): Конечная временная метка (в миллисекундах).
  * Возвращает список кортежей, где каждый кортеж содержит временную метку (int) и цену закрытия (float) свечи.

### `get_ticker()`

```python
def get_ticker(self):
    data = self.session.get_tickers(
        category = self.category,
        symbol = self.symbol
    )
    return int(data["time"]), float(data["result"]["list"][0]["lastPrice"])
```

  * Получает текущую информацию о тикере для указанного символа и категории.
  * Возвращает кортеж, содержащий время сервера (int) и последнюю торговую цену (float).

### `place_order(side, orderType, lastPrice=None, qty=None, takeProfit=None, stopLoss=None)`

```python
def place_order(self, side: str, orderType: str, lastPrice: float=None, qty: float=None, takeProfit: float=None, stopLoss: float=None):
    if self.category == "spot": # ПОКА НЕ РАБОТАТЬ
        result = self.session.place_order(
            category = self.category,
            symbol = self.symbol,
            side = side,
            orderType = orderType,
            qty = qty,
        )
        return result["result"]["orderId"]
    elif self.category == "linear":
        takeProfit, stopLoss = self._caluc_TP_SL(lastPrice=lastPrice, takeProfit=takeProfit, storLoss=stopLoss)
        if side == "Sell":
            takeProfit, stopLoss = stopLoss, takeProfit
        qty = self._calcul_min_qty(lastPrice)
        print(f"qty: {qty}")
        result = self.session.place_order(
            category = self.category,
            symbol = self.symbol,
            side = side,
            orderType = orderType,
            qty = qty,
            takeProfit = takeProfit,
            stopLoss = stopLoss
        )
        return result["result"]["orderId"]
    elif self.category == "inverse":
        pass # Напиши когда-нибудь
```

  * Размещает ордер на бирже Bybit.
  * `side` (str): Сторона ордера (`"Buy"` или `"Sell"`).
  * `orderType` (str): Тип ордера (`"Market"`, `"Limit"`).
  * `lastPrice` (float, optional): Цена ордера (обязательно для лимитных ордеров).
  * `qty` (float, optional): Количество для ордера (для категории `"spot"`). Для `"linear"` количество рассчитывается автоматически.
  * `takeProfit` (float, optional): Множитель для установки Take Profit относительно `lastPrice`.
  * `stopLoss` (float, optional): Множитель для установки Stop Loss относительно `lastPrice`.

**Особенности для категории `"linear"`:**

  * Цены Take Profit и Stop Loss рассчитываются с помощью метода `_caluc_TP_SL()`.
  * Количество ордера (`qty`) рассчитывается автоматически с помощью метода `_calcul_min_qty()` для обеспечения минимальной номинальной стоимости и соблюдения шага изменения количества.
  * Для ордеров на продажу (`"Sell"`), цены Take Profit и Stop Loss меняются местами, так как Take Profit для продажи устанавливается выше цены открытия, а Stop Loss - ниже.

**Важно:** Размещение ордеров для категории `"spot"` в текущей версии кода не реализовано (`# ПОКА НЕ РАБОТАТЬ`).

## Пример использования

```python
# Замените на свои реальные API ключ и секрет
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"
category = "linear"
symbol = "BTCUSDT"

client = ClientBybit(ApiKey=api_key, ApiSecret=api_secret, category=category, symbol=symbol)

# Получение исторических данных
klines = client.get_kline(interval="1h", limit=10)
print("Исторические данные:", klines)

# Получение текущей цены
timestamp, current_price = client.get_ticker()
print("Текущая цена:", current_price)

# Размещение рыночного ордера на покупку с Take Profit и Stop Loss
if current_price is not None:
    order_id = client.place_order(
        side="Buy",
        orderType="Market",
        lastPrice=current_price,
        takeProfit=1.01, # 1% выше цены открытия
        stopLoss=0.99    # 1% ниже цены открытия
    )
    print("ID размещенного ордера:", order_id)
```

Этот пример демонстрирует основные шаги:

1.  Инициализация клиента `ClientBybit`.
2.  Получение исторических данных.
3.  Получение текущей цены.
4.  Размещение рыночного ордера на покупку с установленными Take Profit и Stop Loss (для категории `"linear"`).

Перед использованием кода убедитесь, что у вас есть действующие API ключ и секрет от Bybit и вы понимаете риски, связанные с торговлей на бирже.