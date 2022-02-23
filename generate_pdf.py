from MyPdf import MyPdf, create_total_value_bar_fig, create_pie_fig
from db import MyDB


def main():
    pdf = MyPdf(toc=True)
    pdf.set_title_page('title.jpg', "")

    df_pie = MyDB.get_full_price_with_item_ktru('32.50.13.110-00005159')
    pdf.add_image_from_fig(create_pie_fig(df_pie))
    pdf.add_toc_entry("картинка")

    df_bar = MyDB.get_data_with_period(["32"], 2020, 2021)

    img = create_total_value_bar_fig(df_bar)

    pdf.add_image_from_fig(img)
    pdf.add_toc_entry("ещё")
    for _ in range(40):
        pdf.add_image_from_fig(img)
        pdf.add_toc_entry("и ещё")

    pdf.output('test.pdf', 'F')


if __name__ == "__main__":
    main()
