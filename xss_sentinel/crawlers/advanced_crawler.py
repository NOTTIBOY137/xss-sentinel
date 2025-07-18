import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from .wayback_crawler import WaybackCrawler, CommonCrawlService


class AdvancedCrawler:
    """Advanced web crawler with multiple discovery methods"""
    
    def __init__(self, start_url, max_depth=2, max_urls=10000, 
                 include_subdomains=False, respect_robots=False, delay=0.5):
        self.start_url = start_url
        self.max_depth = max_depth
        self.max_urls = max_urls
        self.include_subdomains = include_subdomains
        self.respect_robots = respect_robots
        self.delay = delay
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'XSS-Sentinel/1.0 (Advanced Crawler)'
        })
        
        self.discovered_urls = set()
        self.discovered_forms = []
        self.domain = urlparse(start_url).netloc
        
    def crawl(self):
        """Main crawling method"""
        print(f"Starting advanced crawl from {self.start_url}")
        
        # Start with the initial URL
        self.discovered_urls.add(self.start_url)
        
        # Crawl in breadth-first manner
        current_depth = 0
        urls_to_crawl = [self.start_url]
        
        while current_depth < self.max_depth and urls_to_crawl:
            next_level_urls = []
            
            for url in urls_to_crawl:
                if len(self.discovered_urls) >= self.max_urls:
                    break
                    
                try:
                    self._crawl_url(url)
                    next_level_urls.extend(self._extract_links(url))
                    time.sleep(self.delay)
                    
                except Exception as e:
                    print(f"Error crawling {url}: {e}")
            
            urls_to_crawl = next_level_urls
            current_depth += 1
            
            print(f"Depth {current_depth}: Discovered {len(self.discovered_urls)} URLs so far")
        
        return {
            'urls': list(self.discovered_urls),
            'forms': self.discovered_forms
        }
    
    def _crawl_url(self, url):
        """Crawl a single URL and extract forms"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract forms
            forms = soup.find_all('form')
            for form in forms:
                form_data = self._extract_form_data(form, url)
                if form_data:
                    self.discovered_forms.append(form_data)
                    
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    
    def _extract_links(self, url):
        """Extract links from a page"""
        new_urls = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                absolute_url = urljoin(url, href)
                
                # Validate URL
                if self._is_valid_url(absolute_url):
                    if absolute_url not in self.discovered_urls:
                        self.discovered_urls.add(absolute_url)
                        new_urls.append(absolute_url)
                        
        except Exception as e:
            print(f"Error extracting links from {url}: {e}")
        
        return new_urls
    
    def _extract_form_data(self, form, page_url):
        """Extract form data for XSS testing"""
        try:
            action = form.get('action', '')
            method = form.get('method', 'get').lower()
            
            if action:
                form_url = urljoin(page_url, action)
            else:
                form_url = page_url
            
            inputs = []
            for input_tag in form.find_all(['input', 'textarea']):
                input_type = input_tag.get('type', 'text')
                input_name = input_tag.get('name', '')
                
                if input_name and input_type in ['text', 'textarea', 'search', 'url', 'email']:
                    inputs.append({
                        'name': input_name,
                        'type': input_type,
                        'required': input_tag.get('required') is not None
                    })
            
            if inputs:
                return {
                    'url': form_url,
                    'method': method,
                    'inputs': inputs,
                    'page_url': page_url
                }
                
        except Exception as e:
            print(f"Error extracting form data: {e}")
        
        return None
    
    def _is_valid_url(self, url):
        """Check if URL is valid for crawling"""
        try:
            parsed = urlparse(url)
            
            # Must have a scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Check if it's the same domain (unless subdomains are allowed)
            if not self.include_subdomains:
                if parsed.netloc != self.domain and not parsed.netloc.endswith('.' + self.domain):
                    return False
            
            # Skip certain file types
            skip_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.exe']
            if any(url.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            # Skip certain URL patterns
            skip_patterns = ['mailto:', 'tel:', 'javascript:', '#']
            if any(pattern in url.lower() for pattern in skip_patterns):
                return False
            
            return True
            
        except Exception:
            return False 