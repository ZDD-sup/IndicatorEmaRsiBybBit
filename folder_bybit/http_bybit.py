from pybit.unified_trading import HTTP
from math import ceil

class ClientBybit:
    def __init__(self, ApiKey, ApiSecret, category, symbol):
        self.session = HTTP(
            demo=True,
            api_key=ApiKey,
            api_secret=ApiSecret,
        )
        self.symbol = symbol
        self.category = category
        # фильтры для торгов
        self.minPrice = 0       # Минимально допустимая цена для ордера
        self.maxPrice = 0       # Максимально допустимая цена для ордера
        self.minOrderQty = 0    # Минимально допустимое количество для ордера
        self.maxOrderQty = 0    # Максимально допустимое количество для ордера
        self.qtyStep = 0        # Шаг изменения количества ордера
        self.tickSize = 0       # Шаг изменения цены ордера
        if category == "linear":
            self._instrument_info()
        print("____________________Успешно подключился!____________________")
        print(f"Время сервера ByBit: {self._time_server()} ms")
        print("\nТекущие параметры:")
        print(f"  Символ: {self.symbol}")
        print(f"  Категория: {self.category}")
        print(f"  Минимальная цена: {self.minPrice}")
        print(f"  Максимальная цена: {self.maxPrice}")
        print(f"  Минимальное количество ордера: {self.minOrderQty}")
        print(f"  Максимальное количество ордера: {self.maxOrderQty}")
        print(f"  Шаг изменения количества: {self.qtyStep}")
        print(f"  Шаг изменения цены (тик): {self.tickSize}")

# ---------- Информирующие функции (Второстипенные) ----------
# ----- Получение времени сервера -----
    def _time_server(self):
        result = self.session.get_server_time()
        return result["time"]

# ----- Получении информации о монете для категории торгов linear -----
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

# ----- Расчёт takeProfit и stotLoss -----
    def _caluc_TP_SL(self, lastPrice: float, takeProfit: float, storLoss: float):
        if self.tickSize is None:
            print("Ошибка: tickSize не определен. Убедитесь, что _instrument_info() была вызвана.")
            return None, None

        take_profit_price_unrounded = lastPrice * takeProfit
        stop_loss_price_unrounded = lastPrice * storLoss

        num_decimals = self._get_decimal_places(self.tickSize)

        take_profit_price = round(take_profit_price_unrounded, num_decimals)
        stop_loss_price = round(stop_loss_price_unrounded, num_decimals)

        # print(f"Последняя цена: {lastPrice}")
        # print(f"Take Profit (множитель {takeProfit}): {take_profit_price_unrounded}, округлено до {num_decimals} знаков: {take_profit_price}")
        # print(f"Stop Loss (множитель {storLoss}): {stop_loss_price_unrounded}, округлено до {num_decimals} знаков: {stop_loss_price}")

        return take_profit_price, stop_loss_price

    def _get_decimal_places(self, tick_size: float) -> int:
        s = str(tick_size)
        if '.' in s:
            return len(s) - s.find('.') - 1
        else:
            return 0
        
# ----- Вычисления минимального qty -----
    def _calcul_min_qty(self, lastPrice):
        """
        Вычисляет минимальное количество для ордера с учетом minNotionalValue, lastPrice и округления по qtyStep.

        Args:
            lastPrice (float): Последняя известная цена актива.

        Returns:
            float: Минимальное количество для ордера.
        """
        if lastPrice == 0:
            return float('inf')  # Избегаем деления на ноль

        calculated_min_qty_unrounded = self.minNotionalValue / lastPrice

        # Округляем вверх до ближайшего кратного qtyStep
        calculated_min_qty_rounded = ceil(calculated_min_qty_unrounded / self.qtyStep) * self.qtyStep

        if calculated_min_qty_rounded < self.minOrderQty:
            return self.minOrderQty
        else:
            return calculated_min_qty_rounded
        


# ---------- Торговые функции (Основные) ----------
# ----- Получение исторических цен -----
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
    
# ----- Получение реальной цены -----
    def get_ticker(self):
        data = self.session.get_tickers(
            category = self.category,
            symbol = self.symbol
        )
        return int(data["time"]), float(data["result"]["list"][0]["lastPrice"])
    
# ----- Размещение ордера -----
    def place_order(self, side: str, orderType: str, lastPrice: float=None, qty:float=None, takeProfit: float=None, stopLoss: float=None):
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
            takeProfit, stopLoss = self._caluc_TP_SL(lastPrice=lastPrice,takeProfit=takeProfit,storLoss=stopLoss)
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
            # Напиши когда-нибудь
            pass
