import re
import nh3

def generate_slug(text: str) -> str:
    """Generate a clean, SEO-friendly URL slug from string text."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug).strip('-')
    return slug

def sanitize_html(html_content: str) -> str:
    """Sanitize user-provided HTML text to prevent XSS attacks while keeping basic text layout."""
    if not html_content:
        return ""
    cleaned = nh3.clean(
        html_content,
        tags={"p", "b", "i", "strong", "em", "ul", "ol", "li", "br", "a"},
        attributes={"a": {"href", "target"}},
        link_rel=None
    )
    return cleaned
