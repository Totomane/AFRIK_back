import spacy
import re
import logging
from typing import Optional, Dict, List, Tuple, Union, Any
from dataclasses import dataclass, asdict
from functools import lru_cache
import json
from datetime import datetime
import unicodedata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CountryDetectionResult:
    """Professional result container for country detection"""
    country: Optional[str] = None
    risk_type: Optional[str] = None
    year: Optional[int] = None
    confidence_score: float = 0.0
    detection_method: Optional[str] = None
    alternative_matches: List[str] = None
    processing_time_ms: float = 0.0
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.alternative_matches is None:
            self.alternative_matches = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return asdict(self)

# ✅ Load lightweight English NER model with professional error handling
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("✅ spaCy model 'en_core_web_sm' loaded successfully")
except OSError as e:
    logger.error("❌ spaCy model not found. Install with: python -m spacy download en_core_web_sm")
    logger.error(f"Error details: {e}")
    nlp = None
except Exception as e:
    logger.error(f"❌ Unexpected error loading spaCy model: {e}")
    nlp = None

# 🌍 Comprehensive country database with ISO codes and regions
COUNTRY_DATABASE = {
    # African Countries (Primary Focus)
    "morocco": {"official": "Morocco", "iso": "MA", "region": "North Africa", "priority": 1},
    "tunisia": {"official": "Tunisia", "iso": "TN", "region": "North Africa", "priority": 1},
    "algeria": {"official": "Algeria", "iso": "DZ", "region": "North Africa", "priority": 1},
    "egypt": {"official": "Egypt", "iso": "EG", "region": "North Africa", "priority": 1},
    "south africa": {"official": "South Africa", "iso": "ZA", "region": "Southern Africa", "priority": 1},
    "kenya": {"official": "Kenya", "iso": "KE", "region": "East Africa", "priority": 1},
    "nigeria": {"official": "Nigeria", "iso": "NG", "region": "West Africa", "priority": 1},
    "ghana": {"official": "Ghana", "iso": "GH", "region": "West Africa", "priority": 1},
    "ethiopia": {"official": "Ethiopia", "iso": "ET", "region": "East Africa", "priority": 1},
    "senegal": {"official": "Senegal", "iso": "SN", "region": "West Africa", "priority": 1},
    "rwanda": {"official": "Rwanda", "iso": "RW", "region": "East Africa", "priority": 1},
    "tanzania": {"official": "Tanzania", "iso": "TZ", "region": "East Africa", "priority": 1},
    "uganda": {"official": "Uganda", "iso": "UG", "region": "East Africa", "priority": 1},
    "cameroon": {"official": "Cameroon", "iso": "CM", "region": "Central Africa", "priority": 1},
    "zambia": {"official": "Zambia", "iso": "ZM", "region": "Southern Africa", "priority": 1},
    "ivory coast": {"official": "Côte d'Ivoire", "iso": "CI", "region": "West Africa", "priority": 1},
    "namibia": {"official": "Namibia", "iso": "NA", "region": "Southern Africa", "priority": 1},
    "botswana": {"official": "Botswana", "iso": "BW", "region": "Southern Africa", "priority": 1},
    "madagascar": {"official": "Madagascar", "iso": "MG", "region": "East Africa", "priority": 1},
    "libya": {"official": "Libya", "iso": "LY", "region": "North Africa", "priority": 1},
    "sudan": {"official": "Sudan", "iso": "SD", "region": "Northeast Africa", "priority": 1},
    "congo": {"official": "Democratic Republic of the Congo", "iso": "CD", "region": "Central Africa", "priority": 1},
    "somalia": {"official": "Somalia", "iso": "SO", "region": "East Africa", "priority": 1},
    "mali": {"official": "Mali", "iso": "ML", "region": "West Africa", "priority": 1},
    "niger": {"official": "Niger", "iso": "NE", "region": "West Africa", "priority": 1},
    "chad": {"official": "Chad", "iso": "TD", "region": "Central Africa", "priority": 1},
    "angola": {"official": "Angola", "iso": "AO", "region": "Southern Africa", "priority": 1},
    
    # Major International Countries
    "united states": {"official": "United States", "iso": "US", "region": "North America", "priority": 2},
    "united kingdom": {"official": "United Kingdom", "iso": "GB", "region": "Europe", "priority": 2},
    "france": {"official": "France", "iso": "FR", "region": "Europe", "priority": 2},
    "germany": {"official": "Germany", "iso": "DE", "region": "Europe", "priority": 2},
    "spain": {"official": "Spain", "iso": "ES", "region": "Europe", "priority": 2},
    "italy": {"official": "Italy", "iso": "IT", "region": "Europe", "priority": 2},
    "canada": {"official": "Canada", "iso": "CA", "region": "North America", "priority": 2},
    "japan": {"official": "Japan", "iso": "JP", "region": "Asia", "priority": 2},
    "china": {"official": "China", "iso": "CN", "region": "Asia", "priority": 2},
    "india": {"official": "India", "iso": "IN", "region": "Asia", "priority": 2},
    "brazil": {"official": "Brazil", "iso": "BR", "region": "South America", "priority": 2},
}

# Generate lookup maps
COUNTRIES = list(COUNTRY_DATABASE.keys())
COUNTRY_MAP = {name: data["official"] for name, data in COUNTRY_DATABASE.items()}

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

# 🧠 Comprehensive risk taxonomy with confidence weights
RISK_TAXONOMY = {
    # Economic risks
    "economic": {"weight": 1.0, "aliases": ["économique", "financier", "financial", "monetary", "fiscal"]},
    "inflation": {"weight": 0.9, "aliases": ["price increase", "cost of living", "monetary devaluation"]},
    "recession": {"weight": 0.9, "aliases": ["economic downturn", "crisis", "depression"]},
    
    # Political risks
    "political": {"weight": 1.0, "aliases": ["politique", "governmental", "governance", "institutional"]},
    "instability": {"weight": 0.9, "aliases": ["unrest", "turmoil", "upheaval", "disorder"]},
    "corruption": {"weight": 0.8, "aliases": ["graft", "bribery", "fraud", "embezzlement"]},
    
    # Environmental risks
    "climate": {"weight": 1.0, "aliases": ["climatique", "weather", "environmental", "ecological"]},
    "environmental": {"weight": 1.0, "aliases": ["écologique", "pollution", "ecosystem", "biodiversity"]},
    "drought": {"weight": 0.9, "aliases": ["water scarcity", "arid", "dry season"]},
    "flooding": {"weight": 0.9, "aliases": ["flood", "inondation", "deluge", "overflow"]},
    
    # Health risks
    "sanitary": {"weight": 1.0, "aliases": ["sanitaire", "health", "medical", "healthcare"]},
    "pandemic": {"weight": 0.9, "aliases": ["epidemic", "outbreak", "contagion", "disease spread"]},
    "malnutrition": {"weight": 0.8, "aliases": ["hunger", "food insecurity", "undernutrition"]},
    
    # Security risks
    "geopolitical": {"weight": 1.0, "aliases": ["géopolitique", "international", "regional", "strategic"]},
    "military": {"weight": 0.9, "aliases": ["militaire", "warfare", "conflict", "defense", "security"]},
    "terrorism": {"weight": 0.9, "aliases": ["terrorist", "extremism", "violence", "attacks"]},
    
    # Social risks
    "social": {"weight": 1.0, "aliases": ["societal", "community", "demographic", "cultural"]},
    "migration": {"weight": 0.8, "aliases": ["displacement", "refugee", "emigration", "exodus"]},
    "inequality": {"weight": 0.8, "aliases": ["disparity", "gap", "injustice", "discrimination"]},
}

