# pip install reportlab
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

buf = io.BytesIO()
c = canvas.Canvas(buf, pagesize=letter)
width, height = letter

x_margin = 72
y = height - x_margin
line_height = 14
font_name = "Helvetica"
font_size = 11
max_width = width - 2 * x_margin

def data_for_pdf(data):

    for line in data.splitlines():
        wrapped = simpleSplit(line, font_name, font_size, max_width)
        for w in wrapped:
            if y < x_margin:
                c.showPage()
                y = height - x_margin
            c.setFont(font_name, font_size)
            c.drawString(x_margin, y, w)
            y -= line_height

    c.save()
    return buf.getvalue()

