import re
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from ..utils.http_utils import make_request

class XSSScanner:
    def __init__(self, url, depth=2, use_ml=True, timeout=10, delay=0.5, 
                include_subdomains=False, user_agent=None, cookies=None):
        self.target_url = url
        self.scan_depth = depth
        self.visited_urls = set()
        self.vulnerable_urls = []
        self.input_points = []
        self.use_ml = use_ml
        self.timeout = timeout
        self.delay = delay
        self.include_subdomains = include_subdomains
        self.user_agent = user_agent
        self.cookies = cookies
    
    def scan(self):
        """Main scanning process"""
        print(f"Starting XSS scan on: {self.target_url}")
        
        # Discover URLs
        from .crawler import Crawler
        crawler = Crawler(
            self.target_url, 
            max_depth=self.scan_depth,
            include_subdomains=self.include_subdomains
        )
        urls = crawler.crawl()
        
        # Add discovered URLs to visited list
        self.visited_urls.update(urls)
        
        # Find input points (forms, URL parameters)
        self._identify_input_points()
        
        # Test each input point
        results = self._test_input_points()
        
        return results
    
    def _identify_input_points(self):
        """Find potential XSS injection points"""
        print("Identifying potential injection points...")
        
        for url in self.visited_urls:
            try:
                response = make_request(url, timeout=self.timeout)
                if not response:
                    continue
                
                # Check URL parameters
                parsed_url = urlparse(url)
                if parsed_url.query:
                    params = parsed_url.query.split('&')
                    for param in params:
                        if '=' in param:
                            name = param.split('=')[0]
                            print(f"Found URL parameter: {name} in {url}")
                            self.input_points.append({
                                'type': 'url_param',
                                'url': url,
                                'param_name': name
                            })
                
                # Check for forms
                soup = BeautifulSoup(response.text, 'html.parser')
                forms = soup.find_all('form')
                
                for form in forms:
                    action = form.get('action', '')
                    method = form.get('method', 'get').lower()
                    form_url = urljoin(url, action) if action else url
                    
                    inputs = form.find_all(['input', 'textarea', 'select'])
                    for input_field in inputs:
                        field_type = input_field.get('type', '')
                        field_name = input_field.get('name', '')
                        
                        # Skip submit buttons and hidden fields
                        if field_type not in ['submit', 'button', 'hidden'] and field_name:
                            print(f"Found form input: {field_name} in {form_url} (method: {method})")
                            self.input_points.append({
                                'type': 'form',
                                'url': form_url,
                                'form_method': method,
                                'param_name': field_name
                            })
            
            except Exception as e:
                print(f"Error processing {url}: {e}")
    
    def _test_input_points(self):
        """Test each input point for XSS vulnerabilities"""
        results = []
        
        print(f"Testing {len(self.input_points)} potential injection points...")
        
        for point in self.input_points:
            vulnerable, context, payload = self._test_injection_point(point)
            
            if vulnerable:
                print(f"Found XSS vulnerability in {point['url']} - Parameter: {point['param_name']}")
                results.append({
                    'url': point['url'],
                    'parameter': point['param_name'],
                    'type': point['type'],
                    'payload': payload,
                    'context': context
                })
                
            # Add delay between requests to avoid overloading the server
            time.sleep(self.delay)
        
        return results
    
    def _test_injection_point(self, point):
        """Test a specific injection point with various payloads"""
        # Generate test payload
        test_marker = f"XSS{hash(point['url'] + point['param_name'])}"
        
        try:
            # Send a benign payload first to identify context
            response = self._inject_payload(point, test_marker)
            if not response:
                return False, None, None
            
            # Analyze where/if our marker appears (to identify context)
            context = None
            if test_marker in response.text:
                if self.use_ml:
                    # Use ML to determine context
                    from ..ai.context_analyzer import AdvancedContextAnalyzer
                    analyzer = AdvancedContextAnalyzer()
                    context_info = analyzer.identify_context(response.text, test_marker)
                    context = context_info.get("context", "html")
                else:
                    # Basic context detection
                    context = self._basic_context_detection(response.text, test_marker)
            
                # Now test with actual XSS payloads based on the context
                payloads = self._get_payloads(context)
                
                for payload in payloads:
                    # Add delay between requests
                    time.sleep(self.delay)
                    
                    injection_response = self._inject_payload(point, payload)
                    if not injection_response:
                        continue
                    
                    # Check if the payload was executed (simplified check)
                    if self._check_payload_execution(injection_response, payload):
                        return True, context, payload
        
        except Exception as e:
            print(f"Error testing {point['url']}: {e}")
        
        return False, None, None
    
    def _inject_payload(self, point, payload):
        """Inject a payload into the specified input point"""
        try:
            if point['type'] == 'url_param':
                # For URL parameters
                parsed = urlparse(point['url'])
                query_parts = parsed.query.split('&')
                
                # Replace the target parameter with our payload
                new_query_parts = []
                for part in query_parts:
                    if '=' in part and part.split('=')[0] == point['param_name']:
                        new_query_parts.append(f"{point['param_name']}={payload}")
                    else:
                        new_query_parts.append(part)
                
                # Reconstruct the URL
                new_query = '&'.join(new_query_parts)
                url_parts = list(parsed)
                url_parts[4] = new_query
                
                # Reconstruct URL (workaround for urlunparse issue)
                new_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if new_query:
                    new_url += f"?{new_query}"
                if parsed.fragment:
                    new_url += f"#{parsed.fragment}"
                
                # Make the request
                headers = {}
                if self.user_agent:
                    headers['User-Agent'] = self.user_agent
                
                return make_request(
                    new_url, 
                    timeout=self.timeout, 
                    headers=headers
                )
                
            elif point['type'] == 'form':
                # For form inputs
                data = {point['param_name']: payload}
                
                headers = {}
                if self.user_agent:
                    headers['User-Agent'] = self.user_agent
                
                if point.get('form_method', 'get').lower() == 'post':
                    return make_request(
                        point['url'], 
                        method="POST", 
                        data=data, 
                        timeout=self.timeout, 
                        headers=headers
                    )
                else:
                    return make_request(
                        point['url'], 
                        method="GET", 
                        data=data, 
                        timeout=self.timeout, 
                        headers=headers
                    )
        
        except Exception as e:
            print(f"Error injecting payload: {e}")
            return None
    
    def _get_payloads(self, context):
        """Get appropriate XSS payloads for the identified context"""
        if self.use_ml:
            # Use AI-based payload generator if available
            try:
                from ..ai.payload_generator import AIPayloadGenerator
                generator = AIPayloadGenerator()
                return generator.generate_payloads(context, count=5)
            except ImportError:
                # Fall back to basic payloads if AI module isn't available
                return self._get_basic_payloads(context)
        else:
            return self._get_basic_payloads(context)
    
    def _get_basic_payloads(self, context):
        """Get basic XSS payloads for different contexts"""
        if context == "js":
            return [
                "';alert('XSS');//",
                "\";alert('XSS');//",
                "\\';alert('XSS');//",
                "alert('XSS')",
                "alert`XSS`"
            ]
        elif context == "attribute":
            return [
                "\" onmouseover=\"alert('XSS')\"",
                "\" onfocus=\"alert('XSS')\"",
                "\" onclick=\"alert('XSS')\"",
                "\" onerror=\"alert('XSS')\"",
                "' onmouseover='alert(\"XSS\")'"
            ]
        elif context == "url":
            return [
                "javascript:alert('XSS')",
                "data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=",
                "data:text/html,<script>alert('XSS')</script>"
            ]
        else:  # Default to HTML context
            return [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg/onload=alert('XSS')>",
                "<body onload=alert('XSS')>",
                "<iframe src='javascript:alert(`XSS`)'>"
            ]
    
    def _basic_context_detection(self, html, marker):
        """Basic context detection for XSS (simplified)"""
        if f"<script>{marker}" in html:
            return "js"
        elif f"=\"{marker}\"" in html or f"='{marker}'" in html:
            return "attribute"
        elif f"<{marker}" in html:
            return "tag"
        else:
            return "html"
    
    def _check_payload_execution(self, response, payload):
        """Check if the payload was executed (simplified)"""
        # In a real implementation, this would involve more sophisticated checks
        # For now, we'll do a simple check if the payload appears unmodified
        # This is not reliable for actual testing but serves as a placeholder
        return payload in response.text and "alert" in payload
