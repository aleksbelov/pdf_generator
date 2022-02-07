from fpdf import FPDF
import plotly.express as px
from plotly.graph_objects import Figure
import plotly.graph_objects as go
import tempfile

from db import MyDB

pdf_h = 297
pdf_w = 210
YEAR = 2021
TITLE_TEXT = f'Данные по государственным закупкам в области утилизации отходов за {YEAR} год'
TITLE_DATE = "29.11.2021"
FONT = 'DejaVu'


class MyPdf(FPDF):
    def __init__(self):
        super().__init__(orientation='P', format='A4')
        self.add_page()
        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        self.add_font('DejaVuBold', '', 'DejaVuSansCondensed-Bold.ttf', uni=True)
        self.set_font(FONT)

    def set_title_page(self, img_path):
        # img_w, img_h = Image.open(img_path).size
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

    def add_image_from_fig(self, new_fig: Figure):
        with tempfile.NamedTemporaryFile() as tmpfile:
            new_fig.write_image(tmpfile.name, format="png")
            self.add_page()
            self.set_x(0)
            self.image(tmpfile.name, type="png", w=pdf_w * 0.98)


def create_fig_for():
    df = MyDB.get_full_price_with_item_ktru_by_country('специального')

    russia_idx = df[df["name"].str.startswith('РОССИЯ')].index.tolist()
    russia_idx = russia_idx[0] if russia_idx else None

    fig: Figure = px.pie(df,
                         values='value',
                         names='name',
                         title='Распределение по странам',
                         hole=0.3,
                         height=600,
                         width=1100)
    fig.update_layout(title_x=0.5,
                      title={"font": {"size": 40, "family": FONT, "color": '#000000'}},
                      annotations=[dict(text=str(df["value"].sum()),
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


def main():
    pdf = MyPdf()
    pdf.set_title_page('title.jpg')
    pdf.add_image_from_fig(create_fig_for())
    pdf.output('test.pdf', 'F')


if __name__ == "__main__":
    main()
