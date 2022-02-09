from sqlalchemy.engine import create_engine, Engine
import pandas as pd
from datetime import datetime


DB_LOCATION = 'Tender_project.db'


class MyDB:
    e: Engine = create_engine(f'sqlite:///{DB_LOCATION}')

    @staticmethod
    def get_full_price_with_item_ktru(item_ktru_like: str) -> pd.DataFrame:
        df = pd.read_sql(
            "select sum(item_full_price_in_order) as value, "
            "case when item_country like '%\n%' then trim(substr(item_country, 0, instr(item_country, '\n'))) "
            "else trim(item_country) end as name "
            "from Contract44_items "
            f"where item_ktru like '%{item_ktru_like}%' and name <> '' "
            "group by name",
            con=MyDB.e,
        )

        print(df)

        def clean_country(s: str):
            if '\n' in s:
                return s.split('\n')[0].strip()
            else:
                return s.strip()

        df["name"] = df["name"].apply(clean_country)

        value_percentage = df["value"] / df["value"].sum()

        others_money = df[value_percentage < 0.01]["value"].sum()
        df.drop(df[value_percentage < 0.01].index, inplace=True)
        df = pd.concat([df, pd.DataFrame({"name": ["ДРУГИЕ (< 1%)"], "value": [others_money]})],
                       ignore_index=True)
        # print(df)

        return df

    @staticmethod
    def get_data_with_period(begin: datetime, end: datetime) -> pd.DataFrame:
        """
        Day will be ignored
        :param begin:
        :param end:
        :return:
        """
        def d1_less_than_d2(d1: datetime, d2: datetime):
            return (d2.year - d1.year)*12 + (d2.month - d1.month) >= 0

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
