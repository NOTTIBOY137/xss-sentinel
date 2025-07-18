import requests
import time
import random
import json
import hashlib
import base64
from urllib.parse import urlparse, urljoin
from fake_useragent import UserAgent
import cloudscraper
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
import ssl
import socket

class StealthHTTPClient:
    """Advanced stealth HTTP client with WAF bypass capabilities"""
    
    def __init__(self, max_retries=5, timeout=30, stealth_level=3):
        self.max_retries = max_retries
        self.timeout = timeout
        self.stealth_level = stealth_level
        self.session = self._create_stealth_session()
        self.user_agent = UserAgent()
        self.request_history = []
        self.blocked_domains = set()
        
    def _create_stealth_session(self):
        """Create a stealth session with advanced evasion techniques"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Advanced headers for stealth
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        return session
    
    def _get_random_headers(self):
        """Generate random headers for each request"""
        headers = {
            'User-Agent': self.user_agent.random,
            'Accept': random.choice([
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            ]),
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-GB,en;q=0.9',
                'en-CA,en;q=0.9',
                'en-AU,en;q=0.9'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Add random additional headers
        if random.random() > 0.5:
            headers['X-Forwarded-For'] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        
        if random.random() > 0.7:
            headers['X-Real-IP'] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        
        return headers
    
    def _add_stealth_delays(self):
        """Add random delays to appear more human-like"""
        if self.stealth_level >= 2:
            time.sleep(random.uniform(1, 3))
        elif self.stealth_level >= 1:
            time.sleep(random.uniform(0.5, 1.5))
    
    def _bypass_cloudflare(self, url):
        """Attempt to bypass Cloudflare protection"""
        try:
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )
            return scraper.get(url, timeout=self.timeout)
        except Exception as e:
            print(f"Cloudflare bypass failed: {e}")
            return None
    
    def _encode_payload(self, payload: str) -> List[str]:
        """Generate multiple encoded versions of a payload for evasion"""
        encoded_payloads = [payload]
        
        # URL encoding
        try:
            import urllib.parse
            encoded_payloads.append(urllib.parse.quote(payload))
            encoded_payloads.append(urllib.parse.quote_plus(payload))
        except:
            pass
        
        # Base64 encoding
        try:
            encoded_payloads.append(base64.b64encode(payload.encode()).decode())
        except:
            pass
        
        # HTML encoding
        html_encoded = payload.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
        encoded_payloads.append(html_encoded)
        
        # Unicode encoding
        unicode_encoded = ''.join([f'\\u{ord(c):04x}' for c in payload])
        encoded_payloads.append(unicode_encoded)
        
        # Hex encoding
        hex_encoded = ''.join([f'%{ord(c):02x}' for c in payload])
        encoded_payloads.append(hex_encoded)
        
        return list(set(encoded_payloads))  # Remove duplicates
    
    def make_request(self, url: str, method: str = "GET", data: Optional[Dict] = None, 
                    headers: Optional[Dict] = None, payload: Optional[str] = None) -> Optional[requests.Response]:
        """Make a stealth HTTP request with advanced evasion"""
        
        if url in self.blocked_domains:
            print(f"Domain {urlparse(url).netloc} is blocked, skipping...")
            return None
        
        # Add stealth delays
        self._add_stealth_delays()
        
        # Generate headers
        request_headers = self._get_random_headers()
        if headers:
            request_headers.update(headers)
        
        # Encode payload if provided
        if payload and self.stealth_level >= 2:
            encoded_payloads = self._encode_payload(payload)
            payload = random.choice(encoded_payloads)
        
        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    response = self.session.get(
                        url, 
                        headers=request_headers, 
                        timeout=self.timeout,
                        allow_redirects=True,
                        verify=False
                    )
                elif method.upper() == "POST":
                    response = self.session.post(
                        url, 
                        data=data, 
                        headers=request_headers, 
                        timeout=self.timeout,
                        allow_redirects=True,
                        verify=False
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle different response codes
                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    print(f"403 Forbidden for {url}, trying Cloudflare bypass...")
                    cf_response = self._bypass_cloudflare(url)
                    if cf_response:
                        return cf_response
                    else:
                        self.blocked_domains.add(urlparse(url).netloc)
                        return None
                elif response.status_code == 429:
                    print(f"Rate limited (429) for {url}, waiting...")
                    time.sleep(random.uniform(5, 15))
                    continue
                elif response.status_code >= 500:
                    print(f"Server error ({response.status_code}) for {url}, retrying...")
                    time.sleep(random.uniform(2, 5))
                    continue
                else:
                    return response
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed (attempt {attempt+1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(random.uniform(1, 3))
                else:
                    print(f"Max retries reached for {url}")
                    return None
        
        return None
    
    def make_parallel_requests(self, urls: List[str], max_workers: int = 5) -> Dict[str, Optional[requests.Response]]:
        """Make parallel requests with rate limiting"""
        results = {}
        
        def make_single_request(url):
            return url, self.make_request(url)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(make_single_request, url): url for url in urls}
            
            for future in future_to_url:
                url, response = future.result()
                results[url] = response
                time.sleep(random.uniform(0.1, 0.5))  # Rate limiting
        
        return results

# Global stealth client instance
stealth_client = StealthHTTPClient(stealth_level=3)

def make_request(url, method="GET", data=None, headers=None, timeout=10, max_retries=3):
    """Legacy function for backward compatibility"""
    return stealth_client.make_request(url, method, data, headers)

def extract_domain(url):
    """Extract the domain from a URL"""
    parsed_url = urlparse(url)
    return parsed_url.netloc

def normalize_url(url):
    """Normalize a URL by removing fragments and normalizing path"""
    parsed = urlparse(url)
    path = parsed.path
    if not path:
        path = '/'
    
    # Ensure http or https
    scheme = parsed.scheme
    if scheme not in ['http', 'https']:
        scheme = 'http'
    
    # Reconstruct the URL without fragments
    normalized = f"{scheme}://{parsed.netloc}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    
    return normalized

def is_blocked(response):
    """Check if the response indicates blocking"""
    if not response:
        return True
    
    blocked_indicators = [
        'access denied',
        'forbidden',
        'blocked',
        'security check',
        'captcha',
        'cloudflare',
        'distil networks',
        'imperva',
        'akamai',
        'fastly',
        'cloudfront'
    ]
    
    content_lower = response.text.lower()
    return any(indicator in content_lower for indicator in blocked_indicators)

def generate_stealth_payloads(base_payload: str) -> List[str]:
    """Generate stealth versions of XSS payloads"""
    stealth_payloads = []
    
    # Original payload
    stealth_payloads.append(base_payload)
    
    # Case variations
    stealth_payloads.append(base_payload.upper())
    stealth_payloads.append(base_payload.lower())
    stealth_payloads.append(base_payload.swapcase())
    
    # Encoding variations
    stealth_payloads.extend(stealth_client._encode_payload(base_payload))
    
    # Obfuscation techniques
    obfuscated = base_payload.replace('<script>', '<scr\x69pt>')
    stealth_payloads.append(obfuscated)
    
    obfuscated = base_payload.replace('alert', 'al\x65rt')
    stealth_payloads.append(obfuscated)
    
    # Unicode variations
    unicode_variants = [
        base_payload.replace('<', '\u003c'),
        base_payload.replace('>', '\u003e'),
        base_payload.replace('"', '\u0022'),
        base_payload.replace("'", '\u0027')
    ]
    stealth_payloads.extend(unicode_variants)
    
    return list(set(stealth_payloads))  # Remove duplicates
