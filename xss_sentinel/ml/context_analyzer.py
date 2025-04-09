import re
from bs4 import BeautifulSoup, Comment

class ContextAnalyzer:
    def __init__(self):
        pass
    
    def identify_context(self, html, marker):
        """
        Identify the context in which a marker appears in HTML
        Returns one of: 'js', 'attribute', 'tag', 'html', 'url'
        """
        if not marker in html:
            return None
        
        # Parse HTML
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Search for marker in different contexts
            
            # 1. Check JavaScript context
            scripts = soup.find_all('script')
            for script in scripts:
                if marker in script.string:
                    return 'js'
            
            # Check event handlers
            event_pattern = re.compile(r'on\w+\s*=\s*["\'][^"\']*' + re.escape(marker))
            if event_pattern.search(html):
                return 'js'
            
            # 2. Check attribute context
            attr_pattern = re.compile(r'=\s*["\'][^"\']*' + re.escape(marker))
            if attr_pattern.search(html):
                return 'attribute'
            
            # 3. Check URL context (href, src, etc.)
            url_attrs = ['href', 'src', 'action', 'formaction']
            for tag in soup.find_all(lambda t: any(marker in t.get(a, '') for a in url_attrs)):
                for attr in url_attrs:
                    if attr in tag.attrs and marker in tag[attr]:
                        return 'url'
            
            # 4. Check tag context
            if re.search(r'<[^>]*' + re.escape(marker), html):
                return 'tag'
            
            # 5. Default to HTML context
            return 'html'
            
        except Exception as e:
            print(f"Error analyzing context: {e}")
            return 'html'  # Default fallback
    
    def extract_contexts(self, html):
        """
        Analyze an HTML document and extract all potential injection contexts
        Returns a dict of contexts and their locations
        """
        contexts = {
            'js': [],
            'attribute': [],
            'tag': [],
            'html': [],
            'url': []
        }
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # 1. Find JavaScript contexts
            # Script tags
            for script in soup.find_all('script'):
                contexts['js'].append({
                    'type': 'script_tag',
                    'content': script.string or ''
                })
            
            # Event handlers
            for tag in soup.find_all(lambda t: any(a.startswith('on') for a in t.attrs)):
                for attr in [a for a in tag.attrs if a.startswith('on')]:
                    contexts['js'].append({
                        'type': 'event_handler',
                        'tag': tag.name,
                        'attribute': attr,
                        'content': tag[attr]
                    })
            
            # 2. Find attribute contexts
            for tag in soup.find_all(True):  # All tags with attributes
                for attr, value in tag.attrs.items():
                    if attr.startswith('on'):
                        continue  # Already handled as JS
                    
                    if attr in ['href', 'src', 'action', 'formaction']:
                        # URL context
                        contexts['url'].append({
                            'tag': tag.name,
                            'attribute': attr,
                            'content': value
                        })
                    else:
                        # Regular attribute
                        contexts['attribute'].append({
                            'tag': tag.name,
                            'attribute': attr,
                            'content': value
                        })
            
            # 3. HTML context (text nodes)
            for text in soup.find_all(string=True):
                if not isinstance(text, Comment):
                    parent = text.parent.name if text.parent else None
                    if parent != 'script' and parent != 'style':
                        contexts['html'].append({
                            'parent_tag': parent,
                            'content': text
                        })
            
            return contexts
            
        except Exception as e:
            print(f"Error extracting contexts: {e}")
            return contexts
