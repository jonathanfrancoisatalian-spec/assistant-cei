import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("test.m4a", "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",
        language="fr"
    )

print("Transcription :")
print(transcript.text)
