from sqlalchemy.engine import create_engine, Engine
import pandas as pd

DB_LOCATION = 'RusTenderDataBase.db'


def where_request_part_for_code_words(code_frases: list) -> str:
    query_text = """ WHERE ("""
    k = 0
    for code_frase in code_frases:
        k+=1
        code_words_untreated = code_frase.strip().split(" ")

        code_words = []
        for code_word in code_words_untreated:
            code_words.append(code_word.lower())
            code_words.append(code_word[0].upper() + code_word[1:].lower())

        # Формируем параметры запроса (WHERE)

        query_text += """("""
        for i in range(len(code_words) // 2):
            if i != 0:
                query_text += " AND "
            query_text += """(Products.KTRUname LIKE "%""" + code_words[2 * i] + """%" OR Products.KTRUname LIKE "%""" + code_words[
                2 * i + 1] + """%")"""

        query_text += """)"""

        query_text += """ OR """

        query_text += """("""
        for i in range(len(code_words) // 2):
            if i != 0:
                query_text += " AND "
            query_text += """(Products.name LIKE "%""" + code_words[2 * i] + """%" OR Products.name LIKE "%""" + code_words[
                2 * i + 1] + """%")"""

        query_text += """)"""
        if k != len(code_frases):
            query_text += """ OR """

    query_text += """)"""
    return query_text


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
    def get_data_with_period(code_words: list, year_start: int, year_finish: int) -> pd.DataFrame:
        return pd.read_sql(f"""SELECT
                                SUM(Products.sumRUR) as value,
                                C.publishMonth as month,
                                C.publishYear as year
                            FROM Products
                            INNER JOIN Contracts C on Products.contractId = C.id
                            {where_request_part_for_code_words(code_words)} 
                            AND year <= {year_finish} AND year >= {year_start} 
                            GROUP BY year, month
                            ORDER BY year, month""",
                           con=MyDB.e
                           )
