
import logging
from aiohttp import web
import aiohttp_jinja2
import ccxt
from abc import ABC
from ccxt.base.errors import BadSymbol
import asyncio

from DBsevice import DbService

logging.basicConfig(filename='logs/app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.WARNING)


#currency=('Bitcoin')

class BaseHandler(ABC):
    def __init__(self, settings):
        self.settings = settings
        self.db_service=DbService(settings)
        
    @staticmethod
    def parse_relevant_data(currency_id, currency_name, ticker):
        result = dict()
        result["id"] = currency_id
        result["name"] = currency_name
        result["symbol"] = ticker["symbol"]
        result["last_bid"] = ticker["bid"]
        return result
        
        
    @staticmethod
    def get_currencyID(currency):
        kucoin=ccxt.kucoin()
        currencies=(kucoin.fetchCurrencies())
        try:
            currency_info={"id":[],"name":[]}
            for key in currencies :
                if currency == currencies[key]["id"] or currency == currencies[key]["name"]:
                    currency_id=currencies[key]["id"]
                    currency_name=currencies[key]["name"]
                    currency_info["id"].append(currency_id)
                    currency_info["name"].append(currency_name)
                    return currency_info
            
        except:
            raise BadSymbol

               
    
    def get_data(self,currency):
        kucoin=ccxt.kucoin()

        
        currency_info=self.get_currencyID(currency)
        def get_currency_id():
            c_id = currency_info["id"]
            for i in c_id:
                return i
        def get_currency_name():
            c_name = currency_info["name"]
            for i in c_name:
                return i
    
        currency_id = get_currency_id()
        currency_name= get_currency_name()

        symbol = (f"{currency_id}/USDT")   
        print(symbol)
        response = []
        try:
            ticker = kucoin.fetch_ticker(symbol)
            #relevant_data=(currency_id, currency_name, ticker["bid"], ticker['timestamp'])
            response.append(self.parse_relevant_data(currency_id,currency_name,ticker))
            self.db_service.add_currency_record(currency_name=currency_id, timestamp=ticker["timestamp"], price=ticker["bid"])
            return response
    
    

        except BadSymbol:
            logging.warning(f"Unknown symbol {symbol}")
    
class MainHandler(BaseHandler):
    def __init__(self, settings):
        super().__init__(settings)

    async def handle(self, request):
        history = "history" == request.match_info.get('currency') and "page" in request.rel_url.query
        if history:
            return await self.get_history_paginated(request)
        return await self.get_data(request)

    @aiohttp_jinja2.template('last_bid.html')
    async def get_data(self, request):
        currency = request.match_info.get('currency')
        response = super().get_data(currency)
        return {
            "response": response
        }

    @aiohttp_jinja2.template('history.html')
    async def get_history_paginated(self, request):
        page = None if "page" not in request.rel_url.query else request.rel_url.query["page"]
        currency = None if "currency" not in request.rel_url.query else request.rel_url.query["currency"]
        currencies = await super().history_paginated(page, currency)
        currencies = [x.json() for x in currencies]
        page = int(page)
        next_page = self.db_service.get_paginated_currencies(page, self.settings.PAGE_SIZE, currency)

        return {
            "current_page": page,
            "previous_page": page - 1 if page > 0 else -1,
            "next_page": page + 1 if len(next_page) > 0 else -1,
            "currency": currency,
            "currencies": currencies
        }


class ApiHandler(BaseHandler):
    def __init__(self, settings):
        super().__init__(settings)

    async def handle(self, request):
        history = "history" == request.match_info.get('currency') and "page" in request.rel_url.query
        if history:
            return await self.get_history_paginated(request)
        return await self.get_data(request)

    async def get_data(self, request):
        currency = request.match_info.get('currency')
        response = super().get_data(currency)
        if len(response) == 0:
            return web.json_response({"error": f"No known bids for {currency}/USDT"})

        return web.json_response(response)

    async def get_history_paginated(self, request):
        page = None if "page" not in request.rel_url.query else request.rel_url.query["page"]
        currency = None if "currency" not in request.rel_url.query else request.rel_url.query["currency"]
        currencies = await super().history_paginated(page, currency)
        currencies = [x.json() for x in currencies]

        return web.json_response(currencies)


