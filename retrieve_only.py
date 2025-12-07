from rank_bm25 import BM25Okapi
import json
import os

# 1. Load Data
chunks = []
docs = []
data_path = "../data/kb_chunks.jsonl"

if not os.path.exists(data_path):
    print("Error: kb_chunks.jsonl not found. Run build_kb.py first.")
else:
    with open(data_path, "r", encoding="utf8") as f:
        for line in f:
            obj = json.loads(line)
            chunks.append(obj)
            # Tokenize the 'search_text' (includes plant name + content)
            docs.append(obj.get("search_text", obj["text"]).lower().split())

if not docs:
    print("Error: Database is empty.")
else:
    bm25 = BM25Okapi(docs)
    print("System Ready!")


def chatbot_no_llm(query, k=3):
    """Original CLI helper (kept for debugging / testing)."""
    if not docs:
        return "System not initialized."

    query_tokens = query.lower().split()
    scores = bm25.get_scores(query_tokens)
    top_indices = scores.argsort()[-k:][::-1]

    intents = {
        'water': ['water', 'watering', 'irrigation', 'moisture', 'soak'],
        'sun': ['light', 'sun', 'shade', 'bright', 'indoor', 'outdoor'],
        'soil': ['soil', 'potting', 'mix', 'drainage', 'fertilizer'],
        'care': ['care', 'grow', 'tips'],
    }

    detected_intent = "General Info"
    for intent, keywords in intents.items():
        if any(k in query.lower() for k in keywords):
            detected_intent = intent.capitalize()
            break

    results = []
    seen_text = set()

    for idx in top_indices:
        chunk = chunks[idx]
        score = scores[idx]
        if score == 0:
            continue
        if chunk["text"] in seen_text:
            continue
        seen_text.add(chunk["text"])
        results.append(f"🌱 **{chunk['plant'].title()}**: {chunk['text']}")

    if not results:
        return "I couldn't find specific details on that. Try mentioning the plant name (e.g., 'Aloe water')."

    response = f"**Topic: {detected_intent}**\n\n" + "\n\n".join(results)
    return response


def retrieve_context_for_llm(query, k=4):
    """Clean, LLM‑friendly context for RAG."""
    if not docs:
        return ""

    query_tokens = query.lower().split()
    scores = bm25.get_scores(query_tokens)
    top_indices = scores.argsort()[-k:][::-1]

    results = []
    seen_text = set()

    for idx in top_indices:
        chunk = chunks[idx]
        score = scores[idx]
        if score == 0:
            continue
        if chunk["text"] in seen_text:
            continue
        seen_text.add(chunk["text"])
        # No emojis/markdown – just structured plain text
        results.append(f"Plant: {chunk['plant']}. {chunk['text']}")

    return "\n\n".join(results)
