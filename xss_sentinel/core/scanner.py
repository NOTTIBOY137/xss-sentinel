import re
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from urllib.parse import urljoin, urlparse
from ..utils.http_utils import make_request
from ..utils.browser_verifier import verify_xss_execution
# Remove legacy ML imports
# from ..ml.context_analyzer import ContextAnalyzer
# from ..ml.payload_generator import PayloadGenerator
# Add new AI imports
try:
    from ..ai.core_ai import XSSAICore
    from ..ai.transformer_generator import TransformerPayloadGenerator
    from ..ai.adaptive_learning import AdaptiveLearningEngine
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class XSSScanner:
    def __init__(self, url, depth=2, use_ml=True):
        self.target_url = url
        self.scan_depth = depth
        self.visited_urls = set()
        self.vulnerable_urls = []
        self.input_points = []
        self.use_ml = use_ml
        
        # Initialize AI components if enabled
        if self.use_ml and AI_AVAILABLE:
            self.ai_core = XSSAICore()
            self.transformer_gen = TransformerPayloadGenerator()
            self.adaptive_engine = AdaptiveLearningEngine()
        else:
            self.ai_core = None
            self.transformer_gen = None
            self.adaptive_engine = None
    
    def scan(self):
        """Main scanning process"""
        print(f"Starting XSS scan on: {self.target_url}")
        self._crawl(self.target_url, depth=self.scan_depth)
        
        # Find input points (forms, URL parameters)
        self._identify_input_points()
        
        # Test each input point
        results = self._test_input_points()
        
        return results
    
    def _crawl(self, url, depth=2):
        """Basic crawler to discover pages within the target domain"""
        if depth == 0 or url in self.visited_urls:
            return
        
        try:
            self.visited_urls.add(url)
            response = make_request(url)
            if not response:
                return
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links on the page
            for link in soup.find_all('a', href=True):
                if not isinstance(link, Tag):
                    continue
                href = link.get('href')
                if not isinstance(href, str) or not href:
                    continue
                full_url = urljoin(url, href)
                
                # Only follow links to the same domain
                if self._same_domain(full_url, url):
                    self._crawl(full_url, depth - 1)
        
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    
    def _same_domain(self, url1, url2):
        """Check if two URLs belong to the same domain"""
        return urlparse(url1).netloc == urlparse(url2).netloc
    
    def _identify_input_points(self):
        """Find potential XSS injection points"""
        for url in self.visited_urls:
            try:
                response = make_request(url)
                if not response:
                    continue
                
                # Check URL parameters
                parsed_url = urlparse(url)
                if parsed_url.query:
                    params = parsed_url.query.split('&')
                    for param in params:
                        if '=' in param:
                            name = param.split('=')[0]
                            self.input_points.append({
                                'type': 'url_param',
                                'url': url,
                                'param_name': name
                            })
                
                # Check for forms
                soup = BeautifulSoup(response.text, 'html.parser')
                forms = soup.find_all('form')
                
                for form in forms:
                    if not isinstance(form, Tag):
                        continue
                    action = form.get('action', '')
                    method = form.get('method', 'get')
                    if not isinstance(method, str):
                        method = 'get'
                    method = method.lower()
                    form_url = urljoin(url, str(action))
                    inputs = form.find_all(['input', 'textarea'])
                    for input_field in inputs:
                        if not isinstance(input_field, Tag):
                            continue
                        field_type = input_field.get('type', '')
                        field_name = input_field.get('name', '')
                        if not isinstance(field_type, str):
                            field_type = ''
                        if not isinstance(field_name, str):
                            field_name = ''
                        # Skip submit buttons and hidden fields
                        if field_type not in ['submit', 'button', 'hidden'] and field_name:
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
            vulnerable, context, payload, verified, evidence = self._test_injection_point(point)
            
            if vulnerable:
                print(f"Found XSS vulnerability in {point['url']} - Parameter: {point['param_name']} (Verified: {verified})")
                results.append({
                    'url': point['url'],
                    'parameter': point['param_name'],
                    'type': point['type'],
                    'payload': payload,
                    'context': context,
                    'verified': verified,
                    'evidence': evidence
                })
        
        return results
    
    def _test_injection_point(self, point):
        """Test a specific injection point with various payloads"""
        test_marker = f"XSS{hash(point['url'] + point['param_name'])}"
        try:
            response = self._inject_payload(point, test_marker)
            if not response:
                return False, None, None, None, None
            context = None
            if test_marker in response.text:
                if self.use_ml and self.ai_core:
                    # Use advanced AI context analysis
                    context = self.ai_core.analyze_context(response.text, point['url'])
                else:
                    context = self._basic_context_detection(response.text, test_marker)
                payloads = self._get_payloads(context, point)
                for payload in payloads:
                    injection_response = self._inject_payload(point, payload)
                    if not injection_response:
                        continue
                    if self._check_payload_execution(injection_response, payload):
                        # Browser-based verification
                        verified, evidence = verify_xss_execution(
                            point['url'], payload, point['param_name'],
                            point.get('form_method', 'get'), context
                        )
                        if verified:
                            # Real-time learning: update adaptive engine
                            if self.use_ml and self.adaptive_engine:
                                context_dict = context if isinstance(context, dict) else {'context_type': context}
                                self.adaptive_engine.learn_from_result(payload, context_dict, True, {'response': injection_response.text})
                            return True, context, payload, True, evidence
                        else:
                            return True, context, payload, False, evidence
        except Exception as e:
            print(f"Error testing {point['url']}: {e}")
        return False, None, None, False, None
    
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
                new_url = urlparse('').geturl()
                
                # Make the request
                return make_request(new_url)
                
            elif point['type'] == 'form':
                # For form inputs
                data = {point['param_name']: payload}
                
                if point['form_method'] == 'post':
                    return requests.post(point['url'], data=data, timeout=10)
                else:
                    return requests.get(point['url'], params=data, timeout=10)
        
        except Exception as e:
            print(f"Error injecting payload: {e}")
            return None
    
    def _get_payloads(self, context, point=None):
        """Get appropriate XSS payloads for the identified context"""
        if self.use_ml and self.ai_core:
            # Use AI-powered payload generation
            try:
                ai_payloads = self.ai_core.generate_ai_payloads(context, point['url'] if point else self.target_url)
                # Optionally add transformer-based and adaptive payloads
                if self.transformer_gen:
                    ai_payloads += self.transformer_gen.generate_context_payloads(str(context), count=5)
                if self.adaptive_engine:
                    ai_payloads += self.adaptive_engine.generate_adaptive_payloads(context, count=5)
                # Deduplicate and return
                return list(set(ai_payloads))[:15]
            except Exception as e:
                print(f"[AI] Error generating AI payloads: {e}")
                # Fallback to basic payloads
        # Fallback to basic payloads
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "\"><script>alert('XSS')</script>",
            "';alert('XSS');//",
            "<svg/onload=alert('XSS')>"
        ]
    
    def _basic_context_detection(self, html, marker):
        """Basic context detection for XSS (simplified)"""
        if f"<script>{marker}</script>" in html:
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
