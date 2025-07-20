"""Configurable, asynchronous client for scraping search engines."""

from types import TracebackType
from typing import TYPE_CHECKING, TypeVar

import httpx
from lxml import html
from pydantic import ValidationError

from scraper.config import ScraperConfig
from scraper.exceptions import NetworkError, ParsingError
from scraper.models import SearchResult

if TYPE_CHECKING:
    from lxml.etree import _Element

ClientT = TypeVar('ClientT', httpx.Client, httpx.AsyncClient)


class BaseScraper[ClientT: (httpx.Client, httpx.AsyncClient)]:
    """
    A generic base class for sync and async scrapers.

    This class contains the shared logic for initialization and HTML parsing,
    while leaving network operations to its subclasses.
    """

    def __init__(self, config: ScraperConfig, client: ClientT | None = None) -> None:
        """
        Initialize the scraper with a specific configuration.

        Args:
            config: The scraper configuration with URLs and XPaths.
            client: An optional httpx.Client or httpx.AsyncClient instance.

        """
        self.config = config
        self._client: ClientT | None = client
        self._owns_client = client is None

    def _parse_html(self, content: str, max_results: int | None = None) -> list[SearchResult]:
        """
        Parse the HTML content using the instance's configuration.

        Args:
            content: The HTML page content as a string.
            max_results: The maximum number of results to parse.

        Returns:
            A list of SearchResult objects.

        Raises:
            ParsingError: If a SearchResult fails validation.

        """
        tree = html.fromstring(content)
        tree.make_links_absolute(self.config.base_url)
        results: list[SearchResult] = []
        containers: list[_Element] = tree.xpath(self.config.container)

        for container in containers:
            if max_results is not None and len(results) >= max_results:
                break

            title_list = container.xpath(self.config.title)
            url_list = container.xpath(self.config.url)
            snippet_nodes = container.xpath(self.config.snippet)

            if not (title_list and url_list and snippet_nodes):
                continue

            title = ''.join(title_list).strip()
            url = ''.join(url_list).strip()
            snippet = (
                ''.join(snip.text_content() for snip in snippet_nodes).strip().replace('\n', ' ')
            )

            try:
                result = SearchResult(title=title, url=url, snippet=snippet)
                results.append(result)
            except ValidationError as e:
                msg = f'Failed to create SearchResult for title "{title}": {e}'
                raise ParsingError(msg) from e
        return results


class SyncScraper(BaseScraper[httpx.Client]):
    """A synchronous, config-driven scraper for search engine results."""

    def __enter__(self) -> 'SyncScraper':
        """Enter the context, creating a client if needed."""
        if self._owns_client:
            self._client = httpx.Client(
                follow_redirects=True, http2=True, headers=self.config.headers
            )
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context, closing the client if owned."""
        if self._owns_client and self._client:
            self._client.close()

    def search(self, query: str, max_results: int | None = None) -> list[SearchResult]:
        """Perform a search and return the parsed results."""
        if not self._client:
            msg = 'Client not initialized. Use as a context manager.'
            raise RuntimeError(msg)
        try:
            response = self._client.get(
                self.config.base_url,
                params={self.config.query_param: query},
            )
            response.raise_for_status()
        except httpx.RequestError as e:
            msg = f'An error occurred while requesting {e.request.url!r}.'
            raise NetworkError(msg) from e

        return self._parse_html(response.text, max_results=max_results)


class AsyncScraper(BaseScraper[httpx.AsyncClient]):
    """An asynchronous, config-driven scraper for search engine results."""

    async def __aenter__(self) -> 'AsyncScraper':
        """Enter the async context, creating a client if needed."""
        if self._owns_client:
            self._client = httpx.AsyncClient(
                follow_redirects=True, http2=True, headers=self.config.headers
            )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the async context, closing the client if owned."""
        if self._owns_client and self._client:
            await self._client.aclose()

    async def search(self, query: str, max_results: int | None = None) -> list[SearchResult]:
        """Perform an asynchronous search and return the parsed results."""
        if not self._client:
            msg = 'Client not initialized. Use as a context manager.'
            raise RuntimeError(msg)
        try:
            response = await self._client.get(
                self.config.base_url,
                params={self.config.query_param: query},
            )
            response.raise_for_status()
        except httpx.RequestError as e:
            msg = f'An error occurred while requesting {e.request.url!r}.'
            raise NetworkError(msg) from e

        return self._parse_html(response.text, max_results=max_results)