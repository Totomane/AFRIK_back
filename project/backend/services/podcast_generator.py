import requests


ELEVENLABS_VOICE_ID = 'your_voice_id'  # e.g., 'Rachel'
REPORT_TEXT = "Your report text goes here."
OUTPUT_MP3_PATH = 'output_podcast.mp3'

def generate_podcast(report_text, output_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": report_text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"Podcast generated: {output_path}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    generate_podcast(REPORT_TEXT, OUTPUT_MP3_PATH)