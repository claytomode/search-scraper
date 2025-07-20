"""A simple example of using the search-scraper library."""

import asyncio
import sys

from scraper.config import ALL_CONFIGS
from scraper.exceptions import ScraperError
from scraper.multi_search import search_async


async def main() -> None:
    """Demonstrates how to use the scraper library programmatically."""
    if not ALL_CONFIGS:
        print(
            "Error: No scraper configurations found. Ensure 'config.yaml' exists and is valid.",
            file=sys.stderr,
        )
        return

    query = 'claytomode'
    print(f"Searching for: '{query}'")
    print('Using failover mode across all configured scrapers...\n')

    try:
        results = await search_async(query, configs=ALL_CONFIGS, max_results=5)

        if not results:
            print('No results found from any scraper.')
            return

        print(f'--- Found {len(results)} results ---')
        for i, result in enumerate(results, 1):
            print(f'\n[{i}] {result.title}')
            print(f'    URL: {result.url}')
            print(f'    Snippet: {result.snippet}')

    except ScraperError as e:
        print(f'An unexpected error occurred: {e}', file=sys.stderr)


if __name__ == '__main__':
    asyncio.run(main())
