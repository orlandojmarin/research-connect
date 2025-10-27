from utils.firebase_query_utils import (
    get_all_listings, search_listings_by_keyword,
    search_listings_by_faculty, search_paid_listings, format_listings_as_context
)

lst = get_all_listings()
print("TOTAL LISTINGS:", len(lst))

print("\n-- KEYWORD: 'machine learning' --")
print(format_listings_as_context(search_listings_by_keyword("machine learning")))

print("\n-- FACULTY: 'Dr.' --")
print(format_listings_as_context(search_listings_by_faculty("Dr.")))

print("\n-- PAID ONLY --")
print(format_listings_as_context(search_paid_listings(True)))
