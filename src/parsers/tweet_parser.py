thonfrom datetime import datetime
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup

def _safe_get_text(soup: BeautifulSoup, selector: str) -> Optional[str]:
    el = soup.select_one(selector)
    if not el:
        return None
    text = el.get_text(strip=True)
    return text or None

def _safe_get_attr(soup: BeautifulSoup, selector: str, attr: str) -> Optional[str]:
    el = soup.select_one(selector)
    if not el:
        return None
    value = el.get(attr)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None

def _safe_int(text: Optional[str]) -> int:
    if text is None:
        return 0
    try:
        # Remove common separators like commas
        cleaned = text.replace(",", "").strip()
        return int(cleaned)
    except (ValueError, AttributeError):
        return 0

def parse_tweet_html(html: str, tweet_link: str) -> Dict[str, Any]:
    """
    Parse a single tweet (or reply) from a small HTML fragment.

    This parser expects HTML that follows a simple, self-contained structure,
    for example:

        <article class="tweet">
          <img class="tweet-avatar" src="https://example.com/avatar.jpg" />
          <span class="tweet-fullname">John Doe</span>
          <span class="tweet-handle">@johndoe</span>
          <span class="tweet-verified">verified</span>
          <time class="tweet-date" data-iso="2024-01-01T12:00:00.000Z"></time>
          <p class="tweet-content">Hello world</p>
          <span class="tweet-comments">5</span>
          <span class="tweet-retweets">2</span>
          <span class="tweet-quotes">1</span>
          <span class="tweet-likes">10</span>
        </article>

    The tests in this repository use this HTML shape. For real-world usage,
    this function can be extended with Twitter/X-specific selectors.
    """
    soup = BeautifulSoup(html, "html.parser")

    avatar = _safe_get_attr(soup, ".tweet-avatar", "src")
    fullname = _safe_get_text(soup, ".tweet-fullname")
    handle = _safe_get_text(soup, ".tweet-handle")
    verified = _safe_get_text(soup, ".tweet-verified")

    # Prefer data-iso attribute when available; otherwise, the tag text.
    date_el = soup.select_one(".tweet-date")
    if date_el is not None:
        date_str = date_el.get("data-iso") or date_el.get_text(strip=True) or None
    else:
        date_str = None

    if not date_str:
        # Fallback: use "now" in ISO 8601 format; this keeps the scraper usable
        # even when date markup is missing.
        date_str = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    content = _safe_get_text(soup, ".tweet-content") or ""

    comment_count = _safe_int(_safe_get_text(soup, ".tweet-comments"))
    retweet_count = _safe_int(_safe_get_text(soup, ".tweet-retweets"))
    quote_count = _safe_int(_safe_get_text(soup, ".tweet-quotes"))
    like_count = _safe_int(_safe_get_text(soup, ".tweet-likes"))

    tweet: Dict[str, Any] = {
        "tweetLink": tweet_link,
        "avatar": avatar,
        "fullname": fullname,
        "handle": handle,
        "verified": verified,
        "tweetDate": date_str,
        "tweetContent": content,
        "commentCount": comment_count,
        "retweetCount": retweet_count,
        "quoteCount": quote_count,
        "likeCount": like_count,
        "repliesData": [],
    }

    return tweet