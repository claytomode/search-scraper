"""Configuration for the web scraper."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScraperConfig:
    """
    Defines the XPaths and settings for a specific target site.

    Attributes:
        base_url: The base URL of the site to be scraped.
        container: An XPath to select each result item's container element.
        title: An XPath relative to the container for the result's title.
        url: An XPath relative to the container for the result's URL.
        snippet: An XPath relative to the container for the result's snippet.
        query_param: The name of the URL parameter for the search query.

    """

    base_url: str
    container: str
    title: str
    url: str
    snippet: str
    query_param: str


LITE_DUCKDUCKGO_CONFIG = ScraperConfig(
    base_url='https://lite.duckduckgo.com/lite/',
    container="//a[@class='result-link']/ancestor::tr",
    title=".//a[@class='result-link']/text()",
    url=".//a[@class='result-link']/@href",
    snippet="following-sibling::tr[1]/td[@class='result-snippet']",
    query_param='q',
)

HTML_DUCKDUCKGO_CONFIG = ScraperConfig(
    base_url='https://html.duckduckgo.com/html/',
    container="//div[contains(@class, 'web-result')]",
    title=".//a[contains(@class, 'result__a')]/text()",
    url=".//a[contains(@class, 'result__a')]/@href",
    snippet=".//a[contains(@class, 'result__snippet')]",
    query_param='q',
)

STARTPAGE_CONFIG = ScraperConfig(
    base_url='https://www.startpage.com/sp/search',
    container="//div[contains(@class, 'result')]",
    title=".//h2[contains(@class, 'wgl-title')]/text()",
    url=".//a[contains(@class, 'result-title')]/@href",
    snippet=".//p[contains(@class, 'description')]",
    query_param='query',
)

BRAVE_SEARCH_CONFIG = ScraperConfig(
    base_url='https://search.brave.com/search',
    container="//div[contains(@class, 'snippet ')]",
    title=".//div[contains(@class, 'title')]/text()",
    url=".//a[contains(@class, 'heading-serpresult')]/@href",
    snippet=".//div[contains(@class, 'snippet-description')]",
    query_param='q',
)

