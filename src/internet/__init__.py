"""Internet module - Web search and content extraction"""

from .web_search import WebSearch
from .web_scraper import WebScraper
from .free_llm_fallback import FreeLLMFallback

__all__ = ['WebSearch', 'WebScraper', 'FreeLLMFallback']
