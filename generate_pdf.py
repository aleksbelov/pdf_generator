from datetime import datetime
from MyPdf import MyPdf, create_total_value_bar_fig, create_pie_fig
from db import MyDB


def main():
    pdf = MyPdf()
    pdf.add_toc_entry("начало")
    pdf.set_title_img('title.jpg', "")

    df_pie = MyDB.get_full_price_with_item_ktru('32.50.13.110-00005159')
    pdf.add_image_from_fig(create_pie_fig(df_pie))
    pdf.add_toc_entry("картинка")

    # df_bar = MyDB.get_data_with_period(["32"], 2020, 2021)
    # pdf.add_image_from_fig(create_total_value_bar_fig(df_bar))

    pdf.insert_toc()
    pdf.output('test.pdf', 'F')


if __name__ == "__main__":
    main()
