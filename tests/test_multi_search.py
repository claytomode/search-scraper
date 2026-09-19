"""Failover across engines."""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from scraper.config import ScraperConfig
from scraper.exceptions import ScraperError
from scraper.multi_search import search_async, search_sync


def _second_config(sample_config: ScraperConfig) -> ScraperConfig:
    return ScraperConfig(
        name='second_engine',
        base_url='https://second.engine.com',
        query_param='q',
        container=sample_config.container,
        title=sample_config.title,
        url=sample_config.url,
        snippet=sample_config.snippet,
        headers=sample_config.headers,
    )


@pytest.mark.asyncio
async def test_async_failover_skips_empty_parse(
    httpx_mock: HTTPXMock,
    sample_config: ScraperConfig,
    sample_html_content: bytes,
) -> None:
    """A 200 with no matching results is a miss — try the next engine."""
    second = _second_config(sample_config)
    httpx_mock.add_response(
        url=f'{sample_config.base_url}?q=test',
        content=b'<html><body><p>Just a moment...</p></body></html>',
    )
    httpx_mock.add_response(url=f'{second.base_url}?q=test', content=sample_html_content)

    results = await search_async('test', configs=[sample_config, second], max_results=2)
    assert results is not None
    assert results[0].title == 'Result 1'


@pytest.mark.asyncio
async def test_async_failover_skips_http_error(
    httpx_mock: HTTPXMock,
    sample_config: ScraperConfig,
    sample_html_content: bytes,
) -> None:
    second = _second_config(sample_config)
    httpx_mock.add_response(url=f'{sample_config.base_url}?q=test', status_code=403)
    httpx_mock.add_response(url=f'{second.base_url}?q=test', content=sample_html_content)

    results = await search_async('test', configs=[sample_config, second], max_results=1)
    assert results is not None
    assert results[0].title == 'Result 1'


def test_sync_all_errors_raise(httpx_mock: HTTPXMock, sample_config: ScraperConfig) -> None:
    httpx_mock.add_exception(httpx.ConnectError('nope'))
    with pytest.raises(ScraperError, match='Failed to scrape from all configs'):
        search_sync('test', configs=[sample_config])
