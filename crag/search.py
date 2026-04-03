"""Brave Search API integration."""

import logging
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
logger = logging.getLogger(__name__)
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("BRAVE_API_KEY")


class BraveSearchClient:
    """Client for Brave Search API."""

    BASE_URL = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }

    def search(self, query: str, count: int = 5) -> List[Dict]:
        """Execute web search."""
        try:
            params = {"q": query, "count": count}
            response = requests.get(
                self.BASE_URL,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("url", ""),
                    "snippet": item.get("description", "")
                })
            return results
        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            return []

    @staticmethod
    def fetch_page_content(url: str, max_chars: int = 3000) -> str:
        """Fetch and extract text from a web page."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            text = soup.get_text()
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return " ".join(lines)[:max_chars]
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return ""


def get_brave_search_client(api_key: str) -> BraveSearchClient:
    """Factory function for Brave search client."""
    return BraveSearchClient(api_key=api_key)


def brave_search_results(query: str, api_key: str, count: int = 5) -> List[Dict]:
    """Convenience function for search."""
    client = get_brave_search_client(api_key)
    return client.search(query, count)
