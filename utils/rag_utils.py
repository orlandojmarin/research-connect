# Sana 

from typing import List
import re

# Firebase listing imports
from utils.firebase_query_utils import (
    search_listings_by_keywords,
    format_listings_brief,
)

# -----------------------------------------------------
# No more FAISS, no more /Data folder, no more chunks
# -----------------------------------------------------

# Simple regex for phone & email extraction
_PHONE_RE = re.compile(r'(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})')
_EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')


def _extract_phones(text: str):
    """Extract phone numbers from text."""
    raw = _PHONE_RE.findall(text)
    cleaned = []
    for n in raw:
        digits = re.sub(r'\D', '', n)
        if len(digits) == 10:
            cleaned.append(f"({digits[:3]}) {digits[3:6]}-{digits[6:]}")
        elif len(digits) == 11 and digits[0] == "1":
            cleaned.append(f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}")
    return list(dict.fromkeys(cleaned))  # unique


def _extract_emails(text: str):
    """Extract emails from text."""
    return list(dict.fromkeys(_EMAIL_RE.findall(text)))


# -----------------------------------------------------
# MAIN FUNCTION THE CHATBOT USES
# -----------------------------------------------------
def answer_question(query: str) -> str:
    q = query.lower()

    # ---------------------------
    # 1. LISTINGS QUESTIONS → FIREBASE
    # ---------------------------
    listing_triggers = [
        "listing", "listings", "research", "project", "projects",
        "opening", "openings", "paid", "unpaid", "hours",
        "faculty", "professor", "dr."
    ]

    if any(t in q for t in listing_triggers):
        matches = search_listings_by_keywords(query, max_results=5)
        if matches:
            return format_listings_brief(matches)
        else:
            return "No research listings match your query in the database."

    # ---------------------------
    # 2. GENERAL QUESTION → no txt RAG anymore
    # ---------------------------
    # Since we removed .txt RAG, we simply say:
    return "I don’t have information about that in my current data sources."


# -----------------------------------------------------
# Streamlit helper (kept for compatibility)
# -----------------------------------------------------
def ask_rag(query: str):
    return answer_question(query)


# -----------------------------------------------------
# CLI mode (optional)
# -----------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--ask", type=str)
    args = parser.parse_args()

    if args.ask:
        print("=== ANSWER ===")
        print(answer_question(args.ask))


if __name__ == "__main__":
    main()
