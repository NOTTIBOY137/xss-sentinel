import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import List, Dict, Any, Optional
from .payload_manager import PayloadManager
from .scanner import XSSScanner


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
            'User-Agent': 'XSS-Sentinel/1.0 (Parallel Scanner)'
        })
        
        self.payload_manager = PayloadManager()
        self.scanner = XSSScanner()
        
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
            response = self.session.get(url, timeout=10)
            
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
            response = self.session.get(url, timeout=10)
            soup = self.scanner._get_soup(response.text)
            
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
                form_url = self.scanner._build_url(page_url, action)
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
                            response = self.session.post(form_url, data=test_data, timeout=10)
                        else:
                            # For GET forms, append to URL
                            test_url = f"{form_url}?{urlencode(test_data)}"
                            response = self.session.get(test_url, timeout=10)
                        
                        # Check if payload is reflected
                        if self._is_payload_reflected(response.text, payload):
                            context = self._analyze_context(response.text, payload)
                            
                            vulnerabilities.append({
                                'url': form_url,
                                'param_name': input_name,
                                'payload': payload,
                                'method': method,
                                'context': context,
                                'response_length': len(response.text),
                                'status_code': response.status_code,
                                'timestamp': time.time()
                            })
                        
                        time.sleep(self.delay)
                        
        except Exception as e:
            print(f"Error testing form: {e}")
        
        return vulnerabilities
    
    def _is_payload_reflected(self, response_text: str, payload: str) -> bool:
        """Check if payload is reflected in response"""
        # Simple reflection check - can be enhanced with more sophisticated analysis
        return payload in response_text
    
    def _analyze_context(self, response_text: str, payload: str) -> str:
        """Analyze the context where payload is reflected"""
        try:
            # Find the position of payload in response
            pos = response_text.find(payload)
            if pos == -1:
                return "unknown"
            
            # Extract context around the payload
            start = max(0, pos - 50)
            end = min(len(response_text), pos + len(payload) + 50)
            context = response_text[start:end]
            
            # Analyze context
            if '<script>' in context and '</script>' in context:
                return "javascript"
            elif context.strip().startswith('<') and context.strip().endswith('>'):
                return "html_tag"
            elif '="' in context and '"' in context:
                return "html_attribute"
            elif 'url(' in context or 'background:' in context:
                return "css"
            else:
                return "html_content"
                
        except Exception:
            return "unknown"
    
    def get_scan_statistics(self) -> Dict[str, Any]:
        """Get scanning statistics"""
        return {
            'total_urls': len(self.urls_to_scan),
            'target_domain': self.target_domain,
            'max_workers': self.max_workers,
            'delay': self.delay,
            'results_dir': self.results_dir
        } 