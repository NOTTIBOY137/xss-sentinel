import requests
import time
from urllib.parse import urljoin, urlparse
import json


class WaybackCrawler:
    """Crawler for discovering URLs from Wayback Machine"""
    
    def __init__(self, delay=1.0):
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'XSS-Sentinel/1.0 (Wayback Crawler)'
        })
    
    def get_wayback_urls(self, domain, limit=1000):
        """Get URLs for a domain from Wayback Machine"""
        urls = set()
        
        try:
            # Wayback Machine CDX API
            cdx_url = f"http://web.archive.org/cdx/search/cdx"
            params = {
                'url': f"*.{domain}/*",
                'output': 'json',
                'fl': 'original',
                'collapse': 'urlkey',
                'limit': limit
            }
            
            response = self.session.get(cdx_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if len(data) > 1:  # Skip header row
                for row in data[1:]:  # Skip header
                    if len(row) > 0:
                        url = row[0]
                        if url.startswith(('http://', 'https://')):
                            urls.add(url)
            
            time.sleep(self.delay)
            
        except Exception as e:
            print(f"Warning: Error fetching from Wayback Machine: {e}")
        
        return list(urls)


class CommonCrawlService:
    """Service for discovering URLs from CommonCrawl"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'XSS-Sentinel/1.0 (CommonCrawl Service)'
        })
    
    def get_urls_for_domain(self, domain, limit=1000):
        """Get URLs for a domain from CommonCrawl"""
        urls = set()
        
        try:
            # CommonCrawl Index API
            index_url = "https://index.commoncrawl.org/CC-MAIN-2023-50-index"
            params = {
                'url': f"*.{domain}/*",
                'output': 'json',
                'limit': limit
            }
            
            response = self.session.get(index_url, params=params, timeout=30)
            response.raise_for_status()
            
            for line in response.text.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        url = data.get('url', '')
                        if url.startswith(('http://', 'https://')):
                            urls.add(url)
                    except json.JSONDecodeError:
                        continue
            
        except Exception as e:
            print(f"Warning: Error fetching from CommonCrawl: {e}")
        
        return list(urls) 