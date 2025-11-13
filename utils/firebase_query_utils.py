# sana - updated to Firebase Admin SDK compatible version 
from firebase_admin import db as admin_db
import re
import json

# -------------------------------------------------
# Helpers to read all listings in raw form
# -------------------------------------------------

def _get_listings_dict():
    """Low-level helper: returns the raw dict from Firebase."""
    listings = admin_db.reference("listings").get()
    return listings or {}

def get_all_listings_raw():
    """
    Return ALL listings as a list of dictionaries.
    Each item is the original listing data + 'listing_id'.
    """
    listings = _get_listings_dict()
    out = []
    for listing_id, data in listings.items():
        if isinstance(data, dict):
            item = data.copy()
            item["listing_id"] = listing_id
            out.append(item)
    return out

def get_all_listings():
    """
    Return a human-readable string of ALL listings.
    Used mainly for building RAG text.
    """
    listings = _get_listings_dict()
    if not listings:
        return "No listings found."

    output = []
    for listing_id, data in listings.items():
        title = data.get("title", "Unknown Title")
        faculty = data.get("pi", "Unknown Faculty")
        department = data.get("department", "Unknown Department")
        skills = data.get("skills", "Not specified")
        duration = data.get("duration", "Not specified")
        start_date = data.get("start_date", "Unknown")
        compensation = data.get("compensation_type", "Unknown")
        hours = data.get("weekly_hours", "Unknown")
        openings = data.get("openings", "Unknown")
        summary = data.get("summary", "No description provided")

        output.append(
            f"Project: {title}\n"
            f"Faculty: {faculty}\n"
            f"Department: {department}\n"
            f"Skills: {skills}\n"
            f"Duration: {duration}, Start Date: {start_date}\n"
            f"Compensation: {compensation}, Hours/Week: {hours}\n"
            f"Openings: {openings}\n"
            f"Description: {summary}\n---"
        )
    
    return "\n\n".join(output)

# -------------------------------------------------
# Simple keyword search (with optional limit)
# -------------------------------------------------

def search_listings_by_keywords(query, max_results=5):
    """
    Rank listings by how many query tokens appear in the JSON of each listing.
    If max_results is None, return ALL matches.
    """
    listings = _get_listings_dict()
    if not listings:
        return []

    q_tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
    results = []

    for key, data in listings.items():
        text = json.dumps(data).lower()
        score = sum(t in text for t in q_tokens) if q_tokens else 1
        if score > 0:
            results.append((score, key, data))

    if not results:
        return []

    results.sort(reverse=True, key=lambda x: x[0])

    docs = [r[2] for r in results]
    if max_results is not None:
        docs = docs[:max_results]
    return docs

# -------------------------------------------------
# Paid / unpaid search
# -------------------------------------------------

def search_paid_listings(is_paid: bool, max_results=None):
    """
    Return listings filtered by compensation_type == 'paid' or 'unpaid'.
    """
    listings = _get_listings_dict()
    if not listings:
        return []

    target = "paid" if is_paid else "unpaid"
    matches = [
        data for data in listings.values()
        if isinstance(data, dict) and data.get("compensation_type", "").lower() == target
    ]

    if max_results is not None:
        matches = matches[:max_results]
    return matches

# -------------------------------------------------
# Faculty / department-based search
# -------------------------------------------------

def search_listings_by_faculty(query, max_results=None):
    """
    If the query mentions a specific professor name, return listings for that PI.
    If it’s generic like 'computer science professors', return all CS department listings.
    """
    listings = _get_listings_dict()
    if not listings:
        return []

    ql = query.lower()
    tokens = [t.lower() for t in re.findall(r"[a-zA-Z]+", ql)]

    results = []

    for key, data in listings.items():
        if not isinstance(data, dict):
            continue

        pi = data.get("pi", "") or ""
        dept = data.get("department", "") or ""
        pi_l = pi.lower()
        dept_l = dept.lower()

        score = 0

        # Any name tokens that appear in PI increase score
        for t in tokens:
            if t in pi_l:
                score += 2

        # Department match (e.g., computer science)
        if "computer" in ql and "science" in ql and "computer science" in dept_l:
            score += 2

        if score > 0:
            results.append((score, key, data))

    # If query is generic "computer science professors" and nothing matched by PI,
    # still return all CS listings
    if not results and "computer" in ql and "science" in ql:
        for key, data in listings.items():
            dept = (data or {}).get("department", "").lower()
            if "computer science" in dept:
                results.append((1, key, data))

    if not results:
        return []

    results.sort(reverse=True, key=lambda x: x[0])

    docs = [r[2] for r in results]
    if max_results is not None:
        docs = docs[:max_results]
    return docs

# -------------------------------------------------
# Brief formatter (unchanged)
# -------------------------------------------------

def format_listings_brief(listings):
    out = []
    for L in listings:
        title = L.get("title", "Untitled")
        pi = L.get("pi", "Unknown PI")
        dept = L.get("department", "Unknown Dept")
        pay = L.get("compensation_type", "unknown")
        pay_rate = L.get("pay_rate", "")
        hours = L.get("weekly_hours", "")
        start = L.get("start_date", "")
        skills = L.get("skills", "")

        # Build the base line EXACTLY like your original
        line = f"- {title} | PI: {pi} | Dept: {dept} | Pay: {pay}"

        # ONLY extra addition: append pay rate if paid
        if pay == "paid" and pay_rate not in ("", None, 0):
            line += f" (${pay_rate}/hour)"

        # Continue your original formatting
        if hours:
            line += f" | Hours/Week: {hours}"

        if start:
            line += f" | Start: {start}"

        if skills:
            line += f" | Skills: {skills}"

        out.append(line)

    return "\n".join(out) if out else "No matching listings found."

from datetime import datetime

def filter_and_group_by_start_date(listings):
    """
    Group listings into upcoming and expired based on start_date.
    Keeps all listings and sorts each group by date.
    Returns (upcoming_list, expired_list).
    """
    today = datetime.today()

    upcoming = []
    expired = []

    for item in listings:
        start = item.get("start_date", "")
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
        except Exception:
            # If date invalid → treat as expired
            expired.append(item)
            continue

        if start_dt >= today:
            upcoming.append(item)
        else:
            expired.append(item)

    # Sort both groups by date
    upcoming.sort(key=lambda x: x.get("start_date", ""))
    expired.sort(key=lambda x: x.get("start_date", ""))

    return upcoming, expired

if __name__ == "__main__":
    print(get_all_listings())
