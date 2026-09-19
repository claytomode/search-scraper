"""Configurable, asynchronous client for scraping search engines."""

from types import TracebackType
from typing import TYPE_CHECKING, Any, TypeVar

import httpx
from lxml import html
from pydantic import ValidationError

from scraper.config import ScraperConfig
from scraper.exceptions import NetworkError, ParsingError
from scraper.models import SearchResult

if TYPE_CHECKING:
    from lxml.etree import _Element

ClientT = TypeVar('ClientT', httpx.Client, httpx.AsyncClient)

# HTTP/2 to html.duckduckgo.com / lite.duckduckgo.com often stalls forever.
_DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


def _client_kwargs(config: ScraperConfig) -> dict[str, Any]:
    return {
        'follow_redirects': True,
        'http2': False,
        'timeout': _DEFAULT_TIMEOUT,
        'headers': config.headers,
    }


def _node_text(nodes: list[Any]) -> str:
    parts: list[str] = []
    for node in nodes:
        if hasattr(node, 'text_content'):
            parts.append(node.text_content())
        else:
            parts.append(str(node))
    return ''.join(parts).strip().replace('\n', ' ')


def _wrap_http_error(exc: httpx.HTTPError) -> NetworkError:
    url = getattr(getattr(exc, 'request', None), 'url', None)
    if isinstance(exc, httpx.HTTPStatusError):
        return NetworkError(f'HTTP {exc.response.status_code} from {url!r}.')
    return NetworkError(f'An error occurred while requesting {url!r}.')


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

            if not (title_list and url_list):
                continue

            title = _node_text(title_list)
            url = _node_text(url_list)
            snippet = _node_text(snippet_nodes)

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
            self._client = httpx.Client(**_client_kwargs(self.config))
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
        except httpx.HTTPError as e:
            raise _wrap_http_error(e) from e

        return self._parse_html(response.text, max_results=max_results)


class AsyncScraper(BaseScraper[httpx.AsyncClient]):
    """An asynchronous, config-driven scraper for search engine results."""

    async def __aenter__(self) -> 'AsyncScraper':
        """Enter the async context, creating a client if needed."""
        if self._owns_client:
            self._client = httpx.AsyncClient(**_client_kwargs(self.config))
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
        except httpx.HTTPError as e:
            raise _wrap_http_error(e) from e

        return self._parse_html(response.text, max_results=max_results)
