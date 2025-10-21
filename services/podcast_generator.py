# backend/services/podcast_generator.py
import os
import requests
import subprocess   # 🎞️ for running ffmpeg commands
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

    print(f"🎙️ Génération du script pour {country}, année {year}, risques: {', '.join(risks)}...")

    country_clean = country.replace(" ", "-")
    risks_str = "_".join([risk.replace(" ", "-") for risk in risks])
    base_filename = f"{country_clean}_{year}_{risks_str}"
    title = ("Podcast sur la situation au " + country+ " en " + str(year)+ " sur " + ", ".join(risks)).strip()
    description = ("Aujourd'hui un épisode intéressant sur la situation au " + country + " en abordant le sujet de " + ", ".join(risks) + f" en {year}").strip()

    text_path = os.path.join(TEXT_DIR, f"{base_filename}.txt")
    mp3_path = os.path.join(PODCAST_DIR, f"{base_filename}.mp3")

    if os.path.exists(text_path) or os.path.exists(mp3_path):
        raise FileExistsError(f"Podcast files already exist for '{base_filename}'. Please use different parameters or delete existing files.")
    text_path = PodcastService.generate_podcast_text(country, risks, year, title=base_filename)

    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    text_filename = os.path.join(TEXT_DIR, f"{base_filename}.txt")
    with open(text_filename, "w", encoding="utf-8") as f:
        f.write(text)

    # 2. Convertir en audio via ElevenLabs
    mp3_filename = os.path.join(PODCAST_DIR, f"{base_filename}.mp3")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {"text": text}

    print("🔊 Conversion du texte en audio avec ElevenLabs...")
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        with open(mp3_filename, "wb") as f:
            f.write(response.content)
        print(f"✅ Podcast généré : {mp3_filename}")

        # 🎞️ 3. Générer la version MP4 (audiogram teaser)
        cover_path = os.path.join(MEDIA_DIR, "cover.jpg")  # image fixe de fond
        mp4_filename = os.path.join(PODCAST_DIR, f"{base_filename}_video.mp4")

        if not os.path.exists(cover_path):
            print("⚠️ Aucune image 'cover.jpg' trouvée — création du MP4 ignorée.")
        else:
            print("🎞️ Génération du teaser MP4 avec FFmpeg...")
            try:
                # couper à 60 secondes pour réseaux sociaux (modifie -t pour durée)
                command = [
                    "ffmpeg",
                    "-y",  # overwrite existing file
                    "-loop", "1",
                    "-i", cover_path,
                    "-i", mp3_filename,
                    "-c:v", "libx264",
                    "-tune", "stillimage",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-pix_fmt", "yuv420p",
                    "-shortest",
                    "-t", "200",  # durée max du teaser
                    mp4_filename
                ]
                subprocess.run(command, check=True)
                print(f"✅ Teaser vidéo généré : {mp4_filename}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors de la génération du MP4 : {e}")

        return mp3_filename, text_filename

    else:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        raise RuntimeError(f"Erreur ElevenLabs: {response.text}")

def main():
    print("\n--- Générateur de Podcast ---")
    country = input("Pays : ")
    risks = input("Risques (séparés par des virgules) : ").split(",")
    year = int(input("Année : "))
    title = ("Podcast sur " + country).strip()
    description = ("Aujourd'hui un épisode intéressant sur la situation au " + country + " en abordant le sujet de " + ", ".join(risks) + f" en {year}").strip()

    generate_podcast(country.strip(), [r.strip() for r in risks], year, title)

if __name__ == "__main__":
    main()
