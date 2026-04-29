import json
import streamlit as st
from openai import OpenAI

# =========================
# CONFIG
# =========================

import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DB_FILE = "knowledge.json"

# =========================
# LOAD DATA
# =========================

try:
    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except:
    data = []

# =========================
# UI
# =========================

st.title("🧠 Assistant CEI (by Jonathan F)")

# Mémoire chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input utilisateur (UNE SEULE FOIS)
question = st.chat_input("Pose ta question...")

# Traitement
if question:

    # Afficher + stocker question
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Construire contexte
    context = ""
    for entry in data:
        text = entry.get("note") or entry.get("raw_text", "")
        context += f"\nNOTE:\n{text}\n---\n"

    # Prompt
    prompt = f"""
Tu es un assistant technique.

Tu DOIS répondre en DEUX parties STRICTEMENT :

------------------------------
RÉPONSE 1 - BASÉE SUR LES NOTES
------------------------------
- Utilise UNIQUEMENT les NOTES
- Si l'information n'existe pas, écris EXACTEMENT :
Je n'ai pas encore cette information dans ma base.

------------------------------
RÉPONSE 2 - CONNAISSANCE GÉNÉRALE
------------------------------
- En t'appuyant sur les notes et en utilisant des connaissance personnels.
-Tu sais dire si les notes sont douteuse et tu peux proposer un correctif sur une information.
- Si tu corrige quelques chose, dit le.


NOTES:
{context}

QUESTION:
{question}
"""

    # Appel IA
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Respecte STRICTEMENT le format demandé."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content

    # Afficher + stocker réponse
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    with st.chat_message("assistant"):
        st.markdown(answer)