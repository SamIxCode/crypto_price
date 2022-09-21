import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from model_currencies import *


class DbService:
    def __init__(self, settings):
        self.engine = create_engine(settings.DATABASE_URI, echo=False)
        print('done')

    def initialize_db(self):
        Base.metadata.create_all(self.engine)
        print('done1')
    def add_currency_record(self, currency_name: str = None, timestamp: int = None, price: float = None):
        timestamp = datetime.datetime.fromtimestamp(timestamp / 1e3)
        currency = Currencies(currency=currency_name, date_=timestamp, price=price)
        with Session(self.engine) as session:
            session.begin()
            try:
                session.add(currency)
            except Exception as ex:
                session.rollback()
                raise ex
            else:
                session.commit()
    def get_paginated_currencies(self, page: int, page_size: int, currency: str = None) -> list:
        offset = str(page * page_size)
        limit = str(page_size)

        with Session(self.engine) as session:
            if currency is not None:
                currencies = session.query(Currencies).filter(Currencies.currency == currency).order_by(
                    Currencies.date_.desc()).offset(offset).limit(limit).all()
            else:
                currencies = session.query(Currencies).order_by(Currencies.date_.desc()).offset(
                    offset).limit(limit).all()
        for index in range(page * page_size, (page + 1) * page_size):
            i = index - page * page_size
            if i >= len(currencies):
                break
            currencies[i].index = index + 1
        return list(currencies)

    def check_currency_presence(self, currency: str) -> bool:
        with Session(self.engine) as session:
            currencies = session.query(Currencies.currency).distinct().all()
        return currency in [x[0] for x in currencies]


