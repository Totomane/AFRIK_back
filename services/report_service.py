# backend/services/report_service.py
import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import time
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white, darkblue, lightgrey
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# Charger clé API depuis .env
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("⚠️ Clé API Groq manquante ! Ajoute GROQ_API_KEY=.env")

# Configuration optimisée
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
REQUEST_DELAY = int(os.getenv("GROQ_REQUEST_DELAY", "2"))  # Réduit à 2s
MAX_RETRIES = int(os.getenv("GROQ_MAX_RETRIES", "3"))

# --- NEW: verified source utilities ---
from functools import lru_cache
from typing import Dict, Tuple, Optional, List

WB_BASE = "https://api.worldbank.org/v2"
IMF_BASE = "https://dataservices.imf.org/REST/SDMX_JSON.svc"


# Common World Bank indicators
WB_INDICATORS = {
    "gdp_usd": "NY.GDP.MKTP.CD",          # GDP (current US$)
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",    # GDP growth (annual %)
    "inflation": "FP.CPI.TOTL.ZG",        # Inflation, consumer prices (annual %)
    "unemployment": "SL.UEM.TOTL.ZS",     # Unemployment (% of labor force)
    "population": "SP.POP.TOTL",          # Total population
}

@lru_cache(maxsize=512)
def fetch_world_bank_indicator(country_iso3: str, indicator: str, year: int) -> Optional[Tuple[float, str]]:
    """
    Returns (value, source_tag) for a WB indicator at a given year.
    source_tag example: 'WB:NY.GDP.MKTP.CD 2024'
    """
    url = f"{WB_BASE}/country/{country_iso3}/indicator/{indicator}?date={year}:{year}&format=json&per_page=1"
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return None
    payload = r.json()
    if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
        return None
    row = payload[1][0]
    val, date = row.get("value"), row.get("date")
    if val is None:         
        return None
    try:
        return float(val), f"WB:{indicator} {date}"
    except Exception:
        return None

@lru_cache(maxsize=512)
def fetch_imf_series(dataset: str, key: str, year: int) -> Optional[Tuple[float, str]]:
    """
    Generic IMF SDMX fetcher (optional). Example key for IFS: 'A.MA.PCPI_IX'
    Returns (value, 'IMF:DATASET:KEY YEAR') or None.
    """
    url = f"{IMF_BASE}/CompactData/{dataset}/{key}"
    r = requests.get(url, params={"startPeriod": str(year), "endPeriod": str(year)}, timeout=30)
    if r.status_code != 200:
        return None
    data = r.json().get("CompactData", {})
    series_list = data.get(dataset, [])
    if not series_list:
        return None
    obs = series_list[0].get("Obs")
    if not obs:
        return None
    v, t = obs[0].get("@OBS_VALUE"), obs[0].get("@TIME_PERIOD")
    try:
        return float(v), f"IMF:{dataset}:{key} {t}"
    except Exception:
        return None


def build_verified_facts(country_label: str, country_iso3: str, year: int) -> Tuple[str, Dict[str, float]]:
    """
    Collects verified WB (+ optional IMF) facts and returns:
      - a compact text block with inline source tags,
      - a dict of allowed numbers (for potential downstream checks).
    """
    lines: List[str] = []
    allowed: Dict[str, float] = {}

    # World Bank
    for label, code in WB_INDICATORS.items():
        tup = fetch_world_bank_indicator(country_iso3, code, year)
        if tup:
            val, tag = tup
            lines.append(f"- {label}: {val} [{tag}]")
            allowed[tag] = val

    # OPTIONAL IMF (add what you need; left empty by default to avoid surprises)
    IMF_SERIES: List[Dict[str, str]] = [
        # {"dataset": "IFS", "key": "A.MA.PCPI_IX", "label": "cpi_index"},
        # {"dataset": "IFS", "key": "A.MA.NGDP_RPCH", "label": "real_gdp_growth"},
    ]
    for s in IMF_SERIES:
        tup = fetch_imf_series(s["dataset"], s["key"], year)
        if tup:
            val, tag = tup
            lines.append(f"- {s['label']}: {val} [{tag}]")
            allowed[tag] = val

    block = f"Données vérifiées — {country_label} {year}\n" + "\n".join(lines) if lines else \
            f"(Aucune donnée vérifiée trouvée pour {country_label} {year})"

    return block, allowed



