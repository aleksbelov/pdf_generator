from sqlalchemy.engine import create_engine, Engine
import pandas as pd
from datetime import datetime

DB_LOCATION = 'RusTenderDataBase.db'


class MyDB:
    e: Engine = create_engine(f'sqlite:///{DB_LOCATION}')

    @staticmethod
    def get_full_price_with_item_ktru(ktru_code: str) -> pd.DataFrame:
        return pd.read_sql(
            "SELECT sum(Products.sumRUR) as value, C2.countryFullName as name "
            "from Products "
            "INNER JOIN Contracts C on Products.contractId = C.id "
            "INNER JOIN Countries C2 on C2.countryCode = Products.countryCode "
            f"where KTRUcode = '{ktru_code}' "
            "group by C2.countryFullName",
            con=MyDB.e,
        )

    @staticmethod
    def get_data_with_period(begin: datetime, end: datetime) -> pd.DataFrame:
        """
        Day will be ignored
        :param begin:
        :param end:
        :return:
        """

        def d1_less_than_d2(d1: datetime, d2: datetime):
            return (d2.year - d1.year) * 12 + (d2.month - d1.month) >= 0

        def d_between(d):
            d_datetime = datetime(d["year"], d["month"], 1)
            return d1_less_than_d2(begin, d_datetime) and d1_less_than_d2(d_datetime, end)

        df = pd.read_sql(
            "select sum(item.item_full_price_in_order) as value, c.mounth as month, c.year "
            "from Contract44_items item inner join Contracts_44fz c on c.id == item.contract "
            "group by year, month "
            "order by year, month",
            con=MyDB.e
        )
        df = df[df.apply(d_between, axis=1)]

        return df
