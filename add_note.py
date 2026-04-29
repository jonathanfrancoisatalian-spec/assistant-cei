
import os
import json
from datetime import datetime
from openai import OpenAI

# =========================
# CONFIG
# =========================

client = OpenAI(api_key="OPENAI_API_KEY")  # ⚠️ mets ta clé via variable d'environnement idéalement

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audios")
DB_FILE = os.path.join(BASE_DIR, "knowledge.json")

SUPPORTED = (".wav", ".mp3", ".m4a", ".ogg", ".flac")

# =========================
# EXTRACT INFO
# =========================

def extract_info(filename):
    name = os.path.splitext(filename)[0]
    parts = name.split("_")

    try:
        date = f"{parts[2]}/{parts[1]}/{parts[0]}"
        client = " ".join(parts[3:])
    except IndexError:
        date = "date inconnue"
        client = "client inconnu"

    return date, client

# =========================
# LOAD DATA
# =========================

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

done_files = {entry.get("file") for entry in data}
print("📚 Fichiers déjà traités :", done_files)

# =========================
# CLEAN NOTE
# =========================

def clean_note(text, date, client_name):

    prompt = f"""
Transforme ce texte en note claire.

Commence IMPÉRATIVEMENT par :
"Le {date}, client : {client_name}"

Fais des phrases propres en français.
Structure en paragraphes.
Ne coupe aucune information.
Fais une transcription complète mais avec des phrases correctes.

Texte :
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

# =========================
# PROCESS AUDIO
# =========================

def process_audio(path, filename):

    print(f"\n🎤 Traitement : {filename}")

    full_text = ""

    try:
        # 👉 Si fichier trop gros → découpage
        if os.path.getsize(path) > 25 * 1024 * 1024:
            print("⚠️ Fichier trop gros → découpage")

            import subprocess

            subprocess.run([
                "ffmpeg", "-i", path,
                "-f", "segment",
                "-segment_time", "300",
                "-c", "copy",
                "temp_%03d.wav"
            ])

            for temp_file in sorted(os.listdir()):
                if temp_file.startswith("temp_") and temp_file.endswith(".wav"):

                    print("➡️ morceau :", temp_file)

                    with open(temp_file, "rb") as audio:
                        transcript = client.audio.transcriptions.create(
                            file=audio,
                            model="whisper-1",
                            language="fr"
                        )

                    full_text += transcript.text + "\n"

                    os.remove(temp_file)

        else:
            print("➡️ fichier normal")

            with open(path, "rb") as audio:
                transcript = client.audio.transcriptions.create(
                    file=audio,
                    model="whisper-1",
                    language="fr"
                )

            full_text = transcript.text

        print("✅ Transcription OK")

        # 👉 récupération date + client
        date, client_name = extract_info(filename)
        print(f"📅 {date} | 👤 {client_name}")

        # 👉 génération note
        note = clean_note(full_text, date, client_name)

        entry = {
            "id": len(data) + 1,
            "file": filename,
            "note": note
        }

        data.append(entry)

        print(f"✅ Ajouté : {filename}")

    except Exception as e:
        print("❌ ERREUR :", e)

# =========================
# MAIN
# =========================

if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)
    print(f"📁 Dossier '{AUDIO_DIR}' créé. Mets tes audios dedans.")
    input("Appuie sur Entrée...")
    exit()

try:
    print("📂 Fichiers trouvés :", os.listdir(AUDIO_DIR))

    for file in os.listdir(AUDIO_DIR):

        print("➡️ Analyse :", repr(file))

        if not file.lower().endswith(SUPPORTED):
            print("❌ Mauvais format")
            continue

        if file in done_files:
            print("⏭ Déjà traité :", file)
            continue

        full_path = os.path.join(AUDIO_DIR, file)

        process_audio(full_path, file)

except Exception as e:
    print("💥 ERREUR GLOBALE :", e)

# =========================
# SAVE
# =========================

with open(DB_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\n🎉 Synchronisation terminée")

input("Appuie sur Entrée pour fermer...")
