# firebase_query_utils.py
# SANA - updated to Firebase Admin SDK compatible version

from firebase_admin import db as admin_db
import re
import json
from datetime import datetime

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
        communication = data.get("communication", "Not specified")
        team = data.get("team", "Not specified")

        output.append(
            f"Project: {title}\n"
            f"Faculty: {faculty}\n"
            f"Department: {department}\n"
            f"Skills: {skills}\n"
            f"Duration: {duration}, Start Date: {start_date}\n"
            f"Compensation: {compensation}, Hours/Week: {hours}\n"
            f"Openings: {openings}\n"
            f"Team: {team}\n"
            f"Communication Method: {communication}\n"
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
    Improved faculty search:
    - Detects professor names
    - Detects 'computer science' AND 'cs'
    - Returns ALL CS listings if no specific name matched
    - Removes randomness and failures
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

        pi = (data.get("pi") or "").lower()
        dept = (data.get("department") or "").lower()

        score = 0

        # ------- 1. Professor name matching -------
        for t in tokens:
            if t in pi and len(t) > 2:
                score += 3

        # ------- 2. Computer Science matching -------
        is_cs_query = (
            "computer science" in ql or
            "cs " in ql or ql.endswith(" cs") or ql.startswith("cs")
        )

        if is_cs_query and "computer science" in dept:
            score += 2

        if score > 0:
            results.append((score, key, data))

    # ------- 3. If user asked about CS faculty, return ALL CS listings -------
    if not results:
        is_cs_query = (
            "computer science" in ql or
            "cs " in ql or ql.endswith(" cs") or ql.startswith("cs")
        )
        if is_cs_query:
            cs_results = []
            for key, data in listings.items():
                dept = (data.get("department") or "").lower()
                if "computer science" in dept:
                    cs_results.append((1, key, data))
            if cs_results:
                results = cs_results

    if not results:
        return []

    # Sort by score
    results.sort(reverse=True, key=lambda x: x[0])

    docs = [r[2] for r in results]
    if max_results is not None:
        docs = docs[:max_results]
    return docs

# -------------------------------------------------
# UPDATED: Enhanced brief formatter with ALL fields
# -------------------------------------------------

def format_listings_brief(listings):
    """
    Format listings with comprehensive information including communication preferences.
    Now includes: title, PI, department, pay, hours, start date, skills, 
    communication method, team, and summary.
    """
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
        communication = L.get("communication", "")
        team = L.get("team", "")
        summary = L.get("summary", "")
        openings = L.get("openings", "")
        duration = L.get("duration", "")

        # Build comprehensive listing format
        line = f"- **{title}**\n"
        line += f"  Principal Investigator: {pi}\n"
        line += f"  Department: {dept}\n"
        line += f"  Compensation: {pay}"
        
        if pay == "paid" and pay_rate not in ("", None, 0):
            line += f" (${pay_rate}/hour)"
        
        line += "\n"

        if hours:
            line += f"  Hours/Week: {hours}\n"

        if start:
            line += f"  Start Date: {start}\n"
        
        if duration:
            line += f"  Duration: {duration}\n"
        
        if openings:
            line += f"  Openings: {openings}\n"

        if skills:
            line += f"  Required Skills: {skills}\n"
        
        # CRITICAL: Communication method
        if communication:
            line += f"  **Preferred Communication: {communication}**\n"
        
        # Team information
        if team:
            line += f"  Team Members: {team}\n"
        
        # Summary/description (truncated if too long)
        if summary:
            summary_brief = summary[:200] + "..." if len(summary) > 200 else summary
            line += f"  Description: {summary_brief}\n"

        out.append(line)

    return "\n".join(out) if out else "No matching listings found."

# -------------------------------------------------
# Date filtering helper
# -------------------------------------------------

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