import pandas as pd

from MyPdf import MyPdf, create_volume_by_month_bar_fig, create_pie_fig
from db import MyDB


N = 0
d = 6


def gen_toc_titles():
    titles = ["картинка", "ещё"]
    for i in range(N):
        titles.append("и ещё "*(20 + d*i))
    return titles


def get_df_from_bad_csv():
    df = pd.read_csv('bad_dataframe.csv',
                     names=['value', 'country', 'date'],
                     dtype={'value': int, 'country': str, 'date': str})
    df['month'] = df['date'].str.split('.', expand=True)[0].astype(int)
    df['year'] = df['date'].str.split('.', expand=True)[1].astype(int)
    return df


def main():
    pdf = MyPdf(toc=True, toc_titles=gen_toc_titles())
    pdf.set_title_page('title.jpg', "Данные по государственным закупкам c кодовыми словами")

    df_pie = MyDB.get_full_price_with_item_ktru('32.50.13.110-00005159')
    pdf.add_image_from_fig(create_pie_fig(df_pie))
    pdf.add_toc_entry("картинка")

    # df_bar = MyDB.get_data_with_period(["32"], 2020, 2021)
    df_bar = get_df_from_bad_csv()

    img = create_volume_by_month_bar_fig(df_bar, description='описание '*10)

    pdf.add_image_from_fig(img)
    pdf.add_toc_entry("ещё")
    for i in range(N):
        pdf.add_image_from_fig(img)
        pdf.add_toc_entry("и ещё "*(20 + d*i))

    pdf.output('test.pdf', 'F')


if __name__ == "__main__":
    main()