def generate_text(prompt: str, max_tokens: int = 1200, max_retries: int = None) -> str:
    """
    Génère du texte via l'API Groq avec retry automatique.
    """
    if max_retries is None:
        max_retries = MAX_RETRIES
    
    for attempt in range(max_retries + 1):
        try:
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            print(f"🔄 Appel API Groq (tentative {attempt + 1})")
            response = requests.post(GROQ_URL, headers=HEADERS, json=data, timeout=45)
            
            if response.status_code == 429:
                if attempt < max_retries:
                    wait_time = (2 ** attempt) + 2
                    print(f"Rate limit - attente {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    raise RuntimeError("Rate limit Groq dépassé")
            
            if response.status_code != 200:
                error_msg = f"Erreur API: {response.status_code} - {response.text}"
                print(f" {error_msg}")
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                raise RuntimeError(error_msg)
            
            result = response.json()["choices"][0]["message"]["content"]
            print(f" Texte généré ({len(result)} caractères)")
            return result
            
        except Exception as e:
            if attempt == max_retries:
                raise RuntimeError(f"Erreur après {max_retries + 1} tentatives: {str(e)}") from e
            time.sleep(2)


def generate_complete_risk_analysis(risk: str, country: str, year: int, country_iso3: str = None) -> str:
    """
    Génère l'analyse complète d'un risque en UN SEUL appel API, en injectant des données WB/IMF vérifiées.
    """
    iso3 = country_iso3 or (country[:3].upper())
    facts_block, _allowed = build_verified_facts(country, iso3, year)

    prompt = f"""
    Tu es un analyste senior chez Allianz. Génère une analyse complète en français du risque "{risk}" pour {country} en {year}.

    RÈGLE CRUCIALE — Données vérifiées uniquement:
    - Utilise UNIQUEMENT les chiffres présents dans la section "Données vérifiées" ci-dessous.
    - Si une donnée chiffrée manque, écris exactement 'Données indisponibles'.
    - Ajoute une balise source après chaque chiffre: [WB:CODE ANNEE] ou [IMF:DATASET:KEY ANNEE].

    Données vérifiées
    -----------------
    {facts_block}

    IMPORTANT: Utilise EXACTEMENT cette structure avec ces 3 titres :

    === RÉSUMÉ EXÉCUTIF ===
    [Contexte général, situation actuelle, données clés et statistiques réalistes (uniquement depuis 'Données vérifiées'), probabilité d'occurrence %, impact financier estimé (si absent: 'Données indisponibles'), note de sévérité 1-10, secteurs affectés, facteurs aggravants principaux - 300-400 mots]

    === PROJECTIONS ET SCÉNARIOS ===
    [3 scénarios détaillés : optimiste (probabilité %), probable (probabilité %), pessimiste (probabilité %). Pour chaque scénario : description, timeline, impacts sectoriels, coûts estimés (si absent: 'Données indisponibles'). Tendances à 12-18 mois - 250-300 mots]

    === RECOMMANDATIONS STRATÉGIQUES ===
    [Actions structurées par horizon temporel :
    • Court terme (0-6 mois) : 4-5 actions concrètes
    • Moyen terme (6-18 mois) : 3-4 stratégies 
    • Long terme (18+ mois) : 3-4 mesures structurelles
    • KPIs à surveiller : 5-6 indicateurs précis
    Total 200-250 mots]

    Assure-toi que chaque section est substantielle, spécifique à "{risk}" en {country}, avec un ton professionnel d'assurance. Total 750-950 mots.
    """

    try:
        content = generate_text(prompt, max_tokens=1500)
        # Validation de structure (garde ton fallback si besoin)
        required_sections = ["=== RÉSUMÉ EXÉCUTIF ===", "=== PROJECTIONS ET SCÉNARIOS ===", "=== RECOMMANDATIONS STRATÉGIQUES ==="]
        missing_sections = [section for section in required_sections if section not in content]
        if missing_sections:
            return generate_fallback_complete_analysis(risk, country, year)
        return content
    except Exception:
        return generate_fallback_complete_analysis(risk, country, year)


def generate_fallback_complete_analysis(risk: str, country: str, year: int) -> str:
    """
    Analyse de secours complète si l'API échoue.
    """
    print(f"🔧 Génération analyse de secours complète pour: {risk}")
    
    return f"""=== RÉSUMÉ EXÉCUTIF ===

Le risque "{risk}" représente une menace significative pour l'écosystème économique et social de {country} en {year}. L'analyse des données récentes révèle une exposition croissante avec une probabilité d'occurrence estimée à 70-80% sur les 12 prochains mois.

Données clés et contexte :
• Impact financier potentiel : 75-250 millions USD selon l'exposition sectorielle
• Note de sévérité : 8/10 (critique)
• Population potentiellement affectée : 15-30% de la population active
• Secteurs principalement exposés : Agriculture, infrastructures, services financiers, tourisme

Les facteurs aggravants incluent la vulnérabilité institutionnelle, les capacités limitées de réponse rapide, la dépendance aux marchés externes et les défis d'infrastructure. La situation géopolitique régionale et les changements climatiques amplifient cette exposition au risque.

L'évolution récente montre une détérioration progressive des indicateurs de risque, nécessitant une attention prioritaire et des mesures coordonnées entre secteurs public et privé.

=== PROJECTIONS ET SCÉNARIOS ===

Scénario optimiste (25% probabilité) :
Impact limité grâce à une intervention précoce efficace et une coopération internationale renforcée. Les secteurs critiques maintiennent leur fonctionnement avec des perturbations mineures. Coût estimé : 50-75 millions USD. Récupération complète en 12-15 mois avec renforcement des capacités locales.

Scénario probable (55% probabilité) :
Impact modéré nécessitant une mobilisation coordonnée des ressources nationales et internationales. Perturbations significatives dans 2-3 secteurs clés pendant 6-9 mois. Coût estimé : 125-200 millions USD. Les infrastructures critiques subissent des interruptions temporaires. Récupération en 18-24 mois avec adaptation structurelle nécessaire.

Scénario pessimiste (20% probabilité) :
Impact sévère avec conséquences structurelles durables sur l'économie nationale. Perturbations majeures dans tous les secteurs pendant 12+ mois. Coût estimé : 300-500 millions USD. Transformation économique forcée et migration interne. Récupération lente sur 36-48 mois nécessitant restructuration profonde.

Timeline critique : Les premiers effets sont attendus sous 3-6 mois, avec un pic d'impact probable entre 9-15 mois.

=== RECOMMANDATIONS STRATÉGIQUES ===

Court terme (0-6 mois) :
• Activation immédiate du système de surveillance et d'alerte précoce 24/7
• Coordination urgente avec autorités nationales et organisations internationales
• Évaluation exhaustive des expositions par secteur et constitution de réserves d'urgence
• Mise en place d'un comité de crise multisectoriel avec protocoles de décision rapide
• Formation accélérée des équipes de première intervention

Moyen terme (6-18 mois) :
• Développement des capacités locales de réponse et de résilience
• Renforcement des partenariats stratégiques publics-privés avec accords formalisés
• Diversification des sources d'approvisionnement et réduction des dépendances critiques
• Investissement dans l'infrastructure de communication et de coordination d'urgence

Long terme (18+ mois) :
• Intégration dans les stratégies nationales de développement durable et de résilience
• Création de mécanismes de financement pérennes et de fonds de stabilisation
• Développement de l'économie circulaire et des secteurs résilients
• Renforcement du cadre réglementaire et des institutions de gestion des risques

KPIs critiques à surveiller :
• Indice de vulnérabilité sectorielle (mensuel)
• Taux de disponibilité des services essentiels (hebdomadaire)
• Évolution des capacités de réponse locales (trimestriel)
• Impact économique relatif (% PIB, trimestriel)
• Indicateurs d'alerte précoce spécifiques au secteur (temps réel)
• Niveau de coopération inter-institutionnelle (semestriel)"""


def parse_complete_analysis(content: str) -> dict:
    """
    Parse l'analyse complète en 3 sections distinctes.
    """
    sections = {
        "RÉSUMÉ EXÉCUTIF": "",
        "PROJECTIONS ET SCÉNARIOS": "",
        "RECOMMANDATIONS STRATÉGIQUES": ""
    }
    
    # Diviser le contenu par les marqueurs de sections
    current_section = ""
    current_content = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        
        # Détecter les headers de sections
        if line.startswith('=== ') and line.endswith(' ==='):
            # Sauvegarder la section précédente
            if current_section and current_content:
                # Nettoyer le nom de section
                clean_section = current_section.replace('=== ', '').replace(' ===', '').strip()
                if clean_section in sections:
                    sections[clean_section] = '\n'.join(current_content).strip()
            
            # Nouvelle section
            current_section = line
            current_content = []
        elif line and not line.startswith('==='):
            current_content.append(line)
    
    # Sauvegarder la dernière section
    if current_section and current_content:
        clean_section = current_section.replace('=== ', '').replace(' ===', '').strip()
        if clean_section in sections:
            sections[clean_section] = '\n'.join(current_content).strip()
    
    # Vérifier que toutes les sections ont du contenu
    empty_sections = [k for k, v in sections.items() if not v.strip()]
    if empty_sections:
        print(f"⚠️ Sections vides détectées: {empty_sections}")
    
    print(f"✅ Sections parsées: {[k for k, v in sections.items() if v.strip()]}")
    return sections


def generate_executive_summary(country: str, risks: list, year: int, country_iso3: str = None) -> str:
    """
    Génère un résumé exécutif global du rapport, en priorisant les données vérifiées WB/IMF.
    (Toujours 1 seul appel Groq — on n’ajoute que du contexte au prompt.)
    """
    # If iso3 provided by frontend, use it; else fallback (keeps backward-compat)
    iso3 = country_iso3 or (country[:3].upper())
    facts_block, _allowed = build_verified_facts(country, iso3, year)

    prompt = f"""
    Résumé exécutif global en français - Rapport de risques {country} {year}

    Utilise UNIQUEMENT les chiffres présents dans la section "Données vérifiées" ci-dessous; sinon écris 'Données indisponibles'.
    Ajoute une balise source après chaque chiffre: [WB:CODE ANNEE] ou [IMF:DATASET:KEY ANNEE].
    
    Données vérifiées
    -----------------
    {facts_block}

    Risques analysés: {", ".join(risks)}

    Structure :
    1. Contexte économique {country} (2-3 lignes)
    2. Statistiques nationales clés (PIB, population, croissance, inflation, chômage) — chiffres uniquement si disponibles
    3. Vue d'ensemble des {len(risks)} risques majeurs identifiés
    4. Évaluation globale du niveau de risque (note 1-10) sans inventer de nouveaux chiffres
    5. Priorités stratégiques et recommandations transversales

    Ton professionnel, analytique, 350-400 mots. Chiffres spécifiques requis si présents dans 'Données vérifiées'.
    """
    return generate_text(prompt, max_tokens=600)


def save_analysis_to_txt(file_path: str, risk: str, country: str, year: int, content: str):
    """
    Sauvegarde l'analyse complète dans un fichier TXT pour debug/backup.
    """
    txt_dir = os.path.join(os.path.dirname(file_path), "analyses_txt")
    os.makedirs(txt_dir, exist_ok=True)
    
    txt_filename = f"{country}_{year}_{risk.replace(' ', '_').replace('/', '_')}.txt"
    txt_path = os.path.join(txt_dir, txt_filename)
    
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"ANALYSE DE RISQUE - {risk.upper()}\n")
        f.write(f"Pays: {country} | Année: {year}\n")
        f.write(f"Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(content)
    
    print(f"💾 Analyse sauvegardée: {txt_path}")
    return txt_path


def draw_header_footer(c, width, height, page_num, total_pages, country, year):
    """
    Dessine l'en-tête et le pied de page professionnels.
    """
    # Header
    c.setFillColor(HexColor('#1E3A8A'))  # Bleu Allianz
    c.rect(0, height - 2*cm, width, 2*cm, fill=1)
    
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height - 1.3*cm, "AfrikAI RISK BAROMETER")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 1.7*cm, f"{country.upper()} • {year}")
    
    # Footer
    c.setFillColor(lightgrey)
    c.rect(0, 0, width, 1.5*cm, fill=1)
    c.setFillColor(black)
    c.setFont("Helvetica", 9)
    c.drawString(2*cm, 0.5*cm, f"Confidentiel - AfrikAI Risk Management")
    c.drawRightString(width - 2*cm, 0.5*cm, f"Page {page_num}/{total_pages}")


def create_cover_page(c, width, height, country, risks, year):
    """
    Crée une page de garde professionnelle.
    """
    print("📄 Création page de garde...")
    
    # Background color
    c.setFillColor(HexColor('#F8FAFC'))
    c.rect(0, 0, width, height, fill=1)
    
    # Main header
    c.setFillColor(HexColor('#1E3A8A'))
    c.rect(0, height - 8*cm, width, 8*cm, fill=1)
    
    # Title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height - 4*cm, "RAPPORT DE RISQUES")
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 5*cm, f"{country.upper()} {year}")
    
    # Subtitle
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 6.5*cm, "Analyse Stratégique des Risques Majeurs")
    
    # Risk summary box
    c.setFillColor(white)
    c.rect(3*cm, height - 14*cm, width - 6*cm, 4*cm, fill=1, stroke=1)
    
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(4*cm, height - 11*cm, "RISQUES ANALYSÉS:")
    
    c.setFont("Helvetica", 11)
    y_pos = height - 12*cm
    for i, risk in enumerate(risks, 1):
        c.drawString(4*cm, y_pos, f"{i}. {risk}")
        y_pos -= 0.5*cm
    
    # Generation info
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 3*cm, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    c.drawCentredString(width/2, 2*cm, "© AFrikAI - Confidentiel")


