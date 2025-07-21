"""Fixtures for testing the scraper."""
import pytest

from scraper.config import ScraperConfig


@pytest.fixture
def sample_config() -> ScraperConfig:
    """Provide a sample ScraperConfig for testing."""
    return ScraperConfig(
        name='test_engine',
        base_url='https://test.engine.com',
        query_param='q',
        container="//div[@class='result']",
        title='.//h2/a/text()',
        url='.//h2/a/@href',
        snippet=".//p[@class='snippet']",
        headers={'User-Agent': 'Test-Agent/1.0'},
    )


@pytest.fixture
def sample_html_content() -> bytes:
    """Provide a sample HTML string that matches the sample_config."""
    return b"""
    <html>
        <body>
            <div class="results">
                <div class="result">
                    <h2><a href="https://test.engine.com/result1">Result 1</a></h2>
                    <p class="snippet">This is the first snippet.</p>
                </div>
                <div class="result">
                    <h2><a href="https://test.engine.com/result2">Result 2</a></h2>
                    <p class="snippet">This is the second snippet.</p>
                </div>
                <div class="result">
                    <h2><a href="https://test.engine.com/result3">Result 3</a></h2>
                </div>
            </div>
        </body>
    </html>
    """
