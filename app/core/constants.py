"""
Centralized application constants to ensure single source of truth across schemas, services, and web routers.
"""

ALLOWED_RESOURCE_TYPES = [
    "Opportunity",
    "Course",
    "Scholarship",
    "Job",
    "Internship",
    "Event",
    "Community Service",
    "Tool",
    "Support",
    "Other"
]

ALLOWED_RESOURCE_STATUSES = [
    "pending",
    "published",
    "rejected",
    "archived"
]

ALLOWED_REPORT_REASONS = [
    "broken_link",
    "incorrect",
    "spam",
    "misleading",
    "inappropriate",
    "duplicate",
    "other"
]

ALLOWED_REPORT_STATUSES = [
    "pending",
    "reviewed",
    "dismissed"
]

ALLOWED_URL_SCHEMES = ("http://", "https://")
FORBIDDEN_URL_SCHEMES = ("javascript:", "data:", "file:", "vbscript:", "blob:")