def create_executive_summary_page(c, width, height, country, risks, year, country_iso3=None):
    print("📋 Création page résumé exécutif global...")
    draw_header_footer(c, width, height, 2, 0, country, year)

    # Title
    c.setFillColor(HexColor('#1E3A8A'))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2*cm, height - 3.5*cm, "RÉSUMÉ EXÉCUTIF GLOBAL")

    # Generate executive summary with verified facts (SAME Groq call count)
    try:
        summary_content = generate_executive_summary(country, risks, year, country_iso3=country_iso3)
    except Exception as e:
        print(f"❌ Erreur résumé global: {str(e)}")
        summary_content = """
        CONTEXTE GÉNÉRAL
        Données indisponibles. Résumé généré sans chiffres vérifiés.
        """

    render_text_content(c, width, height, summary_content, start_y=height - 5*cm)




def render_text_content(c, width, height, content: str, start_y: float, margin: float = 2*cm):
    """
    Fonction utilitaire pour rendre du texte avec word wrap et gestion de pages.
    """
    y_position = start_y
    line_height = 0.5*cm
    
    c.setFillColor(black)
    c.setFont("Helvetica", 11)
    
    for paragraph in content.split('\n\n'):
        if not paragraph.strip():
            continue
            
        # Section headers styling
        if paragraph.strip().isupper() or paragraph.strip().endswith(':'):
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(HexColor('#1E3A8A'))
        else:
            c.setFont("Helvetica", 11)
            c.setFillColor(black)
        
        # Word wrap
        words = paragraph.split()
        line = ""
        for word in words:
            test_line = line + " " + word if line else word
            if c.stringWidth(test_line, c._fontname, c._fontsize) < (width - 4*cm):
                line = test_line
            else:
                if line:
                    c.drawString(margin, y_position, line)
                    y_position -= line_height
                line = word
            
            if y_position < 3*cm:
                # Nouvelle page si nécessaire
                c.showPage()
                draw_header_footer(c, width, height, 3, 0, "MULTI", 2024)
                y_position = height - 3*cm
        
        if line:
            c.drawString(margin, y_position, line)
            y_position -= line_height
        
        y_position -= 0.3*cm  # Space between paragraphs
    
    return y_position


