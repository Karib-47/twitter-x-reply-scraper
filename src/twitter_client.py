thonimport json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

from utils.logging_utils import get_logger
from utils.rate_limiter import RateLimiter
from parsers.tweet_parser import parse_tweet_html
from parsers.reply_parser import parse_replies

@dataclass
class TwitterClientConfig:
    user_agent: str
    max_search_results: int
    max_replies: int
    rate_limit_per_minute: int
    timeout: float

class TwitterClient:
    """
    Light-weight HTML-based scraper client for public Twitter/X pages.

    It does not use authentication and is designed as an educational,
    best-effort implementation. It may break if Twitter/X changes markup,
    but the code is fully runnable and testable.
    """

    def __init__(
        self,
        user_agent: str,
        max_search_results: int = 50,
        max_replies: int = 50,
        rate_limit_per_minute: int = 20,
        timeout: float = 15.0,
    ) -> None:
        self.config = TwitterClientConfig(
            user_agent=user_agent,
            max_search_results=max_search_results,
            max_replies=max_replies,
            rate_limit_per_minute=rate_limit_per_minute,
            timeout=timeout,
        )
        self.logger = get_logger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": self.config.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )
        # Basic rate limiter, total calls per minute
        self.rate_limiter = RateLimiter(
            calls=self.config.rate_limit_per_minute,
            period=60.0,
        )

    def _get_html(self, url: str) -> Optional[str]:
        """
        Fetches raw HTML for a given URL with timeout, rate limiting,
        and basic error handling.
        """
        self.rate_limiter.acquire()
        try:
            self.logger.debug("Fetching URL: %s", url)
            response = self.session.get(url, timeout=self.config.timeout)
            response.raise_for_status()
            self.logger.debug("Fetched %d bytes from %s", len(response.text), url)
            return response.text
        except requests.RequestException as exc:
            self.logger.warning("Failed to fetch %s: %s", url, exc)
            return None

    def fetch_conversation(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a single conversation (the main tweet plus replies) for the given URL.

        Returns a dictionary matching the documented output schema, or None
        if the page could not be loaded or parsed.
        """
        html = self._get_html(url)
        if html is None:
            return None

        try:
            tweet = parse_tweet_html(html, tweet_link=url)
            replies = parse_replies(html, base_tweet_link=url, max_replies=self.config.max_replies)
            tweet["repliesData"] = replies
            return tweet
        except Exception as exc:
            self.logger.error("Failed to parse conversation for %s: %s", url, exc, exc_info=True)
            return None

    def scrape(self, start_urls: List[str]) -> List[Dict[str, Any]]:
        """
        Scrape up to max_search_results tweets (and their replies) starting
        from the list of URLs.

        Each URL is treated as an independent conversation entry point.
        """
        results: List[Dict[str, Any]] = []
        for url in start_urls:
            if len(results) >= self.config.max_search_results:
                self.logger.info("Reached maxSearchResults=%d, stopping.", self.config.max_search_results)
                break

            self.logger.info("Scraping conversation for %s", url)
            conversation = self.fetch_conversation(url)
            if conversation is None:
                self.logger.info("Skipping URL due to previous errors: %s", url)
                continue

            results.append(conversation)

        # Ensure the output is JSON serializable (e.g. datetimes as strings).
        # Our parsers already do this, but we defensively re-encode/parse.
        try:
            serialized = json.loads(json.dumps(results, ensure_ascii=False, default=str))
        except TypeError:
            # As a last resort, convert everything to strings (should not happen with current parsers).
            self.logger.warning("Encountered non-serializable objects, coercing to strings.")
            serialized = json.loads(json.dumps(results, ensure_ascii=False, default=str))

        return serialized