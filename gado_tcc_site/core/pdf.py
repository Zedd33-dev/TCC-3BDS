from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def simple_table_pdf(title: str, headers: list[str], rows: list[list[str]]):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    y = height - 2*cm

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y, title)
    y -= 1.2*cm

    c.setFont("Helvetica-Bold", 9)
    x0 = 2*cm
    col_w = (width - 4*cm) / max(1, len(headers))
    for i, h in enumerate(headers):
        c.drawString(x0 + i*col_w, y, str(h)[:40])
    y -= 0.6*cm

    c.setFont("Helvetica", 9)
    for r in rows:
        if y < 2*cm:
            c.showPage()
            y = height - 2*cm
        for i, cell in enumerate(r):
            c.drawString(x0 + i*col_w, y, str(cell)[:45])
        y -= 0.5*cm

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()
