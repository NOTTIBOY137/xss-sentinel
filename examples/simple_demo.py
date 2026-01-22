#!/usr/bin/env python3
"""
XSS Sentinel v2.0 Neural Engine - Simple Demo
Demonstrates basic functionality of the neural engine components
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def print_banner():
    print("=" * 70)
    print("XSS SENTINEL v2.0 - SIMPLE DEMO")
    print("AI-Powered XSS Detection System")
    print("=" * 70)

def demo_genetic_mutator():
    """Demo genetic payload evolution"""
    print("\n[DEMO 1] Genetic Payload Evolution")
    print("-" * 70)
    
    try:
        from xss_sentinel.neural_engine.genetic_mutator import GeneticPayloadMutator
        
        # Initialize mutator
        mutator = GeneticPayloadMutator(population_size=20, mutation_rate=0.3)
        
        # Seed payloads
        seeds = [
            '<script>alert(1)</script>',
            '<img src=x onerror=alert(1)>',
            '<svg onload=alert(1)>',
        ]
        
        # Fitness function
        def fitness(payload: str) -> float:
            score = 0.0
            if 'alert' in payload:
                score += 0.3
            if any(tag in payload for tag in ['svg', 'iframe', 'object']):
                score += 0.3
            if '%' in payload or '&#' in payload:
                score += 0.4
            return min(score, 1.0)
        
        # Evolve
        print("Evolving payloads (2 generations)...")
        evolved = mutator.evolve_population(seeds, fitness, generations=2)
        
        print("\nTop 5 Evolved Payloads:")
        for i, gene in enumerate(evolved[:5], 1):
            print(f"  {i}. Fitness: {gene.fitness:.3f} | {gene.payload[:60]}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Genetic mutator demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_integration():
    """Demo neural engine integration"""
    print("\n[DEMO 2] Neural Engine Integration")
    print("-" * 70)
    
    try:
        from xss_sentinel.neural_engine.integration import NeuralEngineIntegration
        
        # Initialize integration (without GAN to avoid PyTorch dependency issues)
        engine = NeuralEngineIntegration(
            enable_genetic=True,
            enable_gan=False,  # Skip GAN for quick demo
            enable_rl=True
        )
        
        # Base payloads
        base_payloads = [
            '<script>alert(1)</script>',
            '<img src=x onerror=alert(1)>',
        ]
        
        # Context
        context = {
            'context_type': 'form_input',
            'waf_type': 'cloudflare'
        }
        
        # Generate advanced payloads
        print("Generating advanced payloads...")
        advanced = engine.generate_advanced_payloads(
            base_payloads,
            context,
            'https://example.com',
            count=10
        )
        
        print(f"\nGenerated {len(advanced)} advanced payloads:")
        for i, payload in enumerate(advanced[:5], 1):
            print(f"  {i}. {payload[:60]}")
        
        # Simulate learning
        print("\nSimulating adaptive learning...")
        engine.learn_from_result(advanced[0], context, success=True, details={})
        engine.learn_from_result(advanced[1], context, success=False, details={})
        
        # Get statistics
        stats = engine.get_statistics()
        print("\nLearning Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Integration demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all demos"""
    print_banner()
    
    print("\nThis demo showcases the core neural engine components.")
    print("Note: GAN features require PyTorch and may be skipped if not available.\n")
    
    results = []
    
    # Demo 1: Genetic Mutator
    results.append(("Genetic Mutator", demo_genetic_mutator()))
    
    # Demo 2: Integration
    results.append(("Integration", demo_integration()))
    
    # Summary
    print("\n" + "=" * 70)
    print("[SUMMARY] DEMO RESULTS")
    print("=" * 70)
    
    for name, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n[SUCCESS] All demos completed successfully!")
        print("\nNext steps:")
        print("  1. Read README_NEURAL_ENGINE.md for full documentation")
        print("  2. Try the complete demo: python examples/complete_demo.py")
        print("  3. Integrate with your scanner using integration.py")
    else:
        print("\n[WARN] Some demos failed. Check errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
