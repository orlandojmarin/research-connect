# utils/firebase_query_utils.py
from typing import List, Dict, Any
from utils.auth_utils import db

def _norm(x: Any) -> str:
    return str(x or "").strip().lower()

def _safe_bool(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    return _norm(v) in {"1", "true", "yes", "paid"}

def get_all_listings() -> List[Dict[str, Any]]:
    """Return all listings from Firebase with listing_id added."""
    data = db.child("listings").get().val()
    if not data:
        return []
    out = []
    for lid, item in data.items():
        if isinstance(item, dict):
            out.append({**item, "listing_id": lid})
    return out

def search_listings_by_keyword(keyword: str) -> List[Dict[str, Any]]:
    if not keyword:
        return []
    kw = _norm(keyword)
    hits = []
    for it in get_all_listings():
        hay = " | ".join([
            _norm(it.get("title")),
            _norm(it.get("skills")),
            _norm(it.get("summary")),
            _norm(it.get("department")),
            _norm(it.get("location")),
        ])
        if kw in hay:
            hits.append(it)
    return hits

def search_listings_by_faculty(faculty_query: str) -> List[Dict[str, Any]]:
    if not faculty_query:
        return []
    q = _norm(faculty_query)
    hits = []
    for it in get_all_listings():
        pi = _norm(it.get("pi"))
        fe = _norm(it.get("faculty_email"))
        if q in pi or q in fe:
            hits.append(it)
    return hits

def search_paid_listings(only_paid: bool = True) -> List[Dict[str, Any]]:
    hits = []
    for it in get_all_listings():
        is_paid = _safe_bool(it.get("paid"))
        if (only_paid and is_paid) or (not only_paid and not is_paid):
            hits.append(it)
    return hits

def format_listings_as_context(listings: List[Dict[str, Any]], max_items: int = 8) -> str:
    if not listings:
        return ""
    lines = []
    for i, l in enumerate(listings[:max_items], start=1):
        title = l.get("title", "Untitled")
        pi = l.get("pi") or l.get("faculty_email") or "Unknown faculty"
        paid = "Paid" if _safe_bool(l.get("paid")) else "Unpaid"
        hrs = l.get("hours_per_week", "N/A")
        loc = l.get("location") or l.get("department") or "N/A"
        skills = l.get("skills", "N/A")
        summary = l.get("summary", "")
        lines.append(
            f"[{i}] {title} — {pi} | {paid}, {hrs} hrs/wk | {loc}\n"
            f"    Skills: {skills}\n"
            f"    Summary: {summary}"
        )
    return "RESEARCH LISTINGS (Firebase):\n" + "\n".join(lines)
