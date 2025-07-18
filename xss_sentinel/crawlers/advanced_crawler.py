import requests
import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from .wayback_crawler import WaybackCrawler, CommonCrawlService
from ..utils.http_utils import make_request, is_blocked


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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.discovered_urls = set()
        self.discovered_forms = []
        self.domain = urlparse(start_url).netloc
        
    def crawl(self):
        """Main crawling method"""
        print(f"Starting advanced crawl from {self.start_url}")
        
        # Start with the main URL
        self._crawl_url(self.start_url, depth=0)
        
        # Try alternative discovery methods if standard crawling fails
        if len(self.discovered_urls) < 10:
            print("Standard crawling found few URLs, trying alternative methods...")
            self._try_alternative_discovery()
        
        return {
            'urls': list(self.discovered_urls),
            'forms': self.discovered_forms
        }
    
    def _crawl_url(self, url, depth=0):
        """Crawl a single URL"""
        if depth > self.max_depth or len(self.discovered_urls) >= self.max_urls:
            return
        
        if url in self.discovered_urls:
            return
        
        try:
            print(f"Depth {depth}: Crawling {url}")
            
            # Use stealth request
            response = make_request(url, stealth_mode=True)
            
            if not response or response.status_code != 200:
                print(f"Failed to access {url}: {response.status_code if response else 'No response'}")
                return
            
            # Check if blocked
            if is_blocked(response):
                print(f"Access blocked for {url}")
                return
            
            self.discovered_urls.add(url)
            print(f"Depth {depth}: Discovered {len(self.discovered_urls)} URLs so far")
            
            # Extract links
            links = self._extract_links(response.text, url)
            
            # Process forms
            forms = self._extract_forms(response.text, url)
            self.discovered_forms.extend(forms)
            
            # Follow links
            for link in links:
                if len(self.discovered_urls) >= self.max_urls:
                    break
                self._crawl_url(link, depth + 1)
                time.sleep(self.delay)
                
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    
    def _extract_links(self, html, base_url):
        """Extract links from HTML"""
        links = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                
                # Filter URLs
                if self._should_follow_url(full_url):
                    links.append(full_url)
                    
        except Exception as e:
            print(f"Error extracting links from {base_url}: {e}")
        
        return links
    
    def _extract_forms(self, html, base_url):
        """Extract forms from HTML"""
        forms = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for form in soup.find_all('form'):
                action = form.get('action', '')
                method = form.get('method', 'get').lower()
                
                if action:
                    form_url = urljoin(base_url, action)
                else:
                    form_url = base_url
                
                # Extract form fields
                fields = []
                for input_tag in form.find_all(['input', 'textarea']):
                    field_type = input_tag.get('type', 'text')
                    field_name = input_tag.get('name', '')
                    
                    if field_name and field_type in ['text', 'textarea', 'search', 'url', 'email']:
                        fields.append({
                            'name': field_name,
                            'type': field_type
                        })
                
                if fields:
                    forms.append({
                        'url': form_url,
                        'method': method,
                        'fields': fields
                    })
                    
        except Exception as e:
            print(f"Error extracting forms from {base_url}: {e}")
        
        return forms
    
    def _should_follow_url(self, url):
        """Determine if a URL should be followed"""
        try:
            parsed = urlparse(url)
            
            # Check domain
            if not self.include_subdomains:
                if parsed.netloc != self.domain:
                    return False
            else:
                if not (parsed.netloc == self.domain or parsed.netloc.endswith('.' + self.domain)):
                    return False
            
            # Skip certain file types
            skip_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar', '.exe', '.jpg', '.jpeg', '.png', '.gif']
            if any(parsed.path.lower().endswith(ext) for ext in skip_extensions):
                return False
            
            # Skip certain paths
            skip_paths = ['/admin', '/login', '/logout', '/api/', '/ajax/']
            if any(skip_path in parsed.path.lower() for skip_path in skip_paths):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _try_alternative_discovery(self):
        """Try alternative URL discovery methods"""
        try:
            # Try Wayback Machine
            print("Trying Wayback Machine...")
            wayback = WaybackCrawler()
            wayback_urls = wayback.get_urls(self.domain, limit=100)
            
            for url in wayback_urls:
                if len(self.discovered_urls) >= self.max_urls:
                    break
                if self._should_follow_url(url):
                    self.discovered_urls.add(url)
            
            print(f"Found {len(wayback_urls)} URLs from Wayback Machine")
            
        except Exception as e:
            print(f"Error with alternative discovery: {e}")
