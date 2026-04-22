"""HTML sanitization utilities for input validation."""

import re
from html.parser import HTMLParser


class HTMLStripper(HTMLParser):
    """HTML Parser that strips all tags and extracts text content."""

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_starttag(self, tag, attrs):
        """Ignore start tags - strip them completely."""
        pass

    def handle_endtag(self, tag):
        """Ignore end tags - strip them completely."""
        pass

    def handle_data(self, d):
        """Collect text content."""
        self.text.append(d)

    def get_data(self):
        """Return accumulated text."""
        return ''.join(self.text)

    def error(self, message):
        """Handle parsing errors gracefully."""
        pass


def strip_html(html_content: str | None) -> str | None:
    """
    Strip all HTML tags from a string.

    Args:
        html_content: String that may contain HTML tags

    Returns:
        String with all HTML tags removed, or None if input was None
    """
    if html_content is None:
        return None

    # Handle empty strings
    if not html_content:
        return html_content

    # Strip HTML tags
    stripper = HTMLStripper()
    try:
        stripper.feed(html_content)
        result = stripper.get_data()
        return result
    except Exception:
        # Fallback: use regex-based stripping for malformed HTML
        # This regex removes anything that looks like a tag: <...>
        cleaned = re.sub(r'<[^>]+>', '', html_content)
        return cleaned
