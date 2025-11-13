thonimport sys
from pathlib import Path

# Ensure src/ is importable when running tests from the project root
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parsers.reply_parser import parse_replies  # type: ignore

def test_parse_replies_limited_by_max_replies():
    html = """
    <ul class="replies">
      <li class="reply">
        <article class="tweet">
          <img class="tweet-avatar" src="https://example.com/a1.jpg" />
          <span class="tweet-fullname">Alice</span>
          <span class="tweet-handle">@alice</span>
          <time class="tweet-date" data-iso="2024-01-01T13:00:00.000Z"></time>
          <p class="tweet-content">First reply</p>
          <span class="tweet-comments">1</span>
          <span class="tweet-retweets">0</span>
          <span class="tweet-quotes">0</span>
          <span class="tweet-likes">3</span>
        </article>
      </li>
      <li class="reply">
        <article class="tweet">
          <img class="tweet-avatar" src="https://example.com/a2.jpg" />
          <span class="tweet-fullname">Bob</span>
          <span class="tweet-handle">@bob</span>
          <time class="tweet-date" data-iso="2024-01-01T14:00:00.000Z"></time>
          <p class="tweet-content">Second reply</p>
          <span class="tweet-comments">2</span>
          <span class="tweet-retweets">1</span>
          <span class="tweet-quotes">0</span>
          <span class="tweet-likes">5</span>
        </article>
      </li>
    </ul>
    """

    base_link = "https://x.com/johndoe/status/123"
    replies = parse_replies(html, base_tweet_link=base_link, max_replies=1)

    assert len(replies) == 1
    first = replies[0]
    assert first["fullname"] == "Alice"
    assert first["handle"] == "@alice"
    assert first["tweetContent"] == "First reply"
    assert first["likeCount"] == 3
    assert first["tweetLink"] == f"{base_link}#reply-1"

def test_parse_replies_no_limit_defaults_to_all():
    html = """
    <ul class="replies">
      <li class="reply">
        <article class="tweet">
          <img class="tweet-avatar" src="https://example.com/a1.jpg" />
          <span class="tweet-fullname">Alice</span>
          <span class="tweet-handle">@alice</span>
          <time class="tweet-date" data-iso="2024-01-01T13:00:00.000Z"></time>
          <p class="tweet-content">First reply</p>
          <span class="tweet-comments">1</span>
          <span class="tweet-retweets">0</span>
          <span class="tweet-quotes">0</span>
          <span class="tweet-likes">3</span>
        </article>
      </li>
      <li class="reply">
        <article class="tweet">
          <img class="tweet-avatar" src="https://example.com/a2.jpg" />
          <span class="tweet-fullname">Bob</span>
          <span class="tweet-handle">@bob</span>
          <time class="tweet-date" data-iso="2024-01-01T14:00:00.000Z"></time>
          <p class="tweet-content">Second reply</p>
          <span class="tweet-comments">2</span>
          <span class="tweet-retweets">1</span>
          <span class="tweet-quotes">0</span>
          <span class="tweet-likes">5</span>
        </article>
      </li>
    </ul>
    """

    base_link = "https://x.com/johndoe/status/123"
    replies = parse_replies(html, base_tweet_link=base_link, max_replies=None)

    assert len(replies) == 2
    fullnames = {r["fullname"] for r in replies}
    assert fullnames == {"Alice", "Bob"}