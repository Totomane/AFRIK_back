# backend/services/podcast_generator.py
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from services.text_podcast import PodcastService  # ✅ corrigé l'import

# Charger les variables d'environnement depuis .env
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")
if not ELEVENLABS_API_KEY or not VOICE_ID:
    raise ValueError("⚠️ ELEVENLABS_API_KEY et VOICE_ID doivent être définis dans le fichier .env")

# Dossiers de sortie
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
MEDIA_DIR = os.path.join(BASE_DIR, "media")
PODCAST_DIR = os.path.join(MEDIA_DIR, "podcast")
TEXT_DIR = os.path.join(MEDIA_DIR, "texts")

# Crée les dossiers si absents
os.makedirs(PODCAST_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)


def generate_podcast(country: str, risks: list[str], year: int, title: str = "podcast"):
    """
    Génère un podcast audio (mp3) dans backend/media/podcast
    et sauvegarde le texte dans backend/media/texts
    """

    # 1. Générer le script journalistique avec Groq
    print(f"🎙️ Génération du script pour {country}, année {year}, risques: {', '.join(risks)}...")
    text_path = PodcastService.generate_podcast_text(country, risks, year)

    # Lire le contenu du fichier texte généré
    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Créer un nouveau nom de fichier basé sur l'heure
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Sauvegarde une copie du texte pour traçabilité
    text_filename = os.path.join(TEXT_DIR, f"{title}_{date_str}.txt")
    with open(text_filename, "w", encoding="utf-8") as f:
        f.write(text)

    # 2. Convertir en audio via ElevenLabs
    mp3_filename = os.path.join(PODCAST_DIR, f"{title}_{date_str}.mp3")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text
    }

    print("🔊 Conversion du texte en audio avec ElevenLabs...")
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        with open(mp3_filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Podcast généré : {mp3_filename}")
        return mp3_filename, text_filename
    else:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        raise RuntimeError(f"Erreur ElevenLabs: {response.text}")


def main():
    print("\n--- Générateur de Podcast Avancé ---")
    country = input("Pays : ")
    risks = input("Risques (séparés par des virgules) : ").split(",")
    year = int(input("Année : "))
    title = input("Titre du podcast : ") or "podcast"

    generate_podcast(country.strip(), [r.strip() for r in risks], year, title)


if __name__ == "__main__":
    main()
