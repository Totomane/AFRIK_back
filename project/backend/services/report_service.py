# services/report_service.py
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# Charger clé API depuis .env
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("⚠️ Clé API Groq manquante ! Ajoute GROQ_API_KEY=.env")

# API Groq
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


def generate_text(prompt: str) -> str:
    """
    Génère du texte via l'API Groq.
    """
    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 700
    }
    response = requests.post(GROQ_URL, headers=HEADERS, json=data)

    if response.status_code != 200:
        raise RuntimeError(f"Erreur API Groq: {response.text}")

    return response.json()["choices"][0]["message"]["content"]


def generate_report_pdf(file_path: str, country: str, risks: list, year: int):
    """
    Génère un PDF basé sur les risques, pays et année.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    margin = 2 * cm
    y_position = height - margin

    # Titre principal
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y_position, f"Rapport sur les risques pour {country} ({year})")
    y_position -= 1 * cm
    c.setFont("Helvetica", 10)
    c.drawString(margin, y_position, f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    y_position -= 1.5 * cm

    for risk in risks:
        # Récupérer texte via Groq
        prompt = (
            f"Rédige un rapport détaillé sur le risque '{risk}' pour {country} "
            f"avec un objectif temps de {year}. Inclure tendances, impacts potentiels et recommandations."
        )
        content = generate_text(prompt)

        # Ajouter titre de section
        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y_position, risk)
        y_position -= 1 * cm

        # Ajouter contenu
        c.setFont("Helvetica", 11)
        for line in content.split("\n"):
            wrapped_line = c.beginText(margin, y_position)
            wrapped_line.setFont("Helvetica", 11)
            wrapped_line.textLine(line)
            c.drawText(wrapped_line)
            y_position -= 0.5 * cm

            # Saut de page si on atteint le bas
            if y_position < margin:
                c.showPage()
                y_position = height - margin

        y_position -= 1 * cm  # Espacement après chaque section

    c.save()
    return file_path
