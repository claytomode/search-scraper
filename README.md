# Search Scraper
Trivially scrape search results from static HTML search engines.
> [!Warning]
> This tool is intended for **educational and research purposes only**. Web scraping search engines may violate their Terms of Service. Please review the ToS of any search engine you plan on scraping.

-----

## Usage & Customization

This scraper is driven by a config dataclass. You can use the premade `config.yaml` or define your own based on the config dataclass. This allows you to easily add support for a new search engine or fix an existing one if its HTML structure changes.

The main idea is to define **XPath selectors** for the data you want to extract and pass them to the scraper client.
LLMs are actually pretty good at this! You can send in the HTML webpage of an example search along with the config dataclass and ask it to create one for your designated search engine.
