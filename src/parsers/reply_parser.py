thonfrom typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from parsers.tweet_parser import parse_tweet_html

def parse_replies(html: str, base_tweet_link: str, max_replies: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Parse replies from the tweet HTML.

    This function expects replies to be rendered as a list of HTML elements
    with the `.reply` class. Each `.reply` element can contain the same
    structure as expected by `parse_tweet_html`, for example:

        <li class="reply">
          <article class="tweet">
            ...
          </article>
        </li>

    For each reply, we compute a stable link by appending `#reply-{index}`
    to the base tweet URL when no explicit link is present.
    """
    soup = BeautifulSoup(html, "html.parser")
    reply_nodes = soup.select(".reply")
    replies: List[Dict[str, Any]] = []

    if max_replies is None or max_replies < 0:
        max_replies = len(reply_nodes)

    for idx, reply_node in enumerate(reply_nodes):
        if len(replies) >= max_replies:
            break

        reply_html = str(reply_node)

        # Attempt to find an explicit link inside the reply; otherwise fall back
        # to a synthetic anchor based on the base tweet link and index.
        link_el = reply_node.select_one("a.reply-link")
        if link_el is not None and link_el.get("href"):
            reply_link = link_el.get("href")
        else:
            reply_link = f"{base_tweet_link}#reply-{idx + 1}"

        parsed = parse_tweet_html(reply_html, tweet_link=reply_link)
        replies.append(parsed)

    return replies