import spacy
import re
from typing import Optional

# ✅ Load lightweight English NER model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("⚠️ spaCy model not found — run: python -m spacy download en_core_web_sm")
    nlp = None

# 🌍 Canonical country names
COUNTRIES = [
    "morocco", "tunisia", "algeria", "egypt", "south africa", "kenya", "nigeria",
    "ghana", "ethiopia", "senegal", "rwanda", "tanzania", "uganda", "cameroon",
    "zambia", "ivory coast", "namibia", "botswana", "madagascar", "libya",
    "sudan", "congo", "somalia", "mali", "niger", "chad", "angola",
    "united states", "united kingdom", "france", "germany", "spain", "italy",
    "canada", "japan", "china", "india", "brazil"
]
COUNTRY_MAP = {c.lower(): c.title() for c in COUNTRIES}

# 🌐 Synonyms / aliases / translations
COUNTRY_SYNONYMS = {
    # North Africa
    "maroc": "morocco",
    "tunis": "tunisia",
    "algérie": "algeria",
    "egypte": "egypt",
    "royaume du maroc": "morocco",
    "côte d’ivoire": "ivory coast",
    "côte d'ivoire": "ivory coast",

    # Common abbreviations
    "usa": "united states",
    "u.s.": "united states",
    "u.s.a.": "united states",
    "america": "united states",
    "uk": "united kingdom",
    "england": "united kingdom",
    "britain": "united kingdom",
    "ivorycoast": "ivory coast",
    "southafrica": "south africa",

    # Languages / demonyms
    "french": "france",
    "german": "germany",
    "italian": "italy",
    "spanish": "spain",
    "canadian": "canada",
    "chinese": "china",
    "indian": "india",
    "brazilian": "brazil",
}

# 🧠 Risk types (can be extended)
RISK_TYPES = [
    "economic", "political", "climate", "sanitary",
    "geopolitical", "social", "military", "environmental"
]

DEFAULT_YEAR = 2025


# ────────────────────────────────
# 🔍 DETECTION HELPERS
# ────────────────────────────────

def normalize_text(text: str) -> str:
    """Normalize accents, punctuation, and lowercase the text."""
    text = text.lower()
    text = text.replace("’", "'")
    text = re.sub(r"[^a-z0-9\s\-'éèàù]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_country_keyword(text: str) -> Optional[str]:
    """Fast keyword or synonym-based detection."""
    text = normalize_text(text)

    # Check synonyms first
    for alias, canonical in COUNTRY_SYNONYMS.items():
        if alias in text:
            return COUNTRY_MAP.get(canonical, canonical.title())

    # Then check canonical names
    for name in COUNTRIES:
        if name in text:
            return COUNTRY_MAP[name]

    return None


def detect_country_ner(text: str) -> Optional[str]:
    """spaCy-based Named Entity Recognition fallback."""
    if not nlp:
        return None

    doc = nlp(text)
    detected = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]
    if detected:
        normalized = normalize_text(detected[0])
        return COUNTRY_MAP.get(normalized, detected[0].title())
    return None


def detect_risk(text: str) -> Optional[str]:
    """Extracts the risk category from text."""
    lower = text.lower()
    for r in RISK_TYPES:
        if r in lower:
            return r
    return None


def detect_year(text: str) -> Optional[int]:
    """Extracts the mentioned year (e.g., 2030)."""
    match = re.search(r"\b(19|20)\d{2}\b", text)
    return int(match.group()) if match else DEFAULT_YEAR


# ────────────────────────────────
# 🧠 MAIN PIPELINE
# ────────────────────────────────

def extract_country_risk_year(text: str):
    """
    Combines keyword + synonym + NER + fallback.
    Returns structured (country, risk, year) info from transcription.
    """
    text = text.strip()
    country = detect_country_keyword(text)

    if not country:
        country = detect_country_ner(text)

    risk = detect_risk(text)
    year = detect_year(text)

    return country, risk, year
