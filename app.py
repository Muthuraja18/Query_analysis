import os
import pandas as pd
import numpy as np
import requests
from flask import Flask, render_template, request, jsonify
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
from datetime import datetime

app = Flask(__name__)

# ===================== GROQ =====================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ===================== DATA =====================
CSV_PATH = "context.csv"
OUTPUT_CSV = "query_logs.csv"

dataset = pd.read_csv(CSV_PATH, encoding="latin1")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ===================== HELPERS =====================
def analyze_sentiment(text):
    blob = TextBlob(text)
    score = blob.sentiment.polarity
    if score > 0:
        return "Positive", score, "😊"
    elif score < 0:
        return "Negative", score, "😞"
    return "Neutral", score, "😐"

def get_groq_response(query):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": query}]
    }
    r = requests.post(GROQ_API_URL, headers=headers, json=payload)
    return r.json()["choices"][0]["message"]["content"]

def find_answer(query):
    query_emb = embedding_model.encode([query])
    combined = (
        dataset["question"].fillna("") + " " +
        dataset["product"].fillna("") + " " +
        dataset["features"].fillna("")
    )
    emb = embedding_model.encode(combined.tolist())
    sim = cosine_similarity(query_emb, emb)
    idx = np.argmax(sim)

    row = dataset.iloc[idx]
    return {
        "product": row["product"],
        "price": row["price"],
        "features": row["features"],
        "ratings": row["ratings"],
        "discount": row["discount"]
    }

# ===================== ROUTES =====================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_query = request.json["query"]

    groq_reply = get_groq_response(user_query)
    product_info = find_answer(user_query)
    sentiment, score, emoji = analyze_sentiment(user_query)

    log = {
        "question": user_query,
        "product": product_info["product"],
        "Timestamp": datetime.now()
    }
    pd.DataFrame([log]).to_csv(
        OUTPUT_CSV,
        mode="a",
        header=not os.path.exists(OUTPUT_CSV),
        index=False
    )

    return jsonify({
        "groq": groq_reply,
        "product": product_info,
        "sentiment": sentiment,
        "emoji": emoji
    })

if __name__ == "__main__":
    app.run()
