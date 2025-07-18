#!/usr/bin/env python3
"""
Script to fix XSS Sentinel files
"""

import os

def fix_parallel_scanner():
    """Fix the parallel scanner file"""
    content = '''import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, urljoin
from typing import List, Dict, Any, Optional
from .payload_manager import PayloadManager
from bs4 import BeautifulSoup
from ..utils.http_utils import make_request


class ParallelScanner:
    """Parallel XSS vulnerability scanner"""
    
    def __init__(self, target_domain: str, max_workers: int = 5, 
                 delay: float = 0.5, results_dir: str = 'reports'):
        self.target_domain = target_domain
        self.max_workers = max_workers
        self.delay = delay
        self.results_dir = results_dir
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.payload_manager = PayloadManager()
        
        self.urls_to_scan = []
        self.results = []
        self.lock = threading.Lock()
        
    def add_urls(self, urls: List[str]):
        """Add URLs to scan"""
        # Filter URLs to only include those from target domain
        filtered_urls = []
        for url in urls:
            try:
                parsed = urlparse(url)
                if parsed.netloc == self.target_domain or parsed.netloc.endswith('.' + self.target_domain):
                    filtered_urls.append(url)
            except Exception:
                continue
        
        self.urls_to_scan.extend(filtered_urls)
        print(f"Added {len(filtered_urls)} URLs to scan queue")
    
    def scan(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """Start parallel scanning"""
        if not self.urls_to_scan:
            print("No URLs to scan")
            return []
        
        print(f"Starting parallel scan of {len(self.urls_to_scan)} URLs with {self.max_workers} workers")
        
        start_time = time.time()
        vulnerabilities = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all scan tasks
            future_to_url = {
                executor.submit(self._scan_single_url, url): url 
                for url in self.urls_to_scan
            }
            
            # Process completed tasks
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result(timeout=timeout)
                    if result:
                        with self.lock:
                            vulnerabilities.extend(result)
                except Exception as e:
                    print(f"Error scanning {url}: {e}")
        
        scan_time = time.time() - start_time
        print(f"Parallel scan completed in {scan_time:.2f} seconds")
        print(f"Found {len(vulnerabilities)} potential vulnerabilities")
        
        return vulnerabilities
    
    def _scan_single_url(self, url: str) -> List[Dict[str, Any]]:
        """Scan a single URL for XSS vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Parse URL to get parameters
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)
            
            if not params:
                # No parameters to test
                return []
            
            # Test each parameter
            for param_name, param_values in params.items():
                if param_values:
                    # Test with the first value
                    original_value = param_values[0]
                    
                    # Get payloads to test
                    payloads = self.payload_manager.get_payloads(count=10)
                    
                    for payload in payloads:
                        # Create test URL with payload
                        test_params = params.copy()
                        test_params[param_name] = [payload]
                        
                        test_query = urlencode(test_params, doseq=True)
                        test_url = urlunparse((
                            parsed_url.scheme,
                            parsed_url.netloc,
                            parsed_url.path,
                            parsed_url.params,
                            test_query,
                            parsed_url.fragment
                        ))
                        
                        # Test the URL
                        vuln = self._test_url_for_xss(test_url, param_name, payload, original_value)
                        if vuln:
                            vulnerabilities.append(vuln)
                        
                        # Rate limiting
                        time.sleep(self.delay)
            
            # Also test POST forms if available
            form_vulns = self._test_forms(url)
            vulnerabilities.extend(form_vulns)
            
        except Exception as e:
            print(f"Error scanning {url}: {e}")
        
        return vulnerabilities
    
    def _test_url_for_xss(self, url: str, param_name: str, payload: str, original_value: str) -> Optional[Dict[str, Any]]:
        """Test a specific URL with payload for XSS"""
        try:
            response = make_request(url, stealth_mode=True)
            
            if not response:
                return None
            
            # Check if payload is reflected in response
            if self._is_payload_reflected(response.text, payload):
                # Analyze the context
                context = self._analyze_context(response.text, payload)
                
                return {
                    'url': url,
                    'param_name': param_name,
                    'payload': payload,
                    'original_value': original_value,
                    'context': context,
                    'response_length': len(response.text),
                    'status_code': response.status_code,
                    'timestamp': time.time()
                }
            
        except Exception as e:
            print(f"Error testing {url}: {e}")
        
        return None
    
    def _test_forms(self, url: str) -> List[Dict[str, Any]]:
        """Test forms on a page for XSS vulnerabilities"""
        vulnerabilities = []
        
        try:
            response = make_request(url, stealth_mode=True)
            if not response:
                return vulnerabilities
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            forms = soup.find_all('form')
            for form in forms:
                form_vulns = self._test_single_form(form, url)
                vulnerabilities.extend(form_vulns)
                
        except Exception as e:
            print(f"Error testing forms on {url}: {e}")
        
        return vulnerabilities
    
    def _test_single_form(self, form, page_url: str) -> List[Dict[str, Any]]:
        """Test a single form for XSS vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Extract form data
            action = form.get('action', '')
            method = form.get('method', 'get').lower()
            
            if action:
                form_url = urljoin(page_url, action)
            else:
                form_url = page_url
            
            # Find input fields
            inputs = form.find_all(['input', 'textarea'])
            test_data = {}
            
            for input_tag in inputs:
                input_type = input_tag.get('type', 'text')
                input_name = input_tag.get('name', '')
                
                if input_name and input_type in ['text', 'textarea', 'search', 'url', 'email']:
                    # Test with payload
                    payloads = self.payload_manager.get_payloads(count=5)
                    
                    for payload in payloads:
                        test_data[input_name] = payload
                        
                        if method == 'post':
                            response = make_request(form_url, method='POST', data=test_data, stealth_mode=True)
                        else:
                            # For GET forms, append to URL
                            test_url = f"{form_url}?{urlencode(test_data)}"
                            response = make_request(test_url, stealth_mode=True)
                        
                        if response and self._is_payload_reflected(response.text, payload):
                            context = self._analyze_context(response.text, payload)
                            
                            vulnerabilities.append({
                                'url': form_url,
                                'param_name': input_name,
                                'payload': payload,
                                'original_value': '',
                                'context': context,
                                'response_length': len(response.text),
                                'status_code': response.status_code,
                                'timestamp': time.time()
                            })
                        
                        # Rate limiting
                        time.sleep(self.delay)
                        
        except Exception as e:
            print(f"Error testing form on {page_url}: {e}")
        
        return vulnerabilities
    
    def _is_payload_reflected(self, response_text: str, payload: str) -> bool:
        """Check if payload is reflected in the response"""
        return payload in response_text
    
    def _analyze_context(self, response_text: str, payload: str) -> str:
        """Analyze the context where payload is reflected"""
        try:
            # Find the position of the payload
            pos = response_text.find(payload)
            if pos == -1:
                return "unknown"
            
            # Get surrounding context
            start = max(0, pos - 50)
            end = min(len(response_text), pos + len(payload) + 50)
            context = response_text[start:end]
            
            # Determine context type
            if '<script>' in context and '</script>' in context:
                return "javascript"
            elif '<' in context and '>' in context:
                return "html"
            elif '"' in context:
                return "attribute"
            else:
                return "text"
                
        except Exception:
            return "unknown"
    
    def get_scan_statistics(self) -> Dict[str, Any]:
        """Get statistics about the scan"""
        return {
            'total_urls': len(self.urls_to_scan),
            'scanned_urls': len(self.results),
            'vulnerabilities_found': len(self.results),
            'target_domain': self.target_domain
        }
'''
    
    with open('xss_sentinel/core/parallel_scanner.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Fixed parallel_scanner.py")

def fix_http_utils():
    """Fix the HTTP utils file"""
    content = '''import requests
from urllib.parse import urlparse
import random
import time
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Extended User-Agent strings for better stealth
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0"
]

# Common headers to appear more like a real browser
BROWSER_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
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
}

def make_request(url, method="GET", data=None, headers=None, timeout=15, max_retries=5, stealth_mode=True, params=None):
    """Make an HTTP request with advanced stealth and anti-blocking capabilities"""
    if not headers:
        headers = {}
    
    # Add stealth headers if enabled
    if stealth_mode:
        # Add random User-Agent
        if 'User-Agent' not in headers:
            headers['User-Agent'] = random.choice(USER_AGENTS)
        
        # Add browser-like headers
        for key, value in BROWSER_HEADERS.items():
            if key not in headers:
                headers[key] = value
    
    # Add random delay for stealth
    if stealth_mode:
        time.sleep(random.uniform(1, 3))
    
    # Create session with advanced settings
    session = requests.Session()
    session.verify = False
    
    # Configure session for stealth
    if stealth_mode:
        session.headers.update(headers)
    
    for attempt in range(max_retries):
        try:
            if method.upper() == "GET":
                response = session.get(url, timeout=timeout, allow_redirects=True, params=params)
            elif method.upper() == "POST":
                response = session.post(url, data=data, timeout=timeout, allow_redirects=True, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle common blocking responses
            if response.status_code == 403:
                print(f"Access forbidden (403) for {url} - trying with different approach...")
                # Try with different User-Agent and headers
                headers['User-Agent'] = random.choice(USER_AGENTS)
                headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                session.headers.update(headers)
                time.sleep(random.uniform(2, 5))
                continue
            elif response.status_code == 429:
                print(f"Rate limited (429) for {url} - waiting longer...")
                time.sleep(random.uniform(10, 20))
                continue
            elif response.status_code >= 500:
                print(f"Server error ({response.status_code}) for {url} - retrying...")
                time.sleep(random.uniform(3, 8))
                continue
            elif response.status_code == 200:
                # Check if blocked by WAF
                if is_blocked(response):
                    print(f"WAF detected for {url} - trying different approach...")
                    # Try with different headers
                    headers['User-Agent'] = random.choice(USER_AGENTS)
                    headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                    session.headers.update(headers)
                    time.sleep(random.uniform(2, 5))
                    continue
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                # Exponential backoff
                time_to_sleep = 2 ** attempt
                print(f"Retrying in {time_to_sleep} seconds...")
                time.sleep(time_to_sleep)
            else:
                print(f"Max retries reached for {url}")
                return None

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
        'cloudfront',
        'blocked by',
        'security policy',
        'request blocked',
        'suspicious activity'
    ]
    
    content_lower = response.text.lower()
    return any(indicator in content_lower for indicator in blocked_indicators)

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

def get_random_delay():
    """Get a random delay for stealth"""
    return random.uniform(1, 5)
'''
    
    with open('xss_sentinel/utils/http_utils.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Fixed http_utils.py")

def fix_requirements():
    """Fix the requirements file"""
    content = '''requests>=2.28.1
beautifulsoup4>=4.11.1
scikit-learn>=1.1.2
numpy>=1.23.2
tqdm>=4.64.0
colorama>=0.4.5
joblib>=1.1.0
urllib3>=1.26.0
lxml>=4.9.0
'''
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Fixed requirements.txt")

def main():
    """Run all fixes"""
    print("🔧 Fixing XSS Sentinel files...")
    
    try:
        fix_parallel_scanner()
        fix_http_utils()
        fix_requirements()
        
        print("\n🎉 All files fixed successfully!")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Fix: Complete XSS Sentinel with anti-blocking capabilities'")
        print("3. git push origin main")
        
    except Exception as e:
        print(f"❌ Error fixing files: {e}")

if __name__ == "__main__":
    main()
