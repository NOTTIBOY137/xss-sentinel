import requests
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
