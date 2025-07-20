"""Custom exceptions for the scraper module."""


class ScraperError(Exception):
    """Base exception for the scraper."""


class NetworkError(ScraperError):
    """Raised when a network-related error occurs."""


class ParsingError(ScraperError):
    """Raised when an error occurs during HTML parsing."""