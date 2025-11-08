# sana - updated to Firebase Admin SDK compatible version
from firebase_admin import db as admin_db
import re
import json

def get_all_listings():
    listings = admin_db.reference("listings").get()

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

# --- Simple keyword search ---
def search_listings_by_keywords(query, max_results=5):
    listings = admin_db.reference("listings").get()
    if not listings:
        return []

    q_tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
    results = []

    for key, data in listings.items():
        text = json.dumps(data).lower()
        score = sum(t in text for t in q_tokens)
        if score > 0:
            results.append((score, key, data))

    results.sort(reverse=True, key=lambda x: x[0])

    if not results:
        return None

    return [r[2] for r in results[:max_results]]

def format_listings_brief(listings):
    out = []
    for L in listings:
        title = L.get("title", "Untitled")
        pi = L.get("pi", "Unknown PI")
        dept = L.get("department", "Unknown Dept")
        pay = L.get("compensation_type", "unknown")
        hours = L.get("weekly_hours", "")
        start = L.get("start_date", "")
        skills = L.get("skills", "")

        out.append(
            f"- {title} | PI: {pi} | Dept: {dept} | Pay: {pay}"
            + (f" | Hours/Week: {hours}" if hours else "")
            + (f" | Start: {start}" if start else "")
            + (f" | Skills: {skills}" if skills else "")
        )
    return "\n".join(out) if out else "No matching listings found."

if __name__ == "__main__":
    print(get_all_listings())
