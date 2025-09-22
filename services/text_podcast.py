# service/text_podcast.py


# Use Groq API for podcast text generation (like report_service)
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {GROQ_API_KEY}"}

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
TEXT_DIR = os.path.join(MEDIA_DIR, "texts")
os.makedirs(TEXT_DIR, exist_ok=True)

class PodcastService:
    """
    Service class to generate journalist-style podcast scripts
    using Groq API, formatted for ElevenLabs TTS.
    """

    @staticmethod
    def generate_podcast_text(country: str, risks: list[str], year: int, tone: str = "serious", title: str = "podcast") -> str:
        """
        Generate a journalist-style podcast script and save to media/texts.
        Returns the file path of the saved text.
        """
        risks_text = ", ".join(risks)
        prompt = f"""
        You are a professional French journalist writing a podcast script.
        It must sound natural, detailed, and immersive, with human-like narration,
        pauses, emphasis, prosody, and rhetorical gimmicks.

        Format the output with XML-like tags for TTS engines:
        - <voice emotion=\"{tone}\" style=\"narration\"> ... </voice>
        - <break time=\"500ms\"/>
        - <prosody rate=\"medium\" pitch=\"+2%\"> ... </prosody>
        - <emphasis> ... </emphasis>

        Context:
        - Country: {country}
        - Year: {year}
        - Risks/Topics: {risks_text}

        Instructions:
        - Start with a professional but engaging introduction.
        - Explain the risks in a way that is accessible but detailed.
        - Use statistics, expert quotes, or context when relevant (fabricated but realistic if unknown).
        - Vary rhythm and tone with <prosody> and <break>.
        - End with a strong conclusion, summarizing the situation and outlook.

        Write a full podcast script in French.
        """
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1200
        }
        try:
            response = requests.post(GROQ_URL, headers=HEADERS, json=data)
            if response.status_code != 200:
                raise RuntimeError(f"Erreur API Groq: {response.text}")
            content = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            content = f"⚠️ Erreur génération contenu podcast: {e}"

        # Save to txt file in media/texts
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        text_filename = os.path.join(TEXT_DIR, f"{title}_{date_str}.txt")
        with open(text_filename, "w", encoding="utf-8") as f:
            f.write(content)
        return text_filename


