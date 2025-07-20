"""Data models for DuckDuckGo search results."""

from pydantic import BaseModel, Field, HttpUrl


class SearchResult(BaseModel):
    """
    Represents a single search result item.

    Attributes:
        title: The title of the search result.
        url: The URL of the search result.
        snippet: A brief description or snippet from the result page.

    """

    title: str = Field(..., description='The title of the search result.')
    url: HttpUrl = Field(..., description='The URL of the search result.')
    snippet: str = Field(..., description='A brief description of the result.')