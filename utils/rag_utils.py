# Sana

from typing import List
import re

# Firebase listing imports
from utils.firebase_query_utils import (
    search_listings_by_keywords,
    format_listings_brief,
)

# -----------------------------
# REGEX HELPERS
# -----------------------------
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
    return list(dict.fromkeys(cleaned))


def _extract_emails(text: str):
    return list(dict.fromkeys(_EMAIL_RE.findall(text)))


# =====================================================
# ✨ MAIN FUNCTION — USED BY CHATBOT
# =====================================================
def answer_question(query: str) -> str:
    q = query.lower().strip()

    # ---------------------------------------
    # 1. LISTING-RELATED QUESTIONS → FIREBASE
    # ---------------------------------------
    listing_triggers = [
        "listing", "listings", "research", "project", "projects",
        "opening", "openings", "paid", "unpaid", "hours",
        "faculty", "professor", "dr."
    ]

    if any(t in q for t in listing_triggers):
        matches = search_listings_by_keywords(query, max_results=5)

        if matches:
            return format_listings_brief(matches)

        # Friendly listing fallback
        return (
            "I checked the research listings, but I couldn’t find anything that matches that.\n\n"
            "If you want, I can show you **all available research opportunities**, "
            "or help you look for **paid, unpaid, or faculty-led** projects."
        )

    # ---------------------------------------
    # 2. NON-LISTING QUESTIONS → FRIENDLY REDIRECT
    # ---------------------------------------
    # IMPORTANT: This must be friendly and NOT treated as valid context.
    return (
        "That’s outside what I can access. I work with **SCSU research listings, faculty projects, "
        "and campus resources**.\n\n"
        "I can help you explore:\n"
        "• Current research opportunities\n"
        "• Paid vs unpaid listings\n"
        "• Faculty who have active research\n"
        "• Campus resources that support students\n\n"
        "Feel free to ask about any of those!"
    )
