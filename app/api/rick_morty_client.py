"""Rick and Morty public API client."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://rickandmortyapi.com/api"


@dataclass
class RickMortyClient:
    base_url: str = BASE_URL
    timeout_s: float = 20.0
    max_retries: int = 3
    backoff_s: float = 0.5

    def __post_init__(self) -> None:
        self._session = requests.Session()
        retries = Retry(
            total=self.max_retries,
            connect=self.max_retries,
            read=self.max_retries,
            status=self.max_retries,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        adapter = HTTPAdapter(max_retries=retries)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    def _get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = self._session.get(url, params=params, timeout=self.timeout_s)
        resp.raise_for_status()
        return resp.json()

    def get_all_locations(self) -> List[Dict[str, Any]]:
        locations: List[Dict[str, Any]] = []
        url: Optional[str] = f"{self.base_url.rstrip('/')}/location"

        while url:
            # Small delay to be polite and reduce chance of being reset.
            time.sleep(self.backoff_s)
            data = self._get_json(url)
            locations.extend(data.get("results", []))
            url = (data.get("info") or {}).get("next")

        return locations

    def get_character_by_url(self, url: str) -> Dict[str, Any]:
        return self._get_json(url)
