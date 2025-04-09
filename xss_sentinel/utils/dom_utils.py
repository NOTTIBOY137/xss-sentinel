from bs4 import BeautifulSoup
import re

def find_input_points(html):
    """Find potential input points in HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    input_points = []
    
    # Find form inputs
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action', '')
        method = form.get('method', 'get').lower()
        
        inputs = form.find_all(['input', 'textarea', 'select'])
        for input_field in inputs:
            field_type = input_field.get('type', '')
            field_name = input_field.get('name', '')
            
            # Skip submit buttons and hidden fields
            if field_type not in ['submit', 'button', 'hidden'] and field_name:
                input_points.append({
                    'type': 'form_input',
                    'form_method': method,
                    'form_action': action,
                    'name': field_name
                })
    
    # Find JavaScript event handlers that might process user input
    events = ['onclick', 'onchange', 'onkeyup', 'onkeydown', 'oninput']
    for event in events:
        for tag in soup.find_all(attrs={event: True}):
            input_points.append({
                'type': 'event_handler',
                'event': event,
                'tag': tag.name,
                'id': tag.get('id', ''),
                'handler_code': tag[event]
            })
    
    # Find potential DOM sinks
    js_sinks = [
        'document.write', 'innerHTML', 'outerHTML', 'insertAdjacentHTML',
        'eval', 'setTimeout', 'setInterval', 'location'
    ]
    
    scripts = soup.find_all('script')
    for script in scripts:
        script_content = script.string or ''
        for sink in js_sinks:
            if sink in script_content:
                # Found a potential DOM sink
                matches = re.findall(r'(\w+)\s*=\s*.*' + re.escape(sink), script_content)
                for match in matches:
                    input_points.append({
                        'type': 'dom_sink',
                        'sink': sink,
                        'variable': match
                    })
    
    return input_points

def extract_scripts(html):
    """Extract all JavaScript code from an HTML document"""
    soup = BeautifulSoup(html, 'html.parser')
    scripts = []
    
    # Extract <script> tags
    for script in soup.find_all('script'):
        if script.string:
            scripts.append({
                'type': 'script_tag',
                'content': script.string
            })
    
    # Extract inline event handlers
    for tag in soup.find_all(True):
        for attr in tag.attrs:
            if attr.startswith('on'):
                scripts.append({
                    'type': 'event_handler',
                    'event': attr,
                    'tag': tag.name,
                    'content': tag[attr]
                })
    
    return scripts

def extract_urls(html):
    """Extract all URLs from an HTML document"""
    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    
    # Find all tags with href, src, or action attributes
    for tag in soup.find_all(['a', 'img', 'script', 'link', 'iframe', 'form']):
        if tag.name == 'a' and tag.has_attr('href'):
            urls.append({
                'type': 'link',
                'url': tag['href'],
                'text': tag.text.strip()
            })
        elif tag.name == 'img' and tag.has_attr('src'):
            urls.append({
                'type': 'image',
                'url': tag['src'],
                'alt': tag.get('alt', '')
            })
        elif tag.name == 'script' and tag.has_attr('src'):
            urls.append({
                'type': 'script',
                'url': tag['src']
            })
        elif tag.name == 'link' and tag.has_attr('href'):
            urls.append({
                'type': 'stylesheet' if tag.get('rel') == ['stylesheet'] else 'link',
                'url': tag['href']
            })
        elif tag.name == 'iframe' and tag.has_attr('src'):
            urls.append({
                'type': 'iframe',
                'url': tag['src']
            })
        elif tag.name == 'form' and tag.has_attr('action'):
            urls.append({
                'type': 'form',
                'url': tag['action'],
                'method': tag.get('method', 'get').lower()
            })
    
    # Find URLs in inline styles
    style_url_pattern = re.compile(r'url\([\'"]?([^\'")]+)[\'"]?\)')
    for tag in soup.find_all(style=True):
        style_content = tag['style']
        for url in style_url_pattern.findall(style_content):
            urls.append({
                'type': 'style',
                'url': url
            })
    
    return urls
