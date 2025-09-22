# services/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_pdf(file_path, country, risks, year):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, height - 100, f"Risk Report: {country} ({year})")

    c.setFont("Helvetica", 14)
    c.drawString(100, height - 150, "Risks Identified:")

    y = height - 180
    for risk in risks:
        c.drawString(120, y, f"- {risk}")
        y -= 20

    c.save()
