import asyncio

async def temporary_order(IdOrder: int, closingTimer: int, bb):
    '''Следит за ордером и отменяет его, если он не исполнен через заданное время.'''
    await asyncio.sleep(closingTimer)

    # Получаем статус ордера
    dataOrder = bb.info_OrderId(IdOrder)
    status = dataOrder["result"]["list"][0]["orderStatus"]
    print(status)

    if status in ("Unfilled", "PartiallyFilled"):
        res = bb.cancel_order(IdOrder)
        print("ордер отменён")

async def temporary_position(IdOrder: int, closingTimer: int, bb):
    await asyncio.sleep(closingTimer)

    # Получаем статус позиции
    dataPosition = bb.info_position()
    size = float(dataPosition["result"]["list"][0]["size"])
    side = dataPosition["result"]["list"][0]["side"]

    if size > 0:
        # Закрытие сделки, тем что мы выкупаем её
        opposite_side = "Sell" if side == "Buy" else "Buy"
        result = bb.cancel_position(size, opposite_side)
        print(result)
