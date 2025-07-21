# Search Scraper

> [!Warning]
> This tool is intended for **educational and research purposes only**. Web scraping search engines may violate their Terms of Service. Please review the ToS of any search engine you plan on scraping.

-----

## Usage & Customization

This scraper is driven by a config dataclass. You can use the premade `config.yaml` or define your own based on the config dataclass. This allows you to easily add support for a new search engine or fix an existing one if its HTML structure changes.

The main idea is to define **XPath selectors** for the data you want to extract and pass them to the scraper client.
LLMs are actually pretty good at this! You can send in the HTML webpage of an example search along with the config dataclass and ask it to create one for your designated search engine.

### Example: Creating a Custom Scraper

Here’s how you can define a configuration for a new search engine and use it.

```python
import asyncio
from scraper.client import AsyncScraper
from scraper.config import ScraperConfig # Import the dataclass structure
from scraper.exceptions import ScraperError

# 1. Define your custom configuration using the ScraperConfig structure.
# You would get these XPaths by inspecting the search engine's HTML source.
MY_SEARCH_ENGINE_CONFIG = ScraperConfig(
    base_url='https://my-search-engine.com/search',
    query_param='text',
    container="//div[@class='result-item']",
    title=".//h3/a/text()",
    url=".//h3/a/@href",
    snippet=".//p[@class='description']",
)

async def main() -> None:
    query = 'hello world in python'
    
    # 2. Use your custom config with the scraper client.
    try:
        async with AsyncScraper(config=MY_SEARCH_ENGINE_CONFIG) as scraper:
            # The client will use your config to make the request and parse results.
            results = await scraper.search(query, max_results=5)
            
            for result in results:
                print(f"Title: {result.title}\nURL: {result.url}\n")

    except ScraperError as e:
        print(f'An error occurred: {e}')

if __name__ == '__main__':
    asyncio.run(main())
```
