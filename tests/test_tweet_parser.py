thonimport sys
from pathlib import Path

# Ensure src/ is importable when running tests from the project root
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from parsers.tweet_parser import parse_tweet_html  # type: ignore

def test_parse_tweet_html_basic():
    html = """
    <article class="tweet">
      <img class="tweet-avatar" src="https://example.com/avatar.jpg" />
      <span class="tweet-fullname">John Doe</span>
      <span class="tweet-handle">@johndoe</span>
      <span class="tweet-verified">verified</span>
      <time class="tweet-date" data-iso="2024-01-01T12:00:00.000Z"></time>
      <p class="tweet-content">Hello from unit test</p>
      <span class="tweet-comments">5</span>
      <span class="tweet-retweets">2</span>
      <span class="tweet-quotes">1</span>
      <span class="tweet-likes">10</span>
    </article>
    """
    tweet_link = "https://x.com/johndoe/status/123"

    result = parse_tweet_html(html, tweet_link=tweet_link)

    assert result["tweetLink"] == tweet_link
    assert result["avatar"] == "https://example.com/avatar.jpg"
    assert result["fullname"] == "John Doe"
    assert result["handle"] == "@johndoe"
    assert result["verified"] == "verified"
    assert result["tweetDate"] == "2024-01-01T12:00:00.000Z"
    assert result["tweetContent"] == "Hello from unit test"
    assert result["commentCount"] == 5
    assert result["retweetCount"] == 2
    assert result["quoteCount"] == 1
    assert result["likeCount"] == 10
    assert isinstance(result["repliesData"], list)