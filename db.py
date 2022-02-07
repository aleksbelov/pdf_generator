from sqlalchemy.engine import create_engine, Engine
import pandas as pd

DB_LOCATION = 'Tender_project.db'


class MyDB:
    e: Engine = create_engine(f'sqlite:///{DB_LOCATION}')

    @staticmethod
    def get_full_price_with_item_ktru_by_country(item_ktru_like):
        df = pd.read_sql(
            "select sum(item_full_price_in_order) as value, item_country as name from Contract44_items "
            f"where item_ktru like '%{item_ktru_like}%' and name <> '' group by item_country",
            con=MyDB.e,
        )
        # print(df)

        value_percentage = df["value"] / df["value"].sum()

        others_money = df[value_percentage < 0.01]["value"].sum()
        df.drop(df[value_percentage < 0.01].index, inplace=True)
        df = pd.concat([df, pd.DataFrame({"name": ["ДРУГИЕ (< 1%)"], "value": [others_money]})],
                       ignore_index=True)
        # print(df)

        return df
