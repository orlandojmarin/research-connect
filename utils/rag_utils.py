#Sana
import os
import argparse
import json
from typing import List, Tuple
from utils.firebase_query_utils import search_listings_by_keywords, format_listings_brief
from sentence_transformers import SentenceTransformer
import faiss
import re
import numpy as np

DATA_FOLDER = "Data"
INDEX_FOLDER = ".rag"
INDEX_FILE = os.path.join(INDEX_FOLDER, "index.faiss")
META_FILE = os.path.join(INDEX_FOLDER, "meta.json")

EMBED_MODEL = "all-MiniLM-L6-v2"

from utils.firebase_query_utils import get_all_listings

def get_firebase_listings():
    """
    Fetch research listings from Firebase and return as plain text
    for RAG context retrieval.
    """
    try:
        listings_text = get_all_listings()
        if listings_text and isinstance(listings_text, str):
            return listings_text
        return ""
    except Exception as e:
        print(f"[RAG] Firebase fetch error: {e}")
        return ""
# ---------- Load Embedding Model ----------
def load_model():
    return SentenceTransformer(EMBED_MODEL)


# ---------- Read text files ----------
def load_text_files() -> List[Tuple[str, str]]:
    docs = []
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".txt"):
            path = os.path.join(DATA_FOLDER, filename)
            with open(path, "r", encoding="utf-8") as f:
                docs.append((filename.replace(".txt", ""), f.read()))
    return docs


# ---------- Chunk text ----------
def chunk_text(text: str, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]


# ---------- Build index ----------
def build_index():
    os.makedirs(INDEX_FOLDER, exist_ok=True)
    model = load_model()
    docs = load_text_files()

    all_chunks = []
    meta = []

    for title, content in docs:
        chunks = chunk_text(content)
        for chunk in chunks:
            all_chunks.append(chunk)
            meta.append({"title": title})

    print(f"[RAG] Indexing {len(all_chunks)} chunks from {len(docs)} files...")

    embeddings = model.encode(all_chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

    faiss.write_index(index, INDEX_FILE)

    with open(META_FILE, "w") as f:
        json.dump({"chunks": all_chunks, "meta": meta}, f)

    print("[RAG] ✅ Index built successfully!")


# ---------- Search ----------
def search(query: str, top_k=3):
    model = load_model()
    index = faiss.read_index(INDEX_FILE)

    with open(META_FILE, "r") as f:
        meta_data = json.load(f)

    query_embedding = model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        if idx < len(meta_data["chunks"]):
            results.append(meta_data["chunks"][idx])
    return results

# ---------- Simple fact extractors ----------
_PHONE_RE = re.compile(r'(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})')
_EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

def _extract_phones(text: str):
    raw = _PHONE_RE.findall(text)
    cleaned = []
    for n in raw:
        digits = re.sub(r'\D', '', n)
        if len(digits) == 10:
            cleaned.append(f"({digits[:3]}) {digits[3:6]}-{digits[6:]}")
        elif len(digits) == 11 and digits[0] == "1":
            cleaned.append(f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}")
    # keep unique, stable order
    seen = set()
    out = []
    for x in cleaned:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def _extract_emails(text: str):
    return sorted(set(_EMAIL_RE.findall(text)))

# ---------- Helper ----------
def _scope_to_keywords(texts, keywords):
    """
    Keep only lines that contain any of the keywords (case-insensitive).
    If none match, return the full joined text.
    """
    joined = "\n".join(texts)
    lines = [ln for ln in joined.splitlines() if ln.strip()]
    if not keywords:
        return joined
    keys = [k.lower() for k in keywords]
    scoped = [ln for ln in lines if any(k in ln.lower() for k in keys)]
    return "\n".join(scoped) if scoped else joined



# ---------- Generate Answer ----------

def answer_question(query: str):
    q = query.lower()

    # ---- 1) If the user asks about research listings, use Firebase ----
    listing_triggers = [
        "listing", "listings", "research", "project", "projects",
        "opening", "openings", "paid", "unpaid", "hours", "faculty", "professor", "dr."
    ]
    if any(t in q for t in listing_triggers):
        matches = search_listings_by_keywords(query, max_results=5)
        if matches:
            return format_listings_brief(matches)
        else:
            return "No research listings match your query in the database."

    # ---- 2) Otherwise, use the normal RAG-on-.txt process ----
    results = search(query, top_k=5)
    if not results:
        return "Sorry, I don't have enough information to answer that."

    # --- NEW: scope the retrieved text to the entity in the question ---
    scope_keys = []
    if any(k in q for k in ["ihub", "i hub", "innovation hub"]):
        scope_keys = ["ihub", "innovation hub"]
    elif "career" in q:
        scope_keys = ["career", "career services", "career office"]

    scoped_text = _scope_to_keywords(results, scope_keys)

    # 1) Direct facts: phone / email from scoped text first
    if any(k in q for k in ["phone", "telephone", "call", "number", "contact number", "phone number"]):
        phones = _extract_phones(scoped_text)
        if phones:
            return f"Phone: {phones[0]}"

    if "email" in q or "e-mail" in q:
        emails = _extract_emails(scoped_text)
        if emails:
            return f"Email: {emails[0]}"

    # 2) Concise sentence/line that best matches query tokens (from scoped text)
    lines = [ln.strip() for ln in scoped_text.splitlines() if ln.strip()]
    tokens = [t for t in re.findall(r"\w+", q) if len(t) > 3]

    best_line = ""
    best_score = -1
    for ln in lines:
        score = sum(t in ln.lower() for t in tokens)
        if score > best_score:
            best_score = score
            best_line = ln

    if best_line:
        return best_line[:300]

    # 3) Fallback: short snippet from the first result
    return results[0][:300]


# ---------- CLI Commands ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--ask", type=str)
    args = parser.parse_args()

    if args.build:
        build_index()

    if args.ask:
        print("=== ANSWER ===")
        print(answer_question(args.ask))


# ---------- Chatbot Callable Function ----------
def answer_from_rag(question: str) -> str:
    """Use this in chatbot."""
    return answer_question(question)

# ---------- Simple helper for Streamlit ----------
def ask_rag(query: str):
    from sentence_transformers import SentenceTransformer
    import faiss, json, numpy as np
    import re

    # Load model and index
    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index(".rag/index.faiss")

    # Load metadata
    with open(".rag/meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    # Encode query and search
    q_emb = model.encode([query])
    D, I = index.search(np.array(q_emb).astype("float32"), 1)
    text = meta["chunks"][I[0][0]]

    # --- Simple cleanup filter ---
    # If user asks for phone, extract only the phone
    if "phone" in query.lower():
        match = re.search(r"\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}", text)
        return match.group(0) if match else text[:300]

    # If user asks for email
    if "email" in query.lower():
        match = re.search(r"[\w\.-]+@[\w\.-]+", text)
        return match.group(0) if match else text[:300]

    # Otherwise return the first 300 characters (short but clear)
    return text[:300] + "..."

if __name__ == "__main__":
    main()
