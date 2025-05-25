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
        