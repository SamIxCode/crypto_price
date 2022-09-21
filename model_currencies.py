from sqlalchemy import Column, Integer, String, MetaData, DECIMAL, TIMESTAMP
from sqlalchemy.orm import declarative_base

meta = MetaData()
Base = declarative_base()


class Currencies(Base):
    __tablename__ = "currencies"

    id = Column('id', Integer, primary_key=True)
    currency = Column('currency', String)
    date_ = Column('date_', TIMESTAMP)
    price = Column('price', DECIMAL)

    index = -1

    def __str__(self):
        return f"{self.date_} - {self.currency} : {self.price}"

    def json(self):
        return {
            "index": self.index,
            "name": self.currency,
            "date": str(self.date_),
            "price": float(self.price)
        }

