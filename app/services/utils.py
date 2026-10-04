import re
from urllib.parse import urlparse
import nh3
from app.core.constants import ALLOWED_URL_SCHEMES, FORBIDDEN_URL_SCHEMES

def generate_slug(text: str) -> str:
    """Generate a clean, SEO-friendly URL slug from string text."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug).strip('-')
    return slug

def validate_url_string(url: str) -> bool:
    """
    Robust URL validation using urllib.parse.
    Only allows http:// and https:// schemes.
    Explicitly rejects javascript:, data:, file:, vbscript:, and malformed URLs.
    """
    if not url or not isinstance(url, str):
        return False

    clean_url = url.strip()
    lower_url = clean_url.lower()

    # Reject forbidden scheme prefixes directly
    for forbidden in FORBIDDEN_URL_SCHEMES:
        if lower_url.startswith(forbidden):
            return False

    # Must start with http:// or https://
    if not lower_url.startswith(ALLOWED_URL_SCHEMES):
        return False

    try:
        parsed = urlparse(clean_url)
        if parsed.scheme.lower() not in ("http", "https"):
            return False
        if not parsed.netloc or "." not in parsed.netloc:
            return False
        return True
    except Exception:
        return False

def sanitize_html(html_content: str) -> str:
    """
    Sanitize user-provided HTML text to prevent XSS attacks.
    Restricts allowed tags/attributes and strips unsafe link schemes.
    """
    if not html_content:
        return ""

    # Clean HTML using nh3
    cleaned = nh3.clean(
        html_content,
        tags={"p", "b", "i", "strong", "em", "ul", "ol", "li", "br", "a"},
        attributes={
            "a": {"href", "target"}
        },
        url_schemes={"http", "https"},
        link_rel="noopener noreferrer"
    )
    return cleaned
