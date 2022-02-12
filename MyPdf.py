import pandas as pd
from fpdf import FPDF
import plotly.express as px
from plotly.graph_objects import Figure
from os import path
import tempfile
import datetime


pdf_h = 297
pdf_w = 210
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

colors = ['rgb(139, 0, 0)',
         'rgb(0, 250, 154)',
         'rgb(32, 178, 170)',
        'rgb(95, 158, 160)',
        'rgb(218, 112, 214)',
        'rgb(70, 130, 180)',
        'rgb(123, 104, 238)',
        'rgb(255, 215, 0)',
        'rgb(75, 0, 130)',
        'rgb(128, 128, 128)',
        'rgb(0, 128, 0)',
        'rgb(0, 255, 255)',
        'rgb(0, 0, 255)',
          'rgb(255, 250, 205)',
          'rgb(250, 250, 210)',
          'rgb(255, 239, 213)',
        ]


class MyPdf(FPDF):
    def __init__(self):
        super().__init__(orientation='P', format='A4')
        self.add_page()
        self.add_font('DejaVu', '', path.join('fonts', 'DejaVuSansCondensed.ttf'), uni=True)
        self.add_font('DejaVuBold', '', path.join('fonts', 'DejaVuSansCondensed-Bold.ttf'), uni=True)
        self.add_font('DejaVuItalic', '', path.join('fonts', 'DejaVuSerif-Italic.ttf'), uni=True)
        self.set_font(FONT)
        self.alias_nb_pages()

    def set_title(self, img_path: str, title_text: str):
        y = pdf_h * 0.1
        img_h = pdf_h * 0.3
        self.set_y(y)
        a = 0.8
        self.image(img_path, x=pdf_w * (1 - a) / 2, w=pdf_w * a)
        y += img_h + 7

        self.set_xy(pdf_w * (1 - a) / 2, y)
        self.set_font('DejaVuBold', '', 20)
        self.multi_cell(w=pdf_w * a, h=14, align='C', txt=f"Данные по государственным закупкам c "
                                                          f"кодовыми словами {title_text}")

        self.set_x(pdf_w * (1 - a) / 2)
        self.set_font('DejaVu', '', 14)
        self.multi_cell(w=pdf_w * a, h=14, align='L', txt=datetime.date.today().strftime("%b-%d-%Y"))

        self.set_xy(pdf_w * 0.7, pdf_h * 0.8)
        # self.cell(w=0, h=8, align='L', txt="Ярошенко А.В.", ln=1)
        # self.set_x(pdf_w * 0.7)
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


def create_pie_fig(df: pd.DataFrame, year_start=0, year_finish=0, title_info='', description='') -> Figure:
    global colors

    title_text = "Распределение по странам "
    if title_info:
        title_text += "для " + title_info + ' '

    title_text += f"за {year_start}-{year_finish} года"

    value_percentage = df["value"] / df["value"].sum()

    others_money = df[value_percentage < 0.01]["value"].sum()
    df.drop(df[value_percentage < 0.01].index, inplace=True)
    df = pd.concat([df, pd.DataFrame({"name": ["ДРУГИЕ (< 1%)"], "value": [others_money]})],
                   ignore_index=True)
    # print(df)

    russia_idx = df[df["name"].str.startswith('Росс')].index.tolist()
    russia_idx = russia_idx[0] if russia_idx else None

    fig: Figure = px.pie(df,
                         values='value',
                         names='name',
                         title=title_text,
                         hole=0.45,
                         height=700,
                         width=1100)
    fig.update_layout(title_x=0.5,
                      title={"font": {"size": 20, "family": FONT, "color": '#000000'}},
                      annotations=[dict(text=f'{df["value"].sum():,} р.',
                                        showarrow=False,
                                        x=0.5,
                                        y=0.5,
                                        font_size=18)],
                      font_color="black",
                      font_size=14)
    fig.update_traces(textfont_size=20,
                      textposition='inside',
                      marker=dict(colors=colors, line=dict(color='#000000', width=1)))

    if len(description) > 0:
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=-0.1, y=-0.1,
            text="Описание: " + description,
            showarrow=False,
            font=dict(
                color="black",
                size=20))

    if russia_idx is not None:
        pull = [0] * len(df)
        pull[russia_idx] = 0.1

        colors = [None] * len(df)
        colors[russia_idx] = "red"
        fig.update_traces(pull=pull, marker=dict(colors=colors))

    return fig


def create_total_value_bar_fig(df: pd.DataFrame) -> Figure:
    value_label = "Объем"
    if df["value"].max() / 1000000000 >= 1:
        value_label += ", млрд. р."
    else:
        value_label += ", млн. р."
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
                 height=700,
                 width=1100)
    fig.update_yaxes(ticklabelposition="inside")
    fig.update_layout(title_x=0.5,
                      title={"font": {"size": 20, "family": FONT, "color": '#000000'}},
                      font_color="black",
                      font_size=14)
    fig.update_traces(textfont_size=20,
                      textfont_color= '#000000')
    return fig


def create_value_bar_fig_by_month_country(df: pd.DataFrame, title_info='', description='') -> Figure:
    value_label = "Объем"
    if df["value"].max() / 1000000000 >= 1:
        value_label += ", млрд. Р."
    elif df["value"].max() / 1000000 >= 1:
        value_label += ", млн. Р."
    elif df["value"].max() / 1000 >= 1:
        value_label += ", тыс. Р."
    else:
        value_label += ", Р."
    fig = px.bar(df,
                 x="date",
                 y="value",
                 title=f"Объем закупок для {title_info}",
                 color='name',
                 labels={
                     "name": "Страна",
                     "date": "Месяц",
                     "value": value_label
                 },
                 height=700,
                 width=1100)
    fig.update_yaxes(ticklabelposition="inside")
    fig.update_layout(title_x=0.5,
                      title={"font": {"size": 20, "family": FONT, "color": '#000000'}},
                      font_color="black",
                      font_size=14)
    fig.update_traces(textfont_size=20,
                      textfont_color= '#000000')

    if len(description) > 0:
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=-0.1, y=-0.1,
            text="Описание: " + description,
            showarrow=False,
            font=dict(
                color="black",
                size=20))

    return fig
