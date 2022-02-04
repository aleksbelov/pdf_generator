from fpdf import FPDF
from PIL import Image
from sqlalchemy.engine import create_engine, Engine
from sqlalchemy.sql import select

pdf_h = 297
pdf_w = 210
YEAR = 2021
TITLE_TEXT = f'Данные по государственным закупкам в области утилизации отходов за {YEAR} год'
TITLE_DATE = "29.11.2021"

DB_LOCATION = 'Tender_project_breathing.db'


class MyDB:
    e: Engine = create_engine(f'sqlite:///{DB_LOCATION}')


class MyPdf(FPDF):
    def __init__(self):
        super().__init__(orientation='P', format='A4')
        self.add_page()
        self.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
        self.add_font('DejaVuBold', '', 'DejaVuSansCondensed-Bold.ttf', uni=True)
        self.set_font('DejaVu')

    def set_title_page(self, img_path):
        # img_w, img_h = Image.open(img_path).size
        y = pdf_h * 0.1
        img_h = pdf_h * 0.3
        self.set_y(y)
        a = 0.8
        self.image(img_path, x=pdf_w*(1-a)/2, w=pdf_w*a)
        y += img_h + 7

        self.set_xy(pdf_w*(1-a)/2, y)
        self.set_font('DejaVuBold', '', 20)
        self.multi_cell(w=pdf_w*a, h=14, align='C', txt=TITLE_TEXT)

        self.set_x(pdf_w*(1-a)/2)
        self.set_font('DejaVu', '', 14)
        self.multi_cell(w=pdf_w*a, h=14, align='L', txt=TITLE_DATE)

        self.set_xy(pdf_w*0.7, pdf_h*0.8)
        self.cell(w=0, h=8, align='L', txt="Ярошенко А.В.", ln=1)
        self.set_x(pdf_w*0.7)
        self.cell(w=0, h=8, align='L', txt="artem@yaroshenko.ru", ln=1)
        self.set_x(pdf_w*0.7)
        self.cell(w=0, h=8, align='L', txt="+79162222403", ln=1)


with MyDB.e.connect() as conn:
    print(conn.execute('SELECT count(*) from Contract44_items').fetchall())


pdf = MyPdf()
pdf.set_title_page('title.jpg')

pdf.output('test.pdf', 'F')
