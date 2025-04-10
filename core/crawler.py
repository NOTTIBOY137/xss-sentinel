import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import random
from ..utils.http_utils import make_request

class Crawler:
    def __init__(self, start_url, max_depth=3, max_urls=100, include_subdomains=False):
        self.start_url = start_url
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.visited_urls = set()
        self.queue = [(start_url, 0)]  # (url, depth)
        self.base_domain = urlparse(start_url).netloc
        self.include_subdomains = include_subdomains
    
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
                content_type = response.headers.get('Content-Type', '').lower()
                valid_types = ['text/html', 'application/xhtml', 'application/xhtml+xml']
                is_html = any(html_type in content_type for html_type in valid_types)
                if not is_html and content_type != '':  # Also accept empty content type
                    print(f"Skipping non-HTML content: {url} (type: {content_type})")
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
            
            # Check if URL belongs to the same domain or subdomain if allowed
            if not self._is_same_domain(absolute_url):
                continue
                
            # Skip non-HTTP links
            if not absolute_url.startswith(('http://', 'https://')):
                continue
            
            # Normalize URL (remove fragments)
            normalized_url = self._normalize_url(absolute_url)
            
            # Add to queue if not visited
            if normalized_url not in self.visited_urls:
                self.queue.append((normalized_url, current_depth + 1))
    
    def _is_same_domain(self, url):
        """Check if URL belongs to the same domain or subdomain of the base domain"""
        parsed_url = urlparse(url)
        url_domain = parsed_url.netloc
        
        # Accept exact matches
        if url_domain == self.base_domain:
            return True
        
        # Handle www subdomain variations
        if url_domain == f"www.{self.base_domain}" or self.base_domain == f"www.{url_domain}":
            return True
        
        # Accept subdomains if allowed
        if self.include_subdomains:
            main_domain_parts = self.base_domain.split('.')
            if len(main_domain_parts) >= 2:
                organization_domain = '.'.join(main_domain_parts[-2:])  # e.g., example.com from www.example.com
                if url_domain.endswith(organization_domain):
                    return True
        
        return False
    
    def _normalize_url(self, url):
        """Normalize URL by removing fragments"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}{('?' + parsed.query) if parsed.query else ''}"
