"""Example usage of the config-driven AsyncScraper."""

import asyncio

from scraper.client import AsyncScraper
from scraper.config import LITE_DUCKDUCKGO_CONFIG
from scraper.exceptions import ScraperError


async def main() -> None:
    """Main function to demonstrate scraper usage."""
    query = 'hello world'
    print(f"Scraping DuckDuckGo Lite for: '{query}'\n")

    # initialize the scraper with the desired site configuration
    scraper_config = LITE_DUCKDUCKGO_CONFIG

    try:
        async with AsyncScraper(config=scraper_config) as scraper:
            results = await scraper.search(query, max_results=5)

            if not results:
                print('No results found.')
                return

            for i, result in enumerate(results, 1):
                print(f'--- Result {i} ---')
                print(f'Title: {result.title}')
                print(f'URL: {result.url}')
                print(f'Snippet: {result.snippet}\n')

    except ScraperError as e:
        print(f'An error occurred: {e}')


if __name__ == '__main__':
    asyncio.run(main())