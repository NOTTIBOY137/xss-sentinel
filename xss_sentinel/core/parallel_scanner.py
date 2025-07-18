import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, urljoin
from typing import List, Dict, Any, Optional
from .payload_manager import PayloadManager
from bs4 import BeautifulSoup
from ..utils.http_utils import stealth_client, generate_stealth_payloads


class ParallelScanner:
    """Advanced parallel XSS vulnerability scanner with stealth capabilities"""
    
    def __init__(self, target_domain: str, max_workers: int = 5, 
                 delay: float = 0.5, results_dir: str = 'reports', stealth_level: int = 3):
        self.target_domain = target_domain
        self.max_workers = max_workers
        self.delay = delay
        self.results_dir = results_dir
        self.stealth_level = stealth_level
        
        # Use the global stealth client
        self.client = stealth_client
        
        self.payload_manager = PayloadManager()
        
        self.urls_to_scan = []
        self.results = []
        self.lock = threading.Lock()
        self.scan_stats = {
            'total_urls': 0,
            'scanned_urls': 0,
            'vulnerabilities_found': 0,
            'blocked_requests': 0,
            'start_time': None,
            'end_time': None
        }
        
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
        self.scan_stats['total_urls'] = len(self.urls_to_scan)
        print(f"Added {len(filtered_urls)} URLs to scan queue")
    
    def scan(self, timeout: Optional[int] = None) -> List[Dict[str, Any]]:
        """Start parallel scanning with stealth capabilities"""
        if not self.urls_to_scan:
            print("No URLs to scan")
            return []
        
        print(f"Starting stealth parallel scan of {len(self.urls_to_scan)} URLs with {self.max_workers} workers")
        print(f"Stealth level: {self.stealth_level}")
        
        self.scan_stats['start_time'] = time.time()
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
                            self.scan_stats['vulnerabilities_found'] += len(result)
                    self.scan_stats['scanned_urls'] += 1
                except Exception as e:
                    print(f"Error scanning {url}: {e}")
                    self.scan_stats['blocked_requests'] += 1
        
        self.scan_stats['end_time'] = time.time()
        scan_time = self.scan_stats['end_time'] - self.scan_stats['start_time']
        
        print(f"Stealth scan completed in {scan_time:.2f} seconds")
        print(f"Found {len(vulnerabilities)} potential vulnerabilities")
        print(f"Blocked requests: {self.scan_stats['blocked_requests']}")
        
        return vulnerabilities
    
    def _scan_single_url(self, url: str) -> List[Dict[str, Any]]:
        """Scan a single URL for XSS vulnerabilities with stealth techniques"""
        vulnerabilities = []
        
        try:
            # Parse URL to get parameters
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)
            
            # Test URL parameters
            if params:
                for param_name, param_values in params.items():
                    if param_values:
                        original_value = param_values[0]
                        param_vulns = self._test_parameter(url, param_name, original_value)
                        vulnerabilities.extend(param_vulns)
            
            # Test forms
            form_vulns = self._test_forms(url)
            vulnerabilities.extend(form_vulns)
            
            # Test DOM-based XSS
            dom_vulns = self._test_dom_xss(url)
            vulnerabilities.extend(dom_vulns)
            
        except Exception as e:
            print(f"Error scanning {url}: {e}")
        
        return vulnerabilities
    
    def _test_parameter(self, url: str, param_name: str, original_value: str) -> List[Dict[str, Any]]:
        """Test a URL parameter for XSS vulnerabilities"""
        vulnerabilities = []
        
        try:
            response = stealth_client.make_request(url)
            
            if not response:
                return []
            
            # Get stealth payloads
            base_payloads = self.payload_manager.get_payloads(count=10)
            stealth_payloads = []
            for payload in base_payloads:
                stealth_payloads.extend(generate_stealth_payloads(payload))
            
            # Limit payloads to avoid overwhelming the target
            stealth_payloads = stealth_payloads[:20]
            
            for payload in stealth_payloads:
                vuln = self._test_single_payload(url, param_name, payload, original_value)
                if vuln:
                    vulnerabilities.append(vuln)
                
                # Stealth delay
                time.sleep(random.uniform(0.5, 2.0))
                
        except Exception as e:
            print(f"Error testing parameter {param_name} on {url}: {e}")
        
        return vulnerabilities
    
    def _test_single_payload(self, url: str, param_name: str, payload: str, original_value: str) -> Optional[Dict[str, Any]]:
        """Test a single payload against a URL parameter"""
        try:
            # Parse URL
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)
            
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
            
            # Make stealth request
            response = stealth_client.make_request(test_url, payload=payload)
            
            if response and response.status_code == 200:
                # Check if payload is reflected
                if self._is_payload_reflected(response.text, payload):
                    context = self._analyze_context(response.text, payload)
                    
                    return {
                        'url': test_url,
                        'param_name': param_name,
                        'payload': payload,
                        'original_value': original_value,
                        'context': context,
                        'response_length': len(response.text),
                        'status_code': response.status_code,
                        'timestamp': time.time(),
                        'type': 'reflected_xss'
                    }
            
        except Exception as e:
            print(f"Error testing payload on {url}: {e}")
        
        return None
    
    def _test_forms(self, url: str) -> List[Dict[str, Any]]:
        """Test forms on a page for XSS vulnerabilities"""
        vulnerabilities = []
        
        try:
            response = stealth_client.make_request(url)
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
                    # Get stealth payloads
                    base_payloads = self.payload_manager.get_payloads(count=5)
                    stealth_payloads = []
                    
                    for payload in base_payloads:
                        stealth_payloads.extend(generate_stealth_payloads(payload))
                    
                    # Test each payload
                    for payload in stealth_payloads[:10]:  # Limit for stealth
                        test_data[input_name] = payload
                        
                        if method == 'post':
                            response = stealth_client.make_request(form_url, method='POST', data=test_data, payload=payload)
                        else:
                            # For GET forms, append to URL
                            test_url = f"{form_url}?{urlencode(test_data)}"
                            response = stealth_client.make_request(test_url, payload=payload)
                        
                        # Check if payload is reflected
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
    
    def _test_dom_xss(self, url: str) -> List[Dict[str, Any]]:
        """Test for DOM-based XSS vulnerabilities"""
        vulnerabilities = []
        try:
            response = stealth_client.make_request(url)
            if not response or response.status_code != 200:
                return []
            # Look for JavaScript that processes user input
            js_patterns = [
                r'document\.write\s*\(\s*[^)]*location\.[^)]*\)',
                r'document\.write\s*\(\s*[^)]*document\.URL[^)]*\)',
                r'document\.write\s*\(\s*[^)]*document\.referrer[^)]*\)',
                r'innerHTML\s*=\s*[^;]*location\.[^;]*',
                r'innerHTML\s*=\s*[^;]*document\.URL[^;]*',
                r'eval\s*\(\s*[^)]*location\.[^)]*\)',
                r'setTimeout\s*\(\s*[^)]*location\.[^)]*\)',
                r'setInterval\s*\(\s*[^)]*location\.[^)]*\)'
            ]
            content = response.text
            for pattern in js_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    vulnerabilities.append({
                        'url': url,
                        'param_name': 'DOM',
                        'payload': 'DOM-based XSS detected',
                        'original_value': '',
                        'context': 'javascript',
                        'response_length': len(content),
                        'status_code': response.status_code,
                        'timestamp': time.time(),
                        'type': 'dom_xss'
                    })
                    break
        except Exception as e:
            print(f"Error testing DOM XSS on {url}: {e}")
        return vulnerabilities
    
    def _is_payload_reflected(self, response_text: str, payload: str) -> bool:
        """Check if a payload is reflected in the response text"""
        return payload in response_text
    
    def _analyze_context(self, response_text: str, payload: str) -> str:
        """Analyze the context where payload is reflected"""
        try:
            # Find the position of the payload
            pos = response_text.find(payload)
            if pos == -1:
                # Try encoded versions
                try:
                    import urllib.parse
                    url_encoded = urllib.parse.quote(payload)
                    pos = response_text.find(url_encoded)
                except:
                    pass
            
            if pos == -1:
                return "unknown"
            
            # Get surrounding context
            start = max(0, pos - 100)
            end = min(len(response_text), pos + len(payload) + 100)
            context = response_text[start:end]
            
            # Determine context type
            if '<script>' in context and '</script>' in context:
                return "javascript"
            elif '<' in context and '>' in context:
                return "html"
            elif '"' in context:
                return "attribute"
            elif "'" in context:
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

# Import missing module
import re
import random 
