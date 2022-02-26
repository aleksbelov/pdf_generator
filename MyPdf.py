import pandas as pd
from fpdf import FPDF, HTMLMixin
import plotly.express as px
from plotly.graph_objects import Figure
from os import path
import tempfile
import datetime

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

FONT = 'DejaVu'
FONT_ITALIC = 'DejaVuItalic'
H1_SIZE = 20


class MyPdf(FPDF):
    def __init__(self, toc=False, toc_pages=1):
        super().__init__(orientation='P', format='A4')
        self.add_font('DejaVu', fname=path.join('fonts', 'DejaVuSansCondensed.ttf'), uni=True)
        self.add_font('DejaVuBold', fname=path.join('fonts', 'DejaVuSansCondensed-Bold.ttf'), uni=True)
        self.add_font('DejaVuItalic', fname=path.join('fonts', 'DejaVuSerif-Italic.ttf'), uni=True)
        self.set_font(FONT)
        self.alias_nb_pages()
        self.toc_entries = {} if toc else None
        self.toc_pages = toc_pages

    def set_title_page(self, img_path: str, title_text: str):
        self.add_page()
        self.image(img_path, w=self.epw)

        self.set_font('DejaVuBold', '', H1_SIZE)
        self.ln(5)
        self.multi_cell(w=0, h=self.font_size * 2, align='C', txt=f"Данные по государственным закупкам c "
                                                                  f"кодовыми словами {title_text}", ln=1)

        self.set_font(FONT, '', 14)
        self.multi_cell(w=0, h=14, align='L', txt=datetime.date.today().strftime("%b-%d-%Y"), ln=1)

        self.ln(100)
        self.cell(w=0, h=8, align='R', txt="artem@yaroshenko.ru", ln=1)
        self.cell(w=0, h=8, align='R', txt="+79162222403", ln=1)

        self.add_page()

        if self.toc_entries is not None:
            self.insert_toc_placeholder(render_toc, pages=self.toc_pages)

    def add_image_from_fig(self, new_fig: Figure, title='', description=''):
        with tempfile.NamedTemporaryFile() as tmpfile:
            self.set_font("DejaVu", '', 10)
            if len(title) > 0:
                self.multi_cell(self.epw - 20, self.font_size,
                                title, border=0, align="C")
            new_fig.write_image(tmpfile.name, format="png")
            self.set_x(5)
            self.image(tmpfile.name, type="png", w=self.epw)
            if len(description) > 0:
                self.multi_cell(self.epw - 20, self.font_size,
                                description, border=0, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT_ITALIC, size=8)
        self.cell(0, 10, f'Страница {self.page_no()}/' + '{nb}', 0, 1, 'C')

    def add_toc_entry(self, txt):
        if self.toc_entries is None:
            raise Exception("Unable add toc entry. Use toc=True param while calling constructor")
        if self.page < 1:
            raise Exception("Too early toc entry adding. Page = 0")
        link = self.add_link()
        self.set_link(link, page=self.page)
        self.toc_entries[link] = (txt, self.page)


def render_toc(pdf: MyPdf, _):
    pdf.set_font(FONT, size=H1_SIZE)
    pdf.cell(w=0, h=pdf.font_size*2, txt="Содержание", align="C", ln=1)

    pdf.set_font(FONT, size=11)
    for link, (txt, page) in pdf.toc_entries.items():
        txt = txt.strip()
        h = pdf.font_size
        pdf_w = pdf.epw
        text_w = pdf.get_string_width(txt + ' ')
        page_num_w = pdf.get_string_width(' 123')
        dot_w = pdf.get_string_width(". ")
        # print(pdf_w, text_w, dot_w, page_num_w, text_w % pdf_w, pdf_w - text_w % pdf_w - page_num_w)
        dots_num = int((pdf_w - ((text_w*1.05) % pdf_w) - page_num_w)/dot_w)
        dots = " ." * dots_num
        # print(pdf_w, (text_w % pdf_w) + pdf.get_string_width(dots))
        y = pdf.get_y() + h * int(text_w // pdf_w)
        pdf.multi_cell(w=pdf_w - page_num_w, h=h, txt=f"{txt}{dots}", link=link, align="L")
        pdf.set_y(y)
        pdf.cell(w=0, h=h, txt=str(page), link=link, ln=1, align="R")
        pdf.ln()
        # print("done", txt)


def merge_minorities(df: pd.DataFrame) -> pd.DataFrame:
    value_percentage = df["value"] / df["value"].sum()

    others_money = df[value_percentage < 0.01]["value"].sum()
    df.drop(df[value_percentage < 0.01].index, inplace=True)
    df = pd.concat([df, pd.DataFrame({"name": ["ДРУГИЕ (< 1%)"], "value": [others_money]})],
                   ignore_index=True)
    return df


def create_pie_fig(df: pd.DataFrame, year_start=0, year_finish=0, title_info='', description='') -> Figure:
    global colors

    title_text = "Распределение по странам "
    if title_info:
        title_text += "для " + title_info + ' '

    title_text += f"за {year_start}-{year_finish} года"

    df = merge_minorities(df)

    # russia_idx = df[df["name"].str.startswith('Росс')].index.tolist()
    # russia_idx = russia_idx[0] if russia_idx else None
    russia_idx = -1
    for i in range(len(df)):
        if df.at[i, "name"].find("Росс") != -1:
            russia_idx = i

    fig: Figure = px.pie(df,
                         values='value',
                         names='name',
                         title=title_text,
                         hole=0.45,
                         height=650,
                         width=1100)
    fig.update_layout(title_x=0.5,
                      title={"font": {"size": H1_SIZE, "family": FONT, "color": '#000000'}},
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

    if russia_idx != -1:
        pull = [0] * len(df)
        pull[russia_idx] = 0.1

        colors = [None] * len(df)
        colors[russia_idx] = "#00008B"
        fig.update_traces(pull=pull, marker=dict(colors=colors))

    return fig


def create_total_value_bar_fig(df: pd.DataFrame) -> Figure:
    value_label = "Объем рублей"

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
                 height=650,
                 width=1100)
    fig.update_yaxes(ticklabelposition="inside")
    fig.update_layout(title_x=0.5,
                      title={"font": {"size": 20, "family": FONT, "color": '#000000'}},
                      font_color="black",
                      font_size=14)
    fig.update_traces(textfont_size=20,
                      textfont_color='#000000')
    return fig


def create_value_bar_fig_by_month_country(df: pd.DataFrame, title_info='', description='') -> Figure:
    value_label = "Объем"
    if df["value"].max() / 1000000000 >= 1:
        value_label += ", млрд. Рублей"
    elif df["value"].max() / 1000000 >= 1:
        value_label += ", млн. Рублей"
    elif df["value"].max() / 1000 >= 1:
        value_label += ", тыс. Рублей"
    else:
        value_label += ", Рублей"

    title_text = ''
    if title_info:
        title_text = " для " + title_info
    fig = px.bar(df,
                 x="date",
                 y="value",
                 color='country',
                 category_orders={
                     "year": df["year"].sort_values().unique(),
                     "month": months.values()
                 },
                 labels={
                     "country": "Страна",
                     "date": "Месяц",
                     "value": value_label
                 },
                 height=650,
                 width=1100)
    fig.update_yaxes(ticklabelposition="inside")
    fig.update_layout(  # title_x=0.5,
        # title={"font": {"size": 20, "family": FONT, "color": '#000000'}},
        font_color="black",
        font_size=14,
        margin=dict(l=30, r=30, t=5, b=20))
    fig.update_traces(textfont_size=20,
                      textfont_color='#000000')

    if len(description) > 0:
        fig.add_annotation(
            xref="x domain", yref="y domain",
            x=-0.1, y=-0.2,
            text="Описание: " + description,
            showarrow=False,
            font=dict(
                color="black",
                size=20))

    return fig
