import requests
from urllib.parse import urlparse, urljoin
import random
import time
import urllib3

# Disable SSL warnings for testing (remove in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Common User-Agent strings
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

def make_request(url, method="GET", data=None, headers=None, timeout=10, max_retries=3, follow_redirects=True):
    """Make an HTTP request with retry logic and random user agent"""
    if not headers:
        headers = {}
    
    # Add random User-Agent if not specified
    if 'User-Agent' not in headers:
        headers['User-Agent'] = random.choice(USER_AGENTS)
    
    # Add common headers to appear more like a browser
    if 'Accept' not in headers:
        headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    if 'Accept-Language' not in headers:
        headers['Accept-Language'] = 'en-US,en;q=0.5'
    
    session = requests.Session()
    
    # Configure session to allow insecure requests (careful with this in production!)
    session.verify = False
    
    for attempt in range(max_retries):
        try:
            if method.upper() == "GET":
                response = session.get(url, headers=headers, timeout=timeout, allow_redirects=follow_redirects)
            elif method.upper() == "POST":
                response = session.post(url, data=data, headers=headers, timeout=timeout, allow_redirects=follow_redirects)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle redirects manually if needed
            if not follow_redirects and response.is_redirect:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    if not redirect_url.startswith(('http://', 'https://')):
                        # Handle relative URLs
                        redirect_url = urljoin(url, redirect_url)
                    print(f"Redirected to: {redirect_url}")
                    return make_request(redirect_url, method, data, headers, timeout, max_retries)
            
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
