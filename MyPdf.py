import pandas as pd
from fpdf import FPDF
import plotly.express as px
from plotly.graph_objects import Figure
from os import path
import tempfile


pdf_h = 297
pdf_w = 210
YEAR = 2021
TITLE_TEXT = f'Данные по государственным закупкам в области утилизации отходов за {YEAR} год'
TITLE_DATE = "29.11.2021"
FONT = 'DejaVu'
FONT_ITALIC = 'DejaVuItalic'

months = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}


class MyPdf(FPDF):
    def __init__(self):
        super().__init__(orientation='P', format='A4')
        self.add_page()
        self.add_font('DejaVu', '', path.join('fonts', 'DejaVuSansCondensed.ttf'), uni=True)
        self.add_font('DejaVuBold', '', path.join('fonts', 'DejaVuSansCondensed-Bold.ttf'), uni=True)
        self.add_font('DejaVuItalic', '', path.join('fonts', 'DejaVuSerif-Italic.ttf'), uni=True)
        self.set_font(FONT)
        self.alias_nb_pages()

    def set_title_img(self, img_path: str):
        y = pdf_h * 0.1
        img_h = pdf_h * 0.3
        self.set_y(y)
        a = 0.8
        self.image(img_path, x=pdf_w * (1 - a) / 2, w=pdf_w * a)
        y += img_h + 7

        self.set_xy(pdf_w * (1 - a) / 2, y)
        self.set_font('DejaVuBold', '', 20)
        self.multi_cell(w=pdf_w * a, h=14, align='C', txt=TITLE_TEXT)

        self.set_x(pdf_w * (1 - a) / 2)
        self.set_font('DejaVu', '', 14)
        self.multi_cell(w=pdf_w * a, h=14, align='L', txt=TITLE_DATE)

        # self.set_y(pdf_h * 0.5)
        # self.image('title_bottom.png', x=pdf_w * (1 - a) / 2, w=pdf_w * a)

        self.set_xy(pdf_w * 0.7, pdf_h * 0.8)
        self.cell(w=0, h=8, align='L', txt="Ярошенко А.В.", ln=1)
        self.set_x(pdf_w * 0.7)
        self.cell(w=0, h=8, align='L', txt="artem@yaroshenko.ru", ln=1)
        self.set_x(pdf_w * 0.7)
        self.cell(w=0, h=8, align='L', txt="+79162222403", ln=1)

        self.add_page()
        self.set_x(0)

    def add_image_from_fig(self, new_fig: Figure):
        with tempfile.NamedTemporaryFile() as tmpfile:
            new_fig.write_image(tmpfile.name, format="png")
            self.image(tmpfile.name, type="png", w=pdf_w * 0.98)

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT_ITALIC, size=8)
        self.cell(0, 10, 'Страница %s' % self.page_no() + '/{nb}', 0, 0, 'C')


def create_pie_fig(df: pd.DataFrame) -> Figure:
    russia_idx = df[df["name"].str.startswith('РОССИЯ')].index.tolist()
    russia_idx = russia_idx[0] if russia_idx else None

    fig: Figure = px.pie(df,
                         values='value',
                         names='name',
                         title='Распределение по странам',
                         hole=0.45,
                         height=600,
                         width=1100)
    fig.update_layout(title_x=0.5,
                      title={"font": {"size": 40, "family": FONT, "color": '#000000'}},
                      annotations=[dict(text=f'{df["value"].sum():,} р.',
                                        showarrow=False,
                                        x=0.5,
                                        y=0.5,
                                        font_size=18)])
    fig.update_traces(textfont_size=24)

    if russia_idx is not None:
        pull = [0] * len(df)
        pull[russia_idx] = 0.1

        colors = [None] * len(df)
        colors[russia_idx] = "red"
        fig.update_traces(pull=pull, marker=dict(colors=colors))

    return fig


def create_bar_fig(df: pd.DataFrame) -> Figure:
    value_label = "Объем"
    if df["value"].max() / 1000000000 >= 1:
        value_label += ", млрд. р."
    else:
        value_label += "млн. р."
    df["month"] = df["month"].astype(str)
    df["year"] = df["year"].astype(str)
    df["month"] = df['month'].apply(lambda x: months[int(x)])
    fig = px.bar(df,
                 x="year",
                 y="value",
                 title="Объем по годам и месяцам",
                 color='month',
                 category_orders={
                     "year": df["year"].sort_values().unique(),
                     "month": months.values()
                 },
                 labels={
                     "month": "Месяц",
                     "year": "Год",
                     "value": value_label
                 },
                 height=600,
                 width=1100)
    fig.update_yaxes(ticklabelposition="inside")
    fig.update_layout(title_x=0.5,
                      title={"font": {"size": 40, "family": FONT, "color": '#000000'}})
    return fig
