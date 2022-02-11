from datetime import datetime
from MyPdf import MyPdf, create_bar_fig, create_pie_fig
from db import MyDB


def main():
    pdf = MyPdf()
    pdf.set_title('title.jpg', "")

    # df_pie = MyDB.get_full_price_with_item_ktru('')
    # pdf.add_image_from_fig(create_pie_fig(df_pie))
    #
    # df_bar = MyDB.get_data_with_period(datetime(2020, 1, 1), datetime(2021, 7, 1))
    # pdf.add_image_from_fig(create_bar_fig(df_bar))

    pdf.output('test.pdf', 'F')


if __name__ == "__main__":
    main()
