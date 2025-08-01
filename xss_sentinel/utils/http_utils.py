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
import urllib3
import re

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def is_valid_url(url: str) -> bool:
    """Validate if a URL is safe to request"""
    if not url or not isinstance(url, str):
        return False
    
    # Check for invalid protocols
    invalid_protocols = ['javascript:', 'data:', 'file:', 'ftp:', 'mailto:', 'tel:']
    url_lower = url.lower()
    for protocol in invalid_protocols:
        if url_lower.startswith(protocol):
            return False
    
    # Check for malformed URLs with encoded characters in hostname
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check for encoded characters in hostname that would cause DNS resolution issues
        hostname = parsed.netloc.split(':')[0]  # Remove port if present
        if '%' in hostname:
            return False
        
        # Check for suspicious characters in hostname
        if re.search(r'[<>"\']', hostname):
            return False
        
        # Check for malformed hostnames (like arabica1.cf which may be invalid)
        # This is a basic check - in practice, you might want more sophisticated validation
        if len(hostname) < 3 or len(hostname) > 253:
            return False
        
        # Check for invalid TLD patterns (very basic)
        if hostname.count('.') == 0:
            # Allow localhost without dots
            if hostname.lower() != 'localhost':
                return False
        
        # Check for suspicious patterns in hostname
        suspicious_patterns = [
            r'\.cf$',  # .cf domains are often used for malicious purposes
            r'\.tk$',  # .tk domains are often used for malicious purposes
            r'\.ml$',  # .ml domains are often used for malicious purposes
            r'\.ga$',  # .ga domains are often used for malicious purposes
            r'\.gq$',  # .gq domains are often used for malicious purposes
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, hostname, re.IGNORECASE):
                # Allow these domains but log them
                print(f"Warning: Suspicious domain detected: {hostname}")
                # For now, we'll allow them but you might want to block them
                # return False
            
        return True
    except Exception:
        return False

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
        session = requests.Session()
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
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
        if random.random() > 0.5:
            headers['X-Forwarded-For'] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        if random.random() > 0.7:
            headers['X-Real-IP'] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        return headers
    def _add_stealth_delays(self):
        if self.stealth_level >= 2:
            time.sleep(random.uniform(1, 3))
        elif self.stealth_level >= 1:
            time.sleep(random.uniform(0.5, 1.5))
    def _bypass_cloudflare(self, url):
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
        encoded_payloads = [payload]
        try:
            import urllib.parse
            encoded_payloads.append(urllib.parse.quote(payload))
            encoded_payloads.append(urllib.parse.quote_plus(payload))
        except:
            pass
        try:
            encoded_payloads.append(base64.b64encode(payload.encode()).decode())
        except:
            pass
        html_encoded = payload.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
        encoded_payloads.append(html_encoded)
        unicode_encoded = ''.join([f'\\u{ord(c):04x}' for c in payload])
        encoded_payloads.append(unicode_encoded)
        hex_encoded = ''.join([f'%{ord(c):02x}' for c in payload])
        encoded_payloads.append(hex_encoded)
        return list(set(encoded_payloads))
    def make_request(self, url: str, method: str = "GET", data: Optional[Dict] = None, headers: Optional[Dict] = None, payload: Optional[str] = None) -> Optional[requests.Response]:
        # Validate URL before making request
        if not is_valid_url(url):
            print(f"Skipping invalid URL: {url}")
            return None
            
        if url in self.blocked_domains:
            print(f"Domain {urlparse(url).netloc} is blocked, skipping...")
            return None
        self._add_stealth_delays()
        request_headers = self._get_random_headers()
        if headers:
            request_headers.update(headers)
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
        results = {}
        def make_single_request(url):
            return url, self.make_request(url)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(make_single_request, url): url for url in urls}
            for future in future_to_url:
                url, response = future.result()
                results[url] = response
                time.sleep(random.uniform(0.1, 0.5))
        return results
stealth_client = StealthHTTPClient(stealth_level=3)
def make_request(url, method="GET", data=None, headers=None):
    return stealth_client.make_request(url, method, data, headers)
def is_blocked(response):
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
        'cloudfront',
        'blocked by',
        'security policy',
        'request blocked',
        'suspicious activity'
    ]
    content_lower = response.text.lower()
    return any(indicator in content_lower for indicator in blocked_indicators)
def generate_stealth_payloads(base_payload: str) -> List[str]:
    stealth_payloads = []
    stealth_payloads.append(base_payload)
    stealth_payloads.append(base_payload.upper())
    stealth_payloads.append(base_payload.lower())
    stealth_payloads.append(base_payload.swapcase())
    stealth_payloads.extend(stealth_client._encode_payload(base_payload))
    obfuscated = base_payload.replace('<script>', '<scr\x69pt>')
    stealth_payloads.append(obfuscated)
    obfuscated = base_payload.replace('alert', 'al\x65rt')
    stealth_payloads.append(obfuscated)
    unicode_variants = [
        base_payload.replace('<', '\u003c'),
        base_payload.replace('>', '\u003e'),
        base_payload.replace('"', '\u0022'),
        base_payload.replace("'", '\u0027')
    ]
    stealth_payloads.extend(unicode_variants)
    return list(set(stealth_payloads))
