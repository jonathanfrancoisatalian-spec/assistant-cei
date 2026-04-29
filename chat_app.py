import os
import json
import streamlit as st
from openai import OpenAI

st.write("DEBUG KEY:", os.getenv("OPENAI_API_KEY"))

# =========================
# CONFIGURATION
# =========================

# ⚠️ Mets ta vraie clé OpenAI ici
OPENAI_KEY = "OPENAI_API_KEY"

DB_FILE = "knowledge.json"

client = OpenAI(api_key=OPENAI_KEY)


# =========================
# CHARGER LA BASE
# =========================

try:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except:
    data = []


# =========================
# CONFIG PAGE
# =========================

st.set_page_config(
    page_title="Assistant Intelligent",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 Assistant Intelligent")
st.markdown("Base de connaissances personnelle")


# =========================
# SESSION STATE
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processing" not in st.session_state:
    st.session_state.processing = False


# =========================
# AFFICHAGE HISTORIQUE
# =========================

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# =========================
# INPUT UTILISATEUR
# =========================

question = st.chat_input("Pose ta question...")


# =========================
# TRAITEMENT CHAT
# =========================

if question and not st.session_state.processing:

    st.session_state.processing = True


    # Sauver question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)


    # Construire le contexte depuis la base
    context = ""

    for entry in data:

        text = entry.get("note") or entry.get("raw_text", "")

        context += f"""
NOTE:
{text}
---
"""


    # Prompt principal
    prompt = f"""
Tu es mon assistant personnel basé sur mes notes.
------------------------------
RÉPONSE 1 - BASÉE SUR LES NOTES
------------------------------
- Utilise UNIQUEMENT les NOTES
- Si l'information n'existe pas, écris EXACTEMENT :
Je n'ai pas encore cette information dans ma base.
-Structure avec une belle mise en formes (gras/italique/souligné/emogie/couleur) afin de construire une réponse clair.

------------------------------
RÉPONSE 2 - CONNAISSANCE GÉNÉRALE
------------------------------
- Tu peux utiliser tes connaissances générales
- Donne une réponse claire et utile
-Structure avec une belle mise en formes (gras/italique/souligné/emogie/couleur) afin de construire une réponse clair.

RÈGLES :
- Toujours afficher les 2 parties
- Ne jamais mélanger
- Ne rien ajouter avant ou après


NOTES:
{context}

QUESTION:
{question}

RÉPONSE :
"""


    # Appel IA
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Tu es un assistant professionnel fiable."},
            {"role": "user", "content": prompt}
        ]
    )


    answer = response.choices[0].message.content.strip()


    # Sauver réponse
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    with st.chat_message("assistant"):
        st.markdown(answer)


    st.session_state.processing = False


# =========================
# FOOTER BASE INFO (OPTIONNEL)
# =========================

with st.expander("📚 Infos base de connaissances"):

    st.write("Nombre de notes :", len(data))

    if len(data) == 0:
        st.info("La base est vide pour le moment.")
    else:
        for i, entry in enumerate(data, 1):

            text = entry.get("note") or entry.get("raw_text", "")

            st.markdown(f"**{i}.** {text[:150]}...")