# Extract flat lists for backward compatibility
RISK_TYPES = list(RISK_TAXONOMY.keys())
ALL_RISK_ALIASES = {}
for risk, data in RISK_TAXONOMY.items():
    ALL_RISK_ALIASES[risk] = risk
    for alias in data["aliases"]:
        ALL_RISK_ALIASES[alias.lower()] = risk

DEFAULT_YEAR = 2025
CURRENT_YEAR = datetime.now().year
VALID_YEAR_RANGE = (1990, 2050)


# ────────────────────────────────
# 🔍 DETECTION HELPERS
# ────────────────────────────────

@lru_cache(maxsize=1000)
def normalize_text(text: str) -> str:
    """Advanced text normalization with Unicode handling and caching."""
    if not text or not isinstance(text, str):
        return ""
    
    try:
        # Unicode normalization (NFD = decomposed form)
        text = unicodedata.normalize('NFD', text)
        
        # Remove diacritics while preserving base characters
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Lowercase conversion
        text = text.lower()
        
        # Standardize apostrophes and quotes
        text = text.replace("'", "'").replace("'", "'").replace('"', '"').replace('"', '"')
        
        # Handle common abbreviations and punctuation
        text = text.replace("u.s.a.", "usa").replace("u.s.", "us").replace("u.k.", "uk")
        
        # Remove extra punctuation but keep hyphens and apostrophes in names
        text = re.sub(r"[^a-z0-9\s\-']", " ", text)
        
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        
        logger.debug(f"Normalized text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        return text
        
    except Exception as e:
        logger.warning(f"Text normalization failed for '{text[:50]}': {e}")
        return text.lower().strip()


def detect_country_keyword(text: str) -> Tuple[Optional[str], float, List[str]]:
    """Enhanced keyword detection with confidence scoring and multiple matches."""
    text = normalize_text(text)
    matches = []
    
    if not text:
        return None, 0.0, []
    
    try:
        # Check synonyms first (higher confidence for exact matches)
        for alias, canonical in COUNTRY_SYNONYMS.items():
            if alias in text:
                # Calculate confidence based on match quality
                if f" {alias} " in f" {text} ":  # Word boundary match
                    confidence = 0.9
                elif text.startswith(alias) or text.endswith(alias):
                    confidence = 0.8
                else:
                    confidence = 0.6
                
                country_name = COUNTRY_MAP.get(canonical, canonical.title())
                matches.append((country_name, confidence, f"synonym:{alias}"))
        
        # Check canonical names with word boundary detection
        for name in COUNTRIES:
            if name in text:
                # Prefer word boundaries for higher confidence
                if f" {name} " in f" {text} ":
                    confidence = 0.95
                elif text.startswith(name) or text.endswith(name):
                    confidence = 0.85
                else:
                    confidence = 0.7
                
                # Boost confidence for African countries (primary focus)
                country_info = COUNTRY_DATABASE.get(name, {})
                if country_info.get("priority") == 1:
                    confidence += 0.05
                
                matches.append((COUNTRY_MAP[name], confidence, f"canonical:{name}"))
        
        if matches:
            # Sort by confidence and return best match
            matches.sort(key=lambda x: x[1], reverse=True)
            best_match = matches[0]
            
            # Collect alternative matches for context
            alternatives = [match[0] for match in matches[1:4]]  # Top 3 alternatives
            
            logger.debug(f"Country keyword detection: {best_match[0]} (confidence: {best_match[1]:.2f})")
            return best_match[0], best_match[1], alternatives
        
        return None, 0.0, []
        
    except Exception as e:
        logger.error(f"Error in keyword detection: {e}")
        return None, 0.0, []


def detect_country_ner(text: str) -> Tuple[Optional[str], float, List[str]]:
    """Enhanced spaCy-based Named Entity Recognition with confidence scoring."""
    if not nlp:
        logger.warning("spaCy model not available for NER detection")
        return None, 0.0, []
    
    try:
        # Process text with spaCy
        doc = nlp(text[:1000])  # Limit text length for performance
        
        ner_matches = []
        for ent in doc.ents:
            if ent.label_ in ("GPE", "LOC", "NORP"):  # Geopolitical, Location, Nationality
                normalized = normalize_text(ent.text)
                
                # Check if detected entity matches our country database
                country_match = None
                confidence = 0.0
                
                # Direct match
                if normalized in COUNTRY_MAP:
                    country_match = COUNTRY_MAP[normalized]
                    confidence = 0.8
                
                # Synonym match
                elif normalized in COUNTRY_SYNONYMS:
                    canonical = COUNTRY_SYNONYMS[normalized]
                    country_match = COUNTRY_MAP.get(canonical, canonical.title())
                    confidence = 0.75
                
                # Partial match (fuzzy)
                else:
                    for country in COUNTRIES:
                        if country in normalized or normalized in country:
                            country_match = COUNTRY_MAP[country]
                            confidence = 0.6
                            break
                
                if country_match:
                    # Adjust confidence based on spaCy's confidence and entity type
                    if ent.label_ == "GPE":
                        confidence += 0.1  # Geopolitical entities are more reliable
                    
                    ner_matches.append((country_match, confidence, f"ner:{ent.label_}:{ent.text}"))
        
        if ner_matches:
            # Sort by confidence
            ner_matches.sort(key=lambda x: x[1], reverse=True)
            best_match = ner_matches[0]
            alternatives = [match[0] for match in ner_matches[1:3]]
            
            logger.debug(f"NER detection: {best_match[0]} (confidence: {best_match[1]:.2f})")
            return best_match[0], best_match[1], alternatives
        
        return None, 0.0, []
        
    except Exception as e:
        logger.error(f"Error in NER detection: {e}")
        return None, 0.0, []


def detect_risk(text: str) -> Tuple[Optional[str], float, List[str]]:
    """Enhanced risk detection with confidence scoring and multiple matches."""
    if not text:
        return None, 0.0, []
    
    text_lower = normalize_text(text)
    risk_matches = []
    
    try:
        # Check all risk types and aliases
        for term, canonical_risk in ALL_RISK_ALIASES.items():
            if term in text_lower:
                # Calculate confidence based on match quality
                risk_info = RISK_TAXONOMY.get(canonical_risk, {"weight": 0.5})
                base_confidence = risk_info["weight"]
                
                # Word boundary detection for better confidence
                if f" {term} " in f" {text_lower} ":
                    confidence = base_confidence * 0.95
                elif text_lower.startswith(term) or text_lower.endswith(term):
                    confidence = base_confidence * 0.85
                else:
                    confidence = base_confidence * 0.7
                
                risk_matches.append((canonical_risk, confidence, f"term:{term}"))
        
        if risk_matches:
            # Remove duplicates and sort by confidence
            unique_matches = {}
            for risk, conf, method in risk_matches:
                if risk not in unique_matches or conf > unique_matches[risk][1]:
                    unique_matches[risk] = (risk, conf, method)
            
            sorted_matches = sorted(unique_matches.values(), key=lambda x: x[1], reverse=True)
            best_match = sorted_matches[0]
            alternatives = [match[0] for match in sorted_matches[1:3]]
            
            logger.debug(f"Risk detection: {best_match[0]} (confidence: {best_match[1]:.2f})")
            return best_match[0], best_match[1], alternatives
        
        return None, 0.0, []
        
    except Exception as e:
        logger.error(f"Error in risk detection: {e}")
        return None, 0.0, []


def detect_year(text: str) -> Tuple[Optional[int], float]:
    """Enhanced year detection with validation and confidence scoring."""
    if not text:
        return None, 0.0
    
    try:
        # Find all potential years
        year_patterns = [
            r"\b(19|20)\d{2}\b",  # Standard 4-digit years
            r"\b'(\d{2})\b",      # Abbreviated years like '25, '30
            r"\ben\s*(\d{4})\b",  # "en 2025" pattern
            r"\ban\s*(\d{4})\b",  # "an 2025" pattern (French)
        ]
        
        years_found = []
        
        for pattern in year_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if "'" in pattern:  # Handle abbreviated years
                    year_str = match.group(1)
                    year = int(f"20{year_str}") if int(year_str) < 50 else int(f"19{year_str}")
                else:
                    year = int(match.group(1) if pattern.count('(') > 1 else match.group(0).strip())
                
                # Validate year is in reasonable range
                if VALID_YEAR_RANGE[0] <= year <= VALID_YEAR_RANGE[1]:
                    # Calculate confidence based on context and recency
                    confidence = 0.9
                    
                    # Boost confidence for future years (more relevant for risk assessment)
                    if year > CURRENT_YEAR:
                        confidence += 0.05
                    
                    # Reduce confidence for very old or far future years
                    year_distance = abs(year - CURRENT_YEAR)
                    if year_distance > 20:
                        confidence -= 0.2
                    elif year_distance > 10:
                        confidence -= 0.1
                    
                    years_found.append((year, confidence, match.group(0)))
        
        if years_found:
            # Sort by confidence and return best match
            years_found.sort(key=lambda x: x[1], reverse=True)
            best_year = years_found[0]
            
            logger.debug(f"Year detection: {best_year[0]} (confidence: {best_year[1]:.2f})")
            return best_year[0], best_year[1]
        
        # Return current year + 1 as default with low confidence
        return CURRENT_YEAR + 1, 0.3
        
    except Exception as e:
        logger.error(f"Error in year detection: {e}")
        return DEFAULT_YEAR, 0.2


# ────────────────────────────────
# 🧠 MAIN PIPELINE
# ────────────────────────────────

class ProfessionalCountryDetectionService:
    """Professional country detection service with comprehensive analysis capabilities."""
    
    def __init__(self):
        self.logger = logger
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize service components and validate dependencies."""
        try:
            # Validate spaCy model
            if nlp:
                self.logger.info("✅ Country detection service initialized with NLP support")
            else:
                self.logger.warning("⚠️ NLP model unavailable - using keyword-only detection")
            
            # Validate databases
            self.logger.info(f"📊 Loaded {len(COUNTRY_DATABASE)} countries")
            self.logger.info(f"📊 Loaded {len(COUNTRY_SYNONYMS)} country synonyms")
            self.logger.info(f"📊 Loaded {len(RISK_TAXONOMY)} risk categories")
            
        except Exception as e:
            self.logger.error(f"❌ Service initialization error: {e}")
    
    def extract_country_risk_year(self, text: str, include_metadata: bool = False) -> Union[Tuple, CountryDetectionResult]:
        """
        Professional extraction with comprehensive analysis and confidence scoring.
        
        Args:
            text: Input text to analyze
            include_metadata: If True, returns CountryDetectionResult with full metadata
        
        Returns:
            Tuple[country, risk, year] or CountryDetectionResult object
        """
        start_time = datetime.now()
        
        try:
            if not text or not isinstance(text, str):
                result = CountryDetectionResult(error="Invalid input text")
                return result if include_metadata else (None, None, None)
            
            text = text.strip()
            self.logger.debug(f"🔍 Analyzing text: '{text[:100]}{'...' if len(text) > 100 else ''}'")
            
            # Country detection with multiple methods
            country, country_confidence, country_alternatives = self._detect_country_comprehensive(text)
            
            # Risk detection
            risk, risk_confidence, risk_alternatives = detect_risk(text)
            
            # Year detection
            year, year_confidence = detect_year(text)
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                country_confidence, risk_confidence, year_confidence
            )
            
            # Processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Determine detection method
            detection_method = self._get_detection_method_summary(
                country_confidence, risk_confidence, year_confidence
            )
            
            # Create result object
            result = CountryDetectionResult(
                country=country,
                risk_type=risk,
                year=year,
                confidence_score=overall_confidence,
                detection_method=detection_method,
                alternative_matches=country_alternatives + risk_alternatives,
                processing_time_ms=processing_time
            )
            
            self.logger.debug(f"✅ Detection completed: Country={country}, Risk={risk}, Year={year}, Confidence={overall_confidence:.2f}")
            
            return result if include_metadata else (country, risk, year)
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self.logger.error(f"❌ Extraction failed: {e}")
            
            result = CountryDetectionResult(
                error=str(e),
                processing_time_ms=processing_time
            )
            
            return result if include_metadata else (None, None, None)
    
    def _detect_country_comprehensive(self, text: str) -> Tuple[Optional[str], float, List[str]]:
        """Comprehensive country detection using multiple methods."""
        # Method 1: Keyword detection
        keyword_country, keyword_conf, keyword_alts = detect_country_keyword(text)
        
        # Method 2: NER detection
        ner_country, ner_conf, ner_alts = detect_country_ner(text)
        
        # Combine results and choose best
        candidates = []
        
        if keyword_country:
            candidates.append((keyword_country, keyword_conf, "keyword", keyword_alts))
        
        if ner_country and ner_country != keyword_country:
            candidates.append((ner_country, ner_conf, "ner", ner_alts))
        
        if candidates:
            # Sort by confidence
            candidates.sort(key=lambda x: x[1], reverse=True)
            best = candidates[0]
            
            # Combine alternatives from all methods
            all_alternatives = []
            for candidate in candidates:
                all_alternatives.extend(candidate[3])
            
            # Remove duplicates while preserving order
            unique_alternatives = []
            for alt in all_alternatives:
                if alt not in unique_alternatives and alt != best[0]:
                    unique_alternatives.append(alt)
            
            return best[0], best[1], unique_alternatives[:5]  # Limit to top 5
        
        return None, 0.0, []
    
    def _calculate_overall_confidence(self, country_conf: float, risk_conf: float, year_conf: float) -> float:
        """Calculate weighted overall confidence score."""
        # Weights for different components
        weights = {
            'country': 0.5,  # Country is most important
            'risk': 0.3,     # Risk is secondary
            'year': 0.2      # Year is least critical
        }
        
        # Only include components that were detected
        total_weight = 0
        weighted_sum = 0
        
        if country_conf > 0:
            weighted_sum += country_conf * weights['country']
            total_weight += weights['country']
        
        if risk_conf > 0:
            weighted_sum += risk_conf * weights['risk']
            total_weight += weights['risk']
        
        if year_conf > 0:
            weighted_sum += year_conf * weights['year']
            total_weight += weights['year']
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _get_detection_method_summary(self, country_conf: float, risk_conf: float, year_conf: float) -> str:
        """Generate human-readable detection method summary."""
        methods = []
        
        if country_conf > 0.8:
            methods.append("high-confidence country detection")
        elif country_conf > 0.5:
            methods.append("moderate-confidence country detection")
        elif country_conf > 0:
            methods.append("low-confidence country detection")
        
        if risk_conf > 0.8:
            methods.append("precise risk identification")
        elif risk_conf > 0:
            methods.append("risk pattern matching")
        
        if year_conf > 0.8:
            methods.append("explicit year reference")
        elif year_conf > 0:
            methods.append("year inference")
        
        return "; ".join(methods) if methods else "basic text analysis"
    
    def get_supported_countries(self) -> Dict[str, Dict]:
        """Return comprehensive list of supported countries with metadata."""
        return COUNTRY_DATABASE.copy()
    
    def get_supported_risks(self) -> Dict[str, Dict]:
        """Return comprehensive list of supported risk types with metadata."""
        return RISK_TAXONOMY.copy()
    
    def validate_input(self, text: str) -> Dict[str, Union[bool, str]]:
        """Validate input text and provide recommendations."""
        validation = {
            "is_valid": True,
            "length_ok": len(text) > 10,
            "has_geographic_terms": any(country in text.lower() for country in COUNTRIES[:10]),
            "has_risk_terms": any(risk in text.lower() for risk in RISK_TYPES[:5]),
            "recommendations": []
        }
        
        if len(text) < 10:
            validation["recommendations"].append("Text is very short - consider providing more context")
        
        if not validation["has_geographic_terms"]:
            validation["recommendations"].append("No obvious geographic references found - specify country/region")
        
        if not validation["has_risk_terms"]:
            validation["recommendations"].append("No risk-related terms detected - consider adding risk context")
        
        validation["is_valid"] = len(validation["recommendations"]) == 0
        
        return validation

    def validate_detection(self, text: str, expected_country: str = None, 
                          expected_risk: str = None, expected_year: int = None) -> Dict[str, bool]:
        """
        Validate detection results against expected values.
        
        Args:
            text: Input text
            expected_country: Expected country result
            expected_risk: Expected risk result 
            expected_year: Expected year result
            
        Returns:
            Dictionary with validation results
        """
        result = self.extract_country_risk_year(text, include_metadata=True)
        
        validation = {
            "country_match": False,
            "risk_match": False,
            "year_match": False,
            "overall_confidence": result.confidence_score
        }
        
        if expected_country:
            validation["country_match"] = (
                result.country and result.country.lower() == expected_country.lower() or
                (result.alternative_matches and expected_country.lower() in [alt.lower() for alt in result.alternative_matches])
            )
        
        if expected_risk:
            validation["risk_match"] = (
                result.risk_type and result.risk_type.lower() == expected_risk.lower() or
                (result.alternative_matches and expected_risk.lower() in [alt.lower() for alt in result.alternative_matches])
            )
        
        if expected_year:
            validation["year_match"] = result.year == expected_year
        
        return validation


# Enhanced service instance with additional features
country_detection_service = ProfessionalCountryDetectionService()

# Alternative service for specialized use cases
class CountryDetectionService(ProfessionalCountryDetectionService):
    """Legacy wrapper maintaining backward compatibility while adding modern features."""
    
    def __init__(self):
        super().__init__()
        logger.warning("Using legacy CountryDetectionService wrapper. Consider upgrading to ProfessionalCountryDetectionService directly.")

    def analyze_text(self, text: str, enable_cache: bool = True) -> CountryDetectionResult:
        """Legacy analyze_text method with updated signature."""
        return self.extract_country_risk_year(text, include_metadata=True)

# Backward compatibility functions
def extract_country_risk_year(text: str):
    """
    Backward compatible function that maintains original API.
    For new code, use country_detection_service.extract_country_risk_year() directly.
    """
    return country_detection_service.extract_country_risk_year(text, include_metadata=False)

def analyze_text_advanced(text: str, detailed: bool = False) -> CountryDetectionResult:
    """
    Advanced analysis function with comprehensive results.
    
    Args:
        text: Input text to analyze
        detailed: Include detailed confidence breakdown and alternatives
        
    Returns:
        CountryDetectionResult with comprehensive analysis
    """
    return country_detection_service.extract_country_risk_year(text, include_metadata=True)

def batch_analyze_texts(texts: List[str]) -> List[CountryDetectionResult]:
    """
    Batch analysis function for processing multiple texts efficiently.
    
    Args:
        texts: List of texts to analyze
        
    Returns:
        List of CountryDetectionResult objects
    """
    results = []
    for text in texts:
        result = country_detection_service.extract_country_risk_year(text, include_metadata=True)
        results.append(result)
    return results

def get_service_statistics() -> Dict[str, Any]:
    """Get comprehensive service performance statistics."""
    return {
        "supported_countries": len(COUNTRY_DATABASE),
        "supported_risks": len(RISK_TAXONOMY), 
        "country_synonyms": len(COUNTRY_SYNONYMS),
        "risk_aliases": len(ALL_RISK_ALIASES),
        "nlp_available": nlp is not None,
        "cache_enabled": True,
        "service_version": "2.0.0-professional"
    }
