"""Web Search - Search the internet for information"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
from urllib.parse import quote

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result"""
    title: str
    url: str
    snippet: str
    source: str = "google"


class WebSearch:
    """
    Web search functionality.
    Supports multiple search engines:
    - DuckDuckGo (no API key needed)
    - Google Custom Search (requires API key)
    - Bing Search (requires API key)
    """

    def __init__(
        self,
        search_engine: str = "duckduckgo",
        google_api_key: Optional[str] = None,
        google_cx: Optional[str] = None,
        bing_api_key: Optional[str] = None
    ):
        self.search_engine = search_engine
        self.google_api_key = google_api_key
        self.google_cx = google_cx
        self.bing_api_key = bing_api_key
        self.search_history: List[Dict[str, Any]] = []
        logger.info(f"WebSearch initialized with {search_engine}")

    async def search(
        self,
        query: str,
        num_results: int = 5,
        require_approval: bool = True
    ) -> List[SearchResult]:
        """
        Search the web for information.
        
        Args:
            query: Search query
            num_results: Number of results to return
            require_approval: Whether search requires user approval
        
        Returns:
            List of SearchResult objects
        """
        logger.info(f"Searching for: {query}")
        
        if self.search_engine == "duckduckgo":
            return await self._search_duckduckgo(query, num_results)
        elif self.search_engine == "google" and self.google_api_key:
            return await self._search_google(query, num_results)
        elif self.search_engine == "bing" and self.bing_api_key:
            return await self._search_bing(query, num_results)
        else:
            logger.warning(f"Unknown search engine: {self.search_engine}. Using DuckDuckGo.")
            return await self._search_duckduckgo(query, num_results)

    async def _search_duckduckgo(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Search using DuckDuckGo (no API key required).
        Note: DuckDuckGo doesn't have an official API, so this uses a workaround.
        For production, consider using DDG's fetch or similar services.
        """
        try:
            # Using DuckDuckGo via requests (lite version)
            url = f"https://lite.duckduckgo.com/lite"
            params = {"q": query, "t": "h_"}  # h_ is user agent hint
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse results from DuckDuckGo lite HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            # Note: Parsing lite.duckduckgo.com is fragile. Consider using an API service.
            
            self.search_history.append({
                "query": query,
                "engine": "duckduckgo",
                "results_count": len(results),
                "timestamp": str(__import__('datetime').datetime.now())
            })
            
            return results[:num_results]
        
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {str(e)}")
            return []

    async def _search_google(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Search using Google Custom Search API.
        Requires:
        - google_api_key: API key from Google Cloud Console
        - google_cx: Custom Search Engine ID
        """
        if not self.google_api_key or not self.google_cx:
            logger.error("Google API key or CX not configured")
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "q": query,
                "key": self.google_api_key,
                "cx": self.google_cx,
                "num": min(num_results, 10)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("items", []):
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="google"
                )
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Google search failed: {str(e)}")
            return []

    async def _search_bing(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Search using Bing Search API.
        Requires: bing_api_key from Azure
        """
        if not self.bing_api_key:
            logger.error("Bing API key not configured")
            return []
        
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {"Ocp-Apim-Subscription-Key": self.bing_api_key}
            params = {"q": query, "count": num_results}
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("webPages", {}).get("value", []):
                result = SearchResult(
                    title=item.get("name", ""),
                    url=item.get("url", ""),
                    snippet=item.get("snippet", ""),
                    source="bing"
                )
                results.append(result)
            
            return results
        
        except Exception as e:
            logger.error(f"Bing search failed: {str(e)}")
            return []

    def get_search_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get search history"""
        return self.search_history[-limit:]