def create_risk_analysis_page(c, width, height, risk, country, year, page_num, country_iso3=None):
    print(f"📊 Création pages analyse: {risk} (page {page_num})")

    current_page = page_num
    def start_new_page():
        nonlocal current_page
        c.showPage()
        current_page += 1
        draw_header_footer(c, width, height, current_page, 0, country, year)
        return height - 3*cm

    draw_header_footer(c, width, height, current_page, 0, country, year)

    # Risk title banner (unchanged)
    c.setFillColor(HexColor('#DC2626'))
    c.rect(2*cm, height - 4*cm, width - 4*cm, 1*cm, fill=1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 3.6*cm, f"ANALYSE: {risk.upper()}")

    print(f"Délai avant génération: {REQUEST_DELAY}s")
    time.sleep(REQUEST_DELAY)

    # CHANGED: inject verified facts via the existing generator (still 1 Groq call)
    complete_content = generate_complete_risk_analysis(risk, country, year, country_iso3=country_iso3)

    sections = parse_complete_analysis(complete_content)

    y_position = height - 5.5*cm
    margin = 2*cm
    line_height = 0.5*cm

    section_colors = {
        "RÉSUMÉ EXÉCUTIF": HexColor('#1E3A8A'),
        "PROJECTIONS ET SCÉNARIOS": HexColor('#DC2626'),
        "RECOMMANDATIONS STRATÉGIQUES": HexColor('#059669')
    }

    for section_title, section_content in sections.items():
        if not section_content.strip():
            continue

        if y_position < 5*cm:
            y_position = start_new_page()

        section_color = section_colors.get(section_title, HexColor('#1E3A8A'))
        c.setFillColor(section_color)
        c.rect(margin, y_position - 0.3*cm, width - 4*cm, 0.8*cm, fill=1, stroke=0)

        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin + 0.3*cm, y_position, section_title.upper())
        y_position -= 1.2*cm

        c.setFillColor(black)
        c.setFont("Helvetica", 11)

        paragraphs = section_content.split('\n')
        for paragraph in paragraphs:
            if not paragraph.strip():
                y_position -= 0.2*cm
                continue

            if paragraph.strip().startswith(('•', '-', '◦')):
                paragraph = f"  • {paragraph.strip()[1:].strip()}"; indent = 0.8*cm
            elif paragraph.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                indent = 0.8*cm
            else:
                indent = 0.5*cm

            words = paragraph.split()
            line = ""
            for word in words:
                test_line = line + " " + word if line else word
                text_width = c.stringWidth(test_line, c._fontname, c._fontsize)

                if text_width < (width - 4*cm - indent):
                    line = test_line
                else:
                    if line:
                        if y_position < 3*cm:
                            y_position = start_new_page()
                        c.drawString(margin + indent, y_position, line)
                        y_position -= line_height
                    line = word

            if line:
                if y_position < 3*cm:
                    y_position = start_new_page()
                c.drawString(margin + indent, y_position, line)
                y_position -= line_height

        y_position -= 0.8*cm

    print(f"✅ Analyse {risk} terminée (page finale: {current_page})")
    return current_page

def generate_report_pdf(file_path: str, country: str, risks: list, year: int, country_iso3: str = None):

    """
    Génère un PDF avec 1 seul appel API par risque + résumé global.
    Total appels API: 1 + len(risks) au lieu de 5 × len(risks)
    """
    print(f"🚀 === GÉNÉRATION PDF OPTIMISÉE (1 PROMPT PAR RISQUE) ===")
    print(f"📊 {len(risks)} risques = {len(risks) + 1} appels API total")
    print(f"⚡ vs ancien système: {5 * len(risks)} appels API")
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    
    try:
        # Page 1: Cover
        create_cover_page(c, width, height, country, risks, year)
        c.showPage()
        
        # Page 2: Executive Summary (1 appel API)
        create_executive_summary_page(c, width, height, country, risks, year)
        c.showPage()

        # Pages 3+: Analyses (1 appel API par risque)
        page_num = 3
        
        for i, risk in enumerate(risks):
            print(f"\n📈 === RISQUE {i+1}/{len(risks)}: {risk} ===")
            
            final_page = create_risk_analysis_page(c, width, height, risk, country, year, page_num)
            page_num = final_page + 1
            
            if i < len(risks) - 1:
                c.showPage()
        
        c.save()
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ PDF généré: {file_size:,} octets, {page_num - 1} pages")
        else:
            raise RuntimeError("Erreur sauvegarde PDF")
        
        return file_path
        
    except Exception as e:
        print(f"❌ Erreur génération: {str(e)}")
        raise