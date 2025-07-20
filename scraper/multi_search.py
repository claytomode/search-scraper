"""
Functions to cycle through multiple scraper configurations to find search results.

This helps distribute requests and adds resilience if one service is down
or changes its HTML structure.
"""

from collections.abc import Iterable

from scraper.client import AsyncScraper, SyncScraper
from scraper.config import ScraperConfig
from scraper.exceptions import ScraperError
from scraper.models import SearchResult


def search_sync(
    query: str,
    configs: Iterable[ScraperConfig],
    *,
    max_results: int | None = 5,
) -> list[SearchResult] | None:
    """
    Search using multiple scraper configs, trying each one in order.

    Args:
        query: The search query string.
        configs: An iterable of ScraperConfig objects to try.
        max_results: The maximum number of results to return.

    Returns:
        A list of SearchResult objects, an empty list for a successful search
        with no results, or None if all scrape attempts failed with an error.

    Raises:
        ScraperError: If all scrape attempts fail.

    """
    if not configs:
        return None

    for config in configs:
        try:
            with SyncScraper(config=config) as scraper:
                results = scraper.search(query, max_results=max_results)
                if results is not None:
                    return results
        except ScraperError:
            continue
    msg = 'Failed to scrape from all configs.'
    raise ScraperError(msg)


async def search_async(
    query: str,
    configs: Iterable[ScraperConfig],
    *,
    max_results: int | None = 5,
) -> list[SearchResult] | None:
    """
    Search using multiple scraper configs, trying each one in order.

    Args:
        query: The search query string.
        configs: An iterable of ScraperConfig objects to try.
        max_results: The maximum number of results to return.

    Returns:
        A list of SearchResult objects, an empty list for a successful search
        with no results, or None if all scrape attempts failed with an error.

    Raises:
        ScraperError: If all scrape attempts fail.

    """
    if not configs:
        return None

    for config in configs:
        try:
            async with AsyncScraper(config=config) as scraper:
                results = await scraper.search(query, max_results=max_results)
                if results is not None:
                    return results
        except ScraperError:
            continue

    msg = 'Failed to scrape from all configs.'
    raise ScraperError(msg)
