import requests
import re
import json
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


class JSCrawler:
    """Crawler for analyzing JavaScript files for DOM XSS vulnerabilities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'XSS-Sentinel/1.0 (JS Crawler)'
        })
        
        # Patterns for DOM XSS vulnerabilities
        self.dom_xss_patterns = [
            r'document\.write\s*\(\s*[^)]*\)',
            r'document\.writeln\s*\(\s*[^)]*\)',
            r'innerHTML\s*=\s*[^;]*',
            r'outerHTML\s*=\s*[^;]*',
            r'insertAdjacentHTML\s*\(\s*[^)]*\)',
            r'eval\s*\(\s*[^)]*\)',
            r'setTimeout\s*\(\s*[^)]*\)',
            r'setInterval\s*\(\s*[^)]*\)',
            r'Function\s*\(\s*[^)]*\)',
            r'location\.href\s*=\s*[^;]*',
            r'location\.assign\s*\(\s*[^)]*\)',
            r'location\.replace\s*\(\s*[^)]*\)'
        ]
        
        # Sources of user input
        self.user_input_sources = [
            r'location\.href',
            r'location\.search',
            r'location\.hash',
            r'document\.URL',
            r'document\.documentURI',
            r'document\.baseURI',
            r'document\.referrer',
            r'window\.name',
            r'history\.state',
            r'localStorage\.getItem',
            r'sessionStorage\.getItem',
            r'getParameter',
            r'getQueryString',
            r'URLSearchParams'
        ]
    
    def analyze_js_file(self, js_url):
        """Analyze a JavaScript file for DOM XSS vulnerabilities"""
        try:
            response = self.session.get(js_url, timeout=10)
            response.raise_for_status()
            
            js_content = response.text
            vulnerabilities = []
            
            # Check for dangerous patterns
            for pattern in self.dom_xss_patterns:
                matches = re.finditer(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    line_num = js_content[:match.start()].count('\n') + 1
                    vulnerabilities.append({
                        'type': 'DOM_XSS_PATTERN',
                        'pattern': pattern,
                        'match': match.group(),
                        'line': line_num,
                        'severity': 'high'
                    })
            
            # Check for user input sources
            for pattern in self.user_input_sources:
                matches = re.finditer(pattern, js_content, re.IGNORECASE)
                for match in matches:
                    line_num = js_content[:match.start()].count('\n') + 1
                    vulnerabilities.append({
                        'type': 'USER_INPUT_SOURCE',
                        'pattern': pattern,
                        'match': match.group(),
                        'line': line_num,
                        'severity': 'medium'
                    })
            
            # Check for potential XSS sinks
            xss_sinks = self._find_xss_sinks(js_content)
            vulnerabilities.extend(xss_sinks)
            
            return {
                'url': js_url,
                'vulnerabilities': vulnerabilities,
                'total_vulnerabilities': len(vulnerabilities)
            }
            
        except Exception as e:
            return {
                'url': js_url,
                'error': str(e),
                'vulnerabilities': [],
                'total_vulnerabilities': 0
            }
    
    def _find_xss_sinks(self, js_content):
        """Find potential XSS sinks in JavaScript code"""
        sinks = []
        
        # Common XSS sink patterns
        sink_patterns = [
            (r'innerHTML\s*=\s*([^;]+)', 'innerHTML assignment'),
            (r'outerHTML\s*=\s*([^;]+)', 'outerHTML assignment'),
            (r'document\.write\s*\(\s*([^)]+)\)', 'document.write'),
            (r'document\.writeln\s*\(\s*([^)]+)\)', 'document.writeln'),
            (r'insertAdjacentHTML\s*\(\s*[^,]+,\s*([^)]+)\)', 'insertAdjacentHTML'),
            (r'eval\s*\(\s*([^)]+)\)', 'eval function'),
            (r'setTimeout\s*\(\s*([^,]+)', 'setTimeout'),
            (r'setInterval\s*\(\s*([^,]+)', 'setInterval')
        ]
        
        for pattern, description in sink_patterns:
            matches = re.finditer(pattern, js_content, re.IGNORECASE)
            for match in matches:
                line_num = js_content[:match.start()].count('\n') + 1
                sinks.append({
                    'type': 'XSS_SINK',
                    'description': description,
                    'match': match.group(),
                    'line': line_num,
                    'severity': 'high'
                })
        
        return sinks


class SPACrawler:
    """Crawler for Single Page Application specific vulnerabilities"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'XSS-Sentinel/1.0 (SPA Crawler)'
        })
        
    def crawl_spa(self, spa_url):
        """Analyze a Single Page Application for vulnerabilities"""
        try:
            response = self.session.get(spa_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'url': spa_url,
                'spa_indicators': [],
                'vulnerabilities': [],
                'javascript_files': [],
                'api_endpoints': []
            }
            
            # Check for SPA indicators
            analysis['spa_indicators'] = self._detect_spa_indicators(soup)
            
            # Extract JavaScript files
            js_files = soup.find_all('script', src=True)
            for script in js_files:
                js_url = urljoin(spa_url, script['src'])
                analysis['javascript_files'].append(js_url)
            
            # Look for API endpoints in JavaScript
            inline_scripts = soup.find_all('script')
            for script in inline_scripts:
                if script.string:
                    api_endpoints = self._extract_api_endpoints(script.string)
                    analysis['api_endpoints'].extend(api_endpoints)
            
            # Check for common SPA vulnerabilities
            analysis['vulnerabilities'] = self._check_spa_vulnerabilities(soup, spa_url)
            
            return analysis
            
        except Exception as e:
            return {
                'url': spa_url,
                'error': str(e),
                'spa_indicators': [],
                'vulnerabilities': [],
                'javascript_files': [],
                'api_endpoints': []
            }
    
    def _detect_spa_indicators(self, soup):
        """Detect indicators that suggest this is a SPA"""
        indicators = []
        
        # Check for common SPA frameworks
        if soup.find('div', {'id': 'app'}) or soup.find('div', {'id': 'root'}):
            indicators.append('Vue.js/React root element')
        
        if soup.find('div', {'ng-app': True}):
            indicators.append('Angular.js application')
        
        if soup.find('div', {'data-reactroot': True}):
            indicators.append('React application')
        
        # Check for SPA routing patterns
        if soup.find('a', href=lambda x: x and x.startswith('#')):
            indicators.append('Hash-based routing')
        
        # Check for client-side routing libraries
        script_srcs = [script.get('src', '') for script in soup.find_all('script', src=True)]
        spa_libs = ['vue', 'react', 'angular', 'ember', 'backbone', 'router']
        for lib in spa_libs:
            if any(lib in src.lower() for src in script_srcs):
                indicators.append(f'{lib.title()} framework detected')
        
        return indicators
    
    def _extract_api_endpoints(self, js_content):
        """Extract potential API endpoints from JavaScript code"""
        endpoints = []
        
        # Common API endpoint patterns
        patterns = [
            r'["\'](/api/[^"\']+)["\']',
            r'["\'](/v\d+/[^"\']+)["\']',
            r'["\'](/rest/[^"\']+)["\']',
            r'["\'](/graphql[^"\']*)["\']',
            r'fetch\s*\(\s*["\']([^"\']+)["\']',
            r'axios\.[a-z]+\s*\(\s*["\']([^"\']+)["\']',
            r'\.ajax\s*\(\s*{\s*url\s*:\s*["\']([^"\']+)["\']'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, js_content, re.IGNORECASE)
            for match in matches:
                endpoint = match.group(1)
                if endpoint not in endpoints:
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _check_spa_vulnerabilities(self, soup, url):
        """Check for common SPA vulnerabilities"""
        vulnerabilities = []
        
        # Check for exposed sensitive data in JavaScript
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Check for hardcoded API keys, tokens, etc.
                sensitive_patterns = [
                    r'["\'](api_key|api_token|access_token|secret_key)["\']\s*:\s*["\'][^"\']+["\']',
                    r'["\'](password|secret|key)["\']\s*:\s*["\'][^"\']+["\']',
                    r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',
                    r'sk_[A-Za-z0-9]+',
                    r'pk_[A-Za-z0-9]+'
                ]
                
                for pattern in sensitive_patterns:
                    if re.search(pattern, script.string, re.IGNORECASE):
                        vulnerabilities.append({
                            'type': 'EXPOSED_SENSITIVE_DATA',
                            'description': 'Sensitive data found in client-side code',
                            'severity': 'high',
                            'location': 'inline script'
                        })
        
        # Check for client-side validation only
        forms = soup.find_all('form')
        for form in forms:
            inputs = form.find_all(['input', 'textarea'])
            for input_tag in inputs:
                if input_tag.get('pattern') or input_tag.get('maxlength'):
                    vulnerabilities.append({
                        'type': 'CLIENT_SIDE_VALIDATION_ONLY',
                        'description': 'Form relies only on client-side validation',
                        'severity': 'medium',
                        'location': f'form input: {input_tag.get("name", "unnamed")}'
                    })
        
        return vulnerabilities 