from pybit.unified_trading import HTTP

class ClientBybit:
    def __init__(self, ApiKey, ApiSecret):
        self.session = HTTP(
            demo=True,
            api_key=ApiKey,
            api_secret=ApiSecret,
        )