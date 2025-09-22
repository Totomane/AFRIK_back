# backend/services/report_service.py
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
        "model": "llama-3.3-70b-versatile",  # ou "llama3-70b-8192-compat" si disponible
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 700
    }
    try:
        response = requests.post(GROQ_URL, headers=HEADERS, json=data)
        if response.status_code != 200:
            raise RuntimeError(f"Erreur API Groq: {response.text}")
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Erreur génération texte Groq: {str(e)}") from e


def generate_report_pdf(file_path: str, country: str, risks: list, year: int):
    """
    Génère un PDF Allianz-style :
    - Page de garde
    - 1 risque = 1 page
    - Structure : Contexte / Impact / Recommandations
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    margin = 2 * cm

    # === Page de garde ===
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 6 * cm, f"Rapport des Risques {year}")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width / 2, height - 8 * cm, f"Pays : {country}")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 10 * cm, f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    c.showPage()

    # === Une page par risque ===
    for risk in risks:
        prompt = (
            f"Rédige un rapport structuré façon Allianz sur le risque '{risk}' en {country} pour {year}. "
            f"Structure le texte en 3 parties claires avec titres en majuscules :\n"
            f"1. CONTEXTE ET TENDANCES\n"
            f"2. IMPACT SUR LES ENTREPRISES\n"
            f"3. RECOMMANDATIONS ET MITIGATION\n"
            f"Utilise un ton professionnel, analytique et synthétique."
        )
        try:
            content = generate_text(prompt)
        except RuntimeError as e:
            print(f"Erreur génération contenu pour '{risk}': {e}")
            content = f"⚠️ Erreur génération contenu pour le risque '{risk}': {e}"

        # === Titre de la page ===
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 2 * cm, risk.upper())
        y_position = height - 4 * cm

        # === Contenu ===
        c.setFont("Helvetica", 11)
        for line in content.split("\n"):
            if not line.strip():
                y_position -= 0.4 * cm
                continue
            wrapped_line = c.beginText(margin, y_position)
            wrapped_line.setFont("Helvetica", 11)
            wrapped_line.textLine(line.strip())
            c.drawText(wrapped_line)
            y_position -= 0.6 * cm

        c.showPage()

    c.save()
    print(f"=== PDF généré: {file_path} ===")
    return file_path
