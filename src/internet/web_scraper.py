"""Web Scraper - Extract and summarize web content"""

import logging
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScrapedContent:
    """Represents scraped web content"""
    url: str
    title: str
    text: str
    html: str
    success: bool
    error: Optional[str] = None


class WebScraper:
    """
    Web content scraper and extractor.
    Extracts text, structure, and relevant information from web pages.
    """

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.scrape_history = []
        logger.info("WebScraper initialized")

    async def scrape_url(self, url: str, extract_type: str = "text") -> ScrapedContent:
        """
        Scrape content from a URL.
        
        Args:
            url: URL to scrape
            extract_type: Type of extraction ('text', 'links', 'tables', 'all')
        
        Returns:
            ScrapedContent object with extracted information
        """
        logger.info(f"Scraping {url}")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else "No title"
            
            # Extract text
            text = self._extract_text(soup, extract_type)
            
            scraped = ScrapedContent(
                url=url,
                title=title,
                text=text,
                html=response.text,
                success=True
            )
            
            self.scrape_history.append({
                "url": url,
                "title": title,
                "timestamp": str(__import__('datetime').datetime.now())
            })
            
            return scraped
        
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {str(e)}")
            return ScrapedContent(
                url=url,
                title="",
                text="",
                html="",
                success=False,
                error=str(e)
            )

    def _extract_text(self, soup: BeautifulSoup, extract_type: str) -> str:
        """
        Extract text from BeautifulSoup object.
        """
        if extract_type == "text":
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return '\n'.join(chunk for chunk in chunks if chunk)
        
        elif extract_type == "links":
            links = []
            for link in soup.find_all('a', href=True):
                links.append({
                    "text": link.get_text(strip=True),
                    "url": link['href']
                })
            return str(links[:20])  # Return first 20 links
        
        elif extract_type == "tables":
            tables = []
            for table in soup.find_all('table'):
                rows = []
                for tr in table.find_all('tr'):
                    cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                    rows.append(cells)
                tables.append(rows)
            return str(tables)[:2000]  # Truncate to 2000 chars
        
        else:  # 'all'
            text = self._extract_text(soup, "text")
            links = self._extract_text(soup, "links")
            return f"Text:\n{text}\n\nLinks:\n{links}"

    async def summarize_content(self, content: str, max_length: int = 500) -> str:
        """
        Summarize scraped content (basic extractive summary).
        Phase 2: Use LLM for abstractive summarization.
        """
        sentences = content.split('.')[:10]  # Get first 10 sentences
        summary = '.'.join(sentences)[:max_length]
        return summary

    def get_scrape_history(self, limit: int = 50) -> list:
        """Get scraping history"""
        return self.scrape_history[-limit:]
