"""
Integration Module - Connects Neural Engine to XSS Scanner
Seamlessly integrates all AI components into the existing scanner
"""

import sys
import os
from typing import List, Dict, Tuple, Optional
import numpy as np

# Import neural components
try:
    from .genetic_mutator import GeneticPayloadMutator, PayloadGene
    from .gan_payload_generator import GANPayloadGenerator
    from .reinforcement_learner import ReinforcementLearner
    NEURAL_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Neural Engine components not available: {e}")
    NEURAL_ENGINE_AVAILABLE = False


class NeuralEngineIntegration:
    """
    Main integration class that combines all neural components
    with the existing XSS Scanner
    """
    
    def __init__(self, enable_genetic=True, enable_gan=True, enable_rl=True,
                 genetic_config=None, gan_config=None, rl_config=None):
        """
        Initialize neural engine integration
        
        Args:
            enable_genetic: Enable genetic algorithm mutations
            enable_gan: Enable GAN-based payload generation
            enable_rl: Enable reinforcement learning optimization
            genetic_config: Configuration dict for genetic mutator
            gan_config: Configuration dict for GAN
            rl_config: Configuration dict for RL agent
        """
        if not NEURAL_ENGINE_AVAILABLE:
            raise ImportError("Neural Engine components are not available. "
                            "Please install required dependencies.")
        
        print("[INTEGRATION] Initializing Neural Engine Integration...")
        
        # Initialize components
        self.genetic_mutator = None
        self.gan_generator = None
        self.rl_agent = None
        
        if enable_genetic:
            try:
                genetic_config = genetic_config or {}
                self.genetic_mutator = GeneticPayloadMutator(**genetic_config)
                print("[INTEGRATION] Genetic Mutator loaded")
            except Exception as e:
                print(f"[WARN] Could not load Genetic Mutator: {e}")
        
        if enable_gan:
            try:
                gan_config = gan_config or {}
                self.gan_generator = GANPayloadGenerator(**gan_config)
                print("[INTEGRATION] GAN Generator loaded")
            except Exception as e:
                print(f"[WARN] Could not load GAN Generator: {e}")
        
        if enable_rl:
            try:
                rl_config = rl_config or {}
                self.rl_agent = ReinforcementLearner(**rl_config)
                print("[INTEGRATION] RL Agent loaded")
            except Exception as e:
                print(f"[WARN] Could not load RL Agent: {e}")
        
        # Success tracking for adaptive learning
        self.successful_payloads = []
        self.failed_payloads = []
        self.waf_bypass_patterns = {}
        
        print("[INTEGRATION] Neural Engine Integration ready!")
    
    def generate_advanced_payloads(self, base_payloads: List[str], 
                                  context: Dict,
                                  target_url: str,
                                  count: int = 50) -> List[str]:
        """
        Generate advanced payloads using all neural components
        
        Args:
            base_payloads: Seed payloads
            context: Context information from scanner
            target_url: Target URL being scanned
            count: Number of payloads to generate
        
        Returns:
            List of optimized payloads
        """
        print(f"[INTEGRATION] Generating {count} advanced payloads using Neural Engine...")
        
        all_payloads = set(base_payloads)
        
        # 1. Genetic Evolution
        if self.genetic_mutator and base_payloads:
            print("[INTEGRATION] Phase 1: Genetic Evolution")
            
            def fitness_func(payload):
                # Fitness based on context match and characteristics
                score = 0.0
                if context.get('context_type') == 'form_input':
                    if 'onerror' in payload or 'onload' in payload:
                        score += 0.3
                elif context.get('context_type') == 'url_parameter':
                    if 'javascript:' in payload:
                        score += 0.3
                
                # Reward novelty
                if payload not in base_payloads:
                    score += 0.2
                
                # Reward encodings
                if '%' in payload or '&#' in payload:
                    score += 0.1
                
                return min(score, 1.0)
            
            try:
                evolved = self.genetic_mutator.evolve_population(
                    base_payloads[:10],  # Use top 10 as seeds
                    fitness_func,
                    generations=5
                )
                
                # Add top evolved payloads
                for gene in evolved[:20]:
                    all_payloads.add(gene.payload)
                
                print(f"   Generated {len(evolved)} evolved payloads")
            except Exception as e:
                print(f"   [WARN] Genetic evolution failed: {e}")
        
        # 2. GAN Generation
        if self.gan_generator:
            print("[INTEGRATION] Phase 2: GAN Novel Generation")
            
            try:
                # If we have successful payloads, train GAN on them
                if self.successful_payloads and len(self.successful_payloads) > 20:
                    print(f"   Training GAN on {len(self.successful_payloads)} successful payloads...")
                    self.gan_generator.train(self.successful_payloads, epochs=30, batch_size=8)
                
                # Generate novel payloads
                novel_payloads = self.gan_generator.generate_payloads(count=15)
                all_payloads.update(novel_payloads)
                
                # Generate variations of best base payloads
                if base_payloads:
                    variations = self.gan_generator.generate_from_seed(
                        base_payloads[0], 
                        variations=10
                    )
                    all_payloads.update(variations)
                
                print(f"   Generated {len(novel_payloads) + 10} GAN payloads")
            except Exception as e:
                print(f"   [WARN] GAN generation failed: {e}")
        
        # 3. Reinforcement Learning Optimization
        if self.rl_agent:
            print("[INTEGRATION] Phase 3: RL Optimization")
            
            try:
                # Train agent if we have feedback data
                if self.successful_payloads and len(self.successful_payloads) > 10:
                    print(f"   Training RL agent on {len(self.successful_payloads)} samples...")
                    
                    def test_func(payload):
                        # Check against known successful patterns
                        similarity = any(self._similarity(payload, succ) > 0.7 
                                       for succ in self.successful_payloads)
                        return similarity, {}
                    
                    self.rl_agent.train(
                        self.successful_payloads[:10],
                        episodes=50,
                        max_steps=10,
                        test_function=test_func
                    )
                
                # Optimize base payloads
                optimized_payloads = []
                for payload in base_payloads[:10]:
                    optimized, _ = self.rl_agent.generate_optimal_payload(payload, max_steps=5)
                    optimized_payloads.append(optimized)
                
                all_payloads.update(optimized_payloads)
                print(f"   Generated {len(optimized_payloads)} RL-optimized payloads")
            except Exception as e:
                print(f"   [WARN] RL optimization failed: {e}")
        
        # Convert to list and limit to requested count
        final_payloads = list(all_payloads)[:count]
        
        print(f"[INTEGRATION] Total unique payloads generated: {len(final_payloads)}")
        return final_payloads
    
    def learn_from_result(self, payload: str, context: Dict, 
                         success: bool, details: Dict):
        """
        Learn from testing results (adaptive learning)
        
        Args:
            payload: The payload that was tested
            context: Context information
            success: Whether the payload succeeded
            details: Additional details about the result
        """
        if success:
            self.successful_payloads.append(payload)
            print(f"[INTEGRATION] Learning from SUCCESS: {payload[:50]}...")
            
            # Extract patterns
            waf_type = context.get('waf_type', 'unknown')
            if waf_type not in self.waf_bypass_patterns:
                self.waf_bypass_patterns[waf_type] = []
            self.waf_bypass_patterns[waf_type].append(payload)
        else:
            self.failed_payloads.append(payload)
        
        # Trigger retraining if enough new data
        if len(self.successful_payloads) % 20 == 0 and len(self.successful_payloads) > 20:
            print("[INTEGRATION] Accumulated enough data, triggering adaptive learning...")
            self._adaptive_retrain()
    
    def _adaptive_retrain(self):
        """Retrain models with accumulated successful payloads"""
        if not self.successful_payloads:
            return
        
        print("[INTEGRATION] Adaptive retraining with new successful payloads...")
        
        # Retrain GAN if available
        if self.gan_generator and len(self.successful_payloads) >= 20:
            try:
                self.gan_generator.train(
                    self.successful_payloads,
                    epochs=20,
                    batch_size=8
                )
            except Exception as e:
                print(f"[WARN] GAN retraining failed: {e}")
        
        # Additional RL training
        if self.rl_agent and len(self.successful_payloads) >= 10:
            try:
                self.rl_agent.train(
                    self.successful_payloads[:10],
                    episodes=30,
                    max_steps=8
                )
            except Exception as e:
                print(f"[WARN] RL retraining failed: {e}")
    
    def _similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings"""
        # Simple Jaccard similarity
        set1 = set(s1.lower().split())
        set2 = set(s2.lower().split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_statistics(self) -> Dict:
        """Get statistics about learning progress"""
        total_tested = len(self.successful_payloads) + len(self.failed_payloads)
        return {
            'successful_payloads': len(self.successful_payloads),
            'failed_payloads': len(self.failed_payloads),
            'success_rate': (len(self.successful_payloads) / total_tested
                           if total_tested > 0 else 0.0),
            'waf_types_encountered': len(self.waf_bypass_patterns),
            'genetic_enabled': self.genetic_mutator is not None,
            'gan_enabled': self.gan_generator is not None,
            'rl_enabled': self.rl_agent is not None,
        }
    
    def save_models(self, directory='neural_models'):
        """Save all trained models"""
        os.makedirs(directory, exist_ok=True)
        
        if self.gan_generator:
            try:
                self.gan_generator.save_model(os.path.join(directory, 'gan_model.pth'))
            except Exception as e:
                print(f"[WARN] Could not save GAN model: {e}")
        
        if self.rl_agent:
            try:
                self.rl_agent.save_model(os.path.join(directory, 'rl_model.pkl'))
            except Exception as e:
                print(f"[WARN] Could not save RL model: {e}")
        
        # Save successful payloads database
        import json
        try:
            with open(os.path.join(directory, 'success_db.json'), 'w') as f:
                json.dump({
                    'successful_payloads': self.successful_payloads,
                    'waf_bypass_patterns': self.waf_bypass_patterns
                }, f, indent=2)
        except Exception as e:
            print(f"[WARN] Could not save success database: {e}")
        
        print(f"[INTEGRATION] All models saved to {directory}/")
    
    def load_models(self, directory='neural_models'):
        """Load all trained models"""
        import json
        
        if self.gan_generator:
            gan_path = os.path.join(directory, 'gan_model.pth')
            if os.path.exists(gan_path):
                try:
                    self.gan_generator.load_model(gan_path)
                except Exception as e:
                    print(f"[WARN] Could not load GAN model: {e}")
        
        if self.rl_agent:
            rl_path = os.path.join(directory, 'rl_model.pkl')
            if os.path.exists(rl_path):
                try:
                    self.rl_agent.load_model(rl_path)
                except Exception as e:
                    print(f"[WARN] Could not load RL model: {e}")
        
        # Load successful payloads database
        db_path = os.path.join(directory, 'success_db.json')
        if os.path.exists(db_path):
            try:
                with open(db_path, 'r') as f:
                    data = json.load(f)
                    self.successful_payloads = data.get('successful_payloads', [])
                    self.waf_bypass_patterns = data.get('waf_bypass_patterns', {})
            except Exception as e:
                print(f"[WARN] Could not load success database: {e}")
        
        print(f"[INTEGRATION] All models loaded from {directory}/")


# ==================== SCANNER INTEGRATION PATCH ====================

def patch_scanner_with_neural_engine(scanner_class):
    """
    Decorator to patch existing XSS Scanner with Neural Engine
    
    Usage:
        from xss_sentinel.core.scanner import XSSScanner
        from xss_sentinel.neural_engine.integration import patch_scanner_with_neural_engine
        
        @patch_scanner_with_neural_engine
        class EnhancedXSSScanner(XSSScanner):
            pass
    """
    
    # Store original methods
    original_init = scanner_class.__init__
    
    def enhanced_init(self, *args, **kwargs):
        # Call original init
        original_init(self, *args, **kwargs)
        
        # Add neural engine
        try:
            self.neural_engine = NeuralEngineIntegration(
                enable_genetic=kwargs.get('enable_genetic', True),
                enable_gan=kwargs.get('enable_gan', True),
                enable_rl=kwargs.get('enable_rl', True)
            )
            self.use_neural_engine = True
            print("[INTEGRATION] Neural Engine integrated into scanner!")
        except Exception as e:
            print(f"[WARN] Could not initialize Neural Engine: {e}")
            self.use_neural_engine = False
    
    # Patch __init__
    scanner_class.__init__ = enhanced_init
    
    # Patch _get_payloads if it exists
    if hasattr(scanner_class, '_get_payloads'):
        original_get_payloads = scanner_class._get_payloads
        
        def enhanced_get_payloads(self, context, point=None):
            # Get base payloads
            base_payloads = original_get_payloads(self, context, point)
            
            # Enhance with neural engine if available
            if hasattr(self, 'use_neural_engine') and self.use_neural_engine:
                try:
                    enhanced_payloads = self.neural_engine.generate_advanced_payloads(
                        base_payloads,
                        context if isinstance(context, dict) else {'context_type': context},
                        point.get('url') if point else getattr(self, 'target_url', ''),
                        count=30
                    )
                    return enhanced_payloads
                except Exception as e:
                    print(f"[WARN] Neural engine error: {e}")
                    return base_payloads
            
            return base_payloads
        
        scanner_class._get_payloads = enhanced_get_payloads
    
    # Patch _test_injection_point if it exists
    if hasattr(scanner_class, '_test_injection_point'):
        original_test_injection = scanner_class._test_injection_point
        
        def enhanced_test_injection(self, point):
            # Call original test
            result = original_test_injection(self, point)
            
            # Learn from result if neural engine available
            if hasattr(self, 'use_neural_engine') and self.use_neural_engine:
                try:
                    # Unpack result (adjust based on actual return format)
                    if isinstance(result, tuple) and len(result) >= 3:
                        vulnerable = result[0]
                        context = result[1] if len(result) > 1 else {}
                        payload = result[2] if len(result) > 2 else None
                        verified = result[3] if len(result) > 3 else False
                        evidence = result[4] if len(result) > 4 else {}
                        
                        if payload:
                            self.neural_engine.learn_from_result(
                                payload,
                                context if isinstance(context, dict) else {'context_type': context},
                                vulnerable and verified,
                                {'evidence': evidence}
                            )
                except Exception as e:
                    print(f"[WARN] Learning error: {e}")
            
            return result
        
        scanner_class._test_injection_point = enhanced_test_injection
    
    return scanner_class
