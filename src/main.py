thonimport argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure the src directory is on sys.path so local imports work when running as a script
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from twitter_client import TwitterClient  # type: ignore
from utils.logging_utils import configure_logging, get_logger  # type: ignore

def load_settings(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_output(path: Path, data: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Twitter (X) Reply Scraper - CLI entrypoint"
    )
    parser.add_argument(
        "--settings",
        type=str,
        default=str(BASE_DIR / "config" / "settings.example.json"),
        help="Path to settings JSON file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(BASE_DIR.parent / "data" / "sample-output.json"),
        help="Path to output JSON file",
    )
    return parser.parse_args()

def main() -> None:
    configure_logging()
    logger = get_logger("main")

    args = parse_args()
    settings_path = Path(args.settings)
    output_path = Path(args.output)

    try:
        settings = load_settings(settings_path)
    except Exception as exc:  # pragma: no cover - simple CLI error
        logger.error("Failed to load settings: %s", exc)
        sys.exit(1)

    start_urls = settings.get("startUrls") or []
    if not isinstance(start_urls, list) or not start_urls:
        logger.error("settings.startUrls must be a non-empty list of URLs")
        sys.exit(1)

    max_search_results = int(settings.get("maxSearchResults", 20))
    max_replies = int(settings.get("maxReplies", 20))
    user_agent = settings.get(
        "userAgent",
        "Mozilla/5.0 (compatible; TwitterReplyScraper/1.0; +https://bitbash.dev)",
    )
    rate_limit_per_minute = int(settings.get("rateLimitPerMinute", 20))
    timeout = float(settings.get("requestTimeoutSeconds", 15))

    client = TwitterClient(
        user_agent=user_agent,
        max_search_results=max_search_results,
        max_replies=max_replies,
        rate_limit_per_minute=rate_limit_per_minute,
        timeout=timeout,
    )

    logger.info(
        "Starting scrape for %d start URLs (maxSearchResults=%d, maxReplies=%d)",
        len(start_urls),
        max_search_results,
        max_replies,
    )

    try:
        conversations = client.scrape(start_urls)
    except Exception as exc:  # pragma: no cover - simple CLI error
        logger.error("Scrape failed: %s", exc, exc_info=True)
        sys.exit(1)

    save_output(output_path, conversations)
    logger.info("Scrape finished successfully. Saved %d records to %s", len(conversations), output_path)

if __name__ == "__main__":
    main()