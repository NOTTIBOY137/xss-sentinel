import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from ..utils.http_utils import make_request

class Crawler:
    def __init__(self, start_url, max_depth=3, max_urls=100):
        self.start_url = start_url
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.visited_urls = set()
        self.queue = [(start_url, 0)]  # (url, depth)
        self.base_domain = urlparse(start_url).netloc
    
    def crawl(self):
        """
        Crawl the website starting from the start_url up to max_depth
        and return a list of discovered URLs
        """
        print(f"Starting crawl from {self.start_url} with max depth {self.max_depth}")
        
        while self.queue and len(self.visited_urls) < self.max_urls:
            url, depth = self.queue.pop(0)
            
            if url in self.visited_urls:
                continue
                
            if depth > self.max_depth:
                continue
            
            try:
                print(f"Crawling: {url} (depth: {depth})")
                response = make_request(url)
                if not response:
                    continue
                
                self.visited_urls.add(url)
                
                # Don't process non-HTML responses
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type.lower():
                    continue
                
                # Parse the page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract links
                self._extract_links(soup, url, depth)
                
            except Exception as e:
                print(f"Error crawling {url}: {e}")
        
        return list(self.visited_urls)
    
    def _extract_links(self, soup, base_url, current_depth):
        """Extract links from the page and add them to the queue"""
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip empty links, anchors, and javascript
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Resolve relative URLs
            absolute_url = urljoin(base_url, href)
            
            # Skip external domains and non-HTTP links
            if not self._is_same_domain(absolute_url) or not absolute_url.startswith(('http://', 'https://')):
                continue
            
            # Normalize URL (remove fragments)
            normalized_url = self._normalize_url(absolute_url)
            
            # Add to queue if not visited
            if normalized_url not in self.visited_urls:
                self.queue.append((normalized_url, current_depth + 1))
    
    def _is_same_domain(self, url):
        """Check if URL belongs to the same domain as the start URL"""
        return urlparse(url).netloc == self.base_domain
    
    def _normalize_url(self, url):
        """Normalize URL by removing fragments"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}{('?' + parsed.query) if parsed.query else ''}"
