"""Configuration for the web scraper, loaded from an external YAML file."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True)
class ScraperConfig:
    """Defines the settings and XPaths for a specific target site."""

    name: str
    base_url: str
    query_param: str
    container: str
    title: str
    url: str
    snippet: str
    headers: dict[str, str] | None = field(default=None)


def find_config_file() -> Path | None:
    """
    Find the configuration file by searching in standard locations.

    Search Order:
    1. Path specified in the SEARCH_SCRAPER_CONFIG environment variable.
    2. 'config.yaml' in the current working directory.
    """
    if config_path_str := os.getenv('SEARCH_SCRAPER_CONFIG'):
        config_path = Path(config_path_str)
        if config_path.is_file():
            return config_path

    config_path = Path.cwd() / 'config.yaml'
    if config_path.is_file():
        return config_path

    return None


def load_configs_from_yaml(path: str | Path | None) -> list[ScraperConfig]:
    """Load a list of ScraperConfig objects from a YAML file."""
    if not path:
        return []

    try:
        with Path(path).open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Warning: Configuration file not found at '{path}'.")
        return []
    except yaml.YAMLError as e:
        print(f"Warning: Error parsing YAML file at '{path}': {e}")
        return []

    configs_data: Iterable[dict] = data.get('scrapers', [])
    return [ScraperConfig(**config_data) for config_data in configs_data]


ALL_CONFIGS = load_configs_from_yaml(find_config_file())
