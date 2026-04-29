import os
import json
import streamlit as st
from openai import OpenAI

# =========================
# CONFIGURATION
# =========================

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
DB_FILE = "knowledge.json"

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

    # Construire le contexte
    context = ""
    for entry in data:
        text = entry.get("note") or entry.get("raw_text", "")
        context += f"\nNOTE:\n{text}\n---\n"

    # Prompt
    prompt = f"""
Tu es un assistant technique.

------------------------------
RÉPONSE 1 - BASÉE SUR LES NOTES
------------------------------
- Utilise UNIQUEMENT les NOTES
- Si l'information n'existe pas, écris EXACTEMENT :
Je n'ai pas encore cette information dans ma base.

------------------------------
RÉPONSE 2 - CONNAISSANCE GÉNÉRALE
------------------------------
- Utilise tes connaissances générales
- Tu peux corriger les notes si nécessaire

NOTES:
{context}

QUESTION:
{question}
"""

    # Appel IA (nouvelle API)
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    answer = response.output[0].content[0].text

    # Sauver réponse
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.processing = False

# =========================
# FOOTER
# =========================

with st.expander("📚 Infos base de connaissances"):
    st.write("Nombre de notes :", len(data))

    if len(data) == 0:
        st.info("La base est vide pour le moment.")
    else:
        for i, entry in enumerate(data, 1):
            text = entry.get("note") or entry.get("raw_text", "")
            st.markdown(f"**{i}.** {text[:150]}...")
