"""Test scraper client."""

import httpx
import pytest
from pydantic import HttpUrl
from pytest_httpx import HTTPXMock

from scraper.client import AsyncScraper, SyncScraper
from scraper.config import ScraperConfig
from scraper.exceptions import NetworkError, ParsingError
from scraper.models import SearchResult


@pytest.mark.asyncio
async def test_async_scraper_success(
    httpx_mock: HTTPXMock, sample_config: ScraperConfig, sample_html_content: bytes
) -> None:
    """Test successful async search and parsing."""
    httpx_mock.add_response(url=f'{sample_config.base_url}?q=test', content=sample_html_content)
    max_results = 2
    async with AsyncScraper(config=sample_config) as scraper:
        results = await scraper.search('test', max_results=max_results)
    assert len(results) == max_results
    assert results[0] == SearchResult(
        title='Result 1',
        url=HttpUrl(url='https://test.engine.com/result1'),
        snippet='This is the first snippet.',
    )
    assert results[1].title == 'Result 2'


@pytest.mark.asyncio
async def test_async_scraper_network_error(
    httpx_mock: HTTPXMock, sample_config: ScraperConfig
) -> None:
    """Test that NetworkError is raised on httpx.RequestError."""
    httpx_mock.add_exception(httpx.ConnectError('Connection failed'))

    with pytest.raises(NetworkError, match='An error occurred while requesting'):
        async with AsyncScraper(config=sample_config) as scraper:
            await scraper.search('test')


@pytest.mark.asyncio
async def test_async_scraper_parsing_error(
    httpx_mock: HTTPXMock,
    sample_config: ScraperConfig,
) -> None:
    """Test that ParsingError is raised for invalid search result data."""
    invalid_html = b"""
    <div class="result">
        <h2><a href="file://invalid.url/file">Invalid URL</a></h2>
        <p class="snippet">This will fail validation.</p>
    </div>
    """
    httpx_mock.add_response(url=f'{sample_config.base_url}?q=test', content=invalid_html)

    with pytest.raises(ParsingError, match='Failed to create SearchResult'):
        async with AsyncScraper(config=sample_config) as scraper:
            await scraper.search('test')


def test_sync_scraper_success(
    httpx_mock: HTTPXMock, sample_config: ScraperConfig, sample_html_content: bytes
) -> None:
    """Test successful synchronous search and parsing."""
    httpx_mock.add_response(url=f'{sample_config.base_url}?q=test', content=sample_html_content)

    max_results = 1
    with SyncScraper(config=sample_config) as scraper:
        results = scraper.search('test', max_results=max_results)

    assert len(results) == max_results
    assert results[0].title == 'Result 1'


def test_sync_scraper_network_error(httpx_mock: HTTPXMock, sample_config: ScraperConfig) -> None:
    """Test that NetworkError is raised on httpx.RequestError for the sync client."""
    httpx_mock.add_exception(httpx.ConnectError('Connection failed'))

    with pytest.raises(NetworkError), SyncScraper(config=sample_config) as scraper:
        scraper.search('test')


def test_sync_scraper_parsing_error(
    httpx_mock: HTTPXMock,
    sample_config: ScraperConfig,
) -> None:
    """Test that ParsingError is raised for invalid search result data for the sync client."""
    invalid_html = b"""
    <div class="result">
        <h2><a href="file://invalid.url/file">Invalid URL</a></h2>
        <p class="snippet">This will fail validation.</p>
    </div>
    """
    httpx_mock.add_response(url=f'{sample_config.base_url}?q=test', content=invalid_html)

    with pytest.raises(ParsingError), SyncScraper(config=sample_config) as scraper:
        scraper.search('test')
