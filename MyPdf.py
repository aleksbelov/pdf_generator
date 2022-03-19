import pandas as pd
from fpdf import FPDF
import plotly.express as px
from plotly.graph_objects import Figure
from os import path
from math import ceil, log10
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
H1_SIZE = 20


class MyPdf(FPDF):
    def __init__(self, toc: bool = False, toc_titles: list = None):
        super().__init__(orientation='P', format='A4')
        self.add_font(FONT, fname=path.join('fonts', 'DejaVuSansCondensed.ttf'), uni=True)
        self.add_font(FONT, fname=path.join('fonts', 'DejaVuSansCondensed-Bold.ttf'), uni=True, style="B")
        self.add_font(FONT, fname=path.join('fonts', 'DejaVuSerif-Italic.ttf'), uni=True, style="I")
        self.set_font(FONT)
        self.alias_nb_pages()

        self.toc = toc
        self.toc_titles = toc_titles
        self.toc_entries = None
        self.toc_pages_num = None
        self.toc_page_num_w = None
        self.toc_font_sz = None

        if self.toc:
            self.toc_entries = {}
            self.toc_pages_num = 1

    def setup_toc(self):
        self.toc_page_num_w = self.get_string_width(' 123')
        self.toc_font_sz = 11

        if self.toc_titles is not None:
            toc_total_lines = 2  # Большое слово "Содержание" тоже что-то занимает
            self.set_font(FONT, size=self.toc_font_sz)
            h = self.font_size
            toc_w = self.epw - self.toc_page_num_w

            for title in self.toc_titles:
                title = title.strip()
                toc_total_lines += len(self.multi_cell(w=toc_w, h=h, txt=title, align="L", split_only=True)) + 1
            self.toc_pages_num = ceil(toc_total_lines / int(self.eph / h))
            # print(f"Toc: num pages = {self.toc_pages_num}")

    def set_title_page(self, img_path: str, title_text: str):
        self.add_page()
        self.image(img_path, w=self.epw)

        self.set_font(FONT, 'B', H1_SIZE)
        self.ln(5)
        self.multi_cell(w=0, h=self.font_size * 2, align='C', txt=title_text, ln=1)

        self.set_font(FONT, '', 14)
        self.multi_cell(w=0, h=14, align='L', txt=datetime.date.today().strftime("%b-%d-%Y"), ln=1)

        self.ln(100)
        self.cell(w=0, h=8, align='R', txt="artem@yaroshenko.ru", ln=1)
        self.cell(w=0, h=8, align='R', txt="+79162222403", ln=1)

        self.add_page()

        if self.toc_entries is not None:
            self.setup_toc()
            self.insert_toc_placeholder(render_toc, pages=self.toc_pages_num)

    def add_image_from_fig(self, new_fig: Figure, title='', description=''):
        with tempfile.NamedTemporaryFile() as tmpfile:
            self.set_font(FONT, '', 10)
            if len(title) > 0:
                self.multi_cell(self.epw - 20, self.font_size, title, border=0, align="C")
            new_fig.write_image(tmpfile.name, format="png")
            self.set_x(5)
            self.image(tmpfile.name, type="png", w=self.epw)
            if len(description) > 0:
                self.multi_cell(self.epw - 20, self.font_size, description, border=0, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT, "I", size=8)
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
    pdf.cell(w=0, h=pdf.font_size*2, txt="Содержание", align="C", ln=0)

    pdf.set_font(FONT, size=pdf.toc_font_sz)
    dot_str = " ."
    h = pdf.font_size
    page_num_w = pdf.toc_page_num_w
    dot_w = pdf.get_string_width(dot_str)
    pdf_w = pdf.epw - page_num_w

    for link, (txt, page) in pdf.toc_entries.items():
        pdf.ln()

        txt = txt.strip()

        lines = pdf.multi_cell(w=pdf_w, h=h, txt=f"{txt}", link=link, align="L", split_only=True)
        dots_num = int((pdf_w - pdf.get_string_width(lines[-1])) / dot_w) - 1
        dots = dot_str * dots_num

        pdf.multi_cell(w=pdf_w, h=h, txt=f"{txt}{dots}", link=link, align="L")

        y = pdf.get_y() - h
        pdf.set_y(y)
        pdf.cell(w=0, h=h, txt=str(page), link=link, ln=1, align="R")


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


def get_value_order(x: int):
    return {1: 'тыс.',
            2: 'млн.',
            3: 'млрд.'}.get(int(log10(x)/3), '')


def get_month_name(x, short_month_name):
    if short_month_name:
        return months[x][:3]
    return months[x]


def create_volume_by_month_bar_fig(df: pd.DataFrame,
                                   title='',
                                   description='',
                                   short_month_name=True) -> Figure:
    value_label = f"Объем, {get_value_order(df['value'].max())} рублей"

    x_label = "Месяц"
    if description:
        x_label += "<br>Описание:  " + description

    df["year"] = df["year"].astype(str)
    df["month_order"] = df["year"] + df["month"].apply(lambda x: f'{x:02}')
    df["x_label"] = df['month'].apply(lambda x: get_month_name(x, short_month_name)) + ' ' + df["year"]
    df["month"] = df["month"].astype(str)
    df = df.sort_values(by=["month_order"])

    fig = px.bar(df,
                 x="x_label",
                 y="value",
                 color='country',
                 title=title,
                 labels={
                     "x_label": x_label,
                     "value": value_label,
                     "country": "Страна"
                 },
                 category_orders={
                     "x_label": df["x_label"]
                 },
                 height=650,
                 width=1100)
    fig.update_xaxes(tickangle=45)
    fig.update_yaxes(ticklabelposition="inside")

    fig.update_layout(title_x=0.5,
                      title_y=0.9,
                      font_color="black",
                      font_size=13)

    return fig
