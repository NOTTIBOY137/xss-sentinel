#!/usr/bin/env python3
"""
XSS Sentinel v2.0 Neural Engine - Quick Installation Test
Verifies that the neural engine components are properly installed
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def print_banner():
    try:
        print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║        XSS SENTINEL v2.0 - QUICK TEST                         ║
║                                                                ║
║     AI-Powered XSS Detection System - Installation Test       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")
    except UnicodeEncodeError:
        print("=" * 70)
        print("XSS SENTINEL v2.0 - QUICK TEST")
        print("AI-Powered XSS Detection System - Installation Test")
        print("=" * 70)

def test_imports():
    """Test that all modules can be imported"""
    print("\n[TEST] Testing Module Imports...")
    
    tests = [
        ("numpy", "NumPy"),
        ("sklearn", "Scikit-learn"),
        ("xss_sentinel.neural_engine.genetic_mutator", "Genetic Mutator"),
    ]
    
    results = {}
    for module_name, display_name in tests:
        try:
            __import__(module_name)
            print(f"   [OK] {display_name} - OK")
            results[display_name] = True
        except ImportError as e:
            print(f"   [FAIL] {display_name} - NOT FOUND")
            print(f"      Error: {e}")
            results[display_name] = False
    
    # Test optional neural dependencies
    print("\n[TEST] Testing Optional Neural Dependencies...")
    optional_tests = [
        ("torch", "PyTorch"),
        ("cv2", "OpenCV"),
    ]
    
    for module_name, display_name in optional_tests:
        try:
            __import__(module_name)
            print(f"   [OK] {display_name} - OK (Optional)")
            results[display_name] = True
        except ImportError:
            print(f"   [WARN] {display_name} - Not installed (Optional)")
            results[display_name] = False
    
    return results

def test_genetic_mutator():
    """Test genetic mutator functionality"""
    print("\n[TEST] Testing Genetic Mutator...")
    
    try:
        from xss_sentinel.neural_engine.genetic_mutator import GeneticPayloadMutator, PayloadGene
        
        # Test initialization
        mutator = GeneticPayloadMutator(population_size=10, mutation_rate=0.3)
        print("   [OK] Genetic Mutator initialized")
        
        # Test PayloadGene
        gene = PayloadGene(payload="<script>alert(1)</script>", fitness=0.5)
        print(f"   [OK] PayloadGene created: {gene.payload[:30]}...")
        
        # Test mutation operators
        test_payload = "<script>alert(1)</script>"
        mutated = mutator._case_mutation(test_payload)
        if mutated != test_payload:
            print("   [OK] Mutation operators working")
        else:
            print("   [WARN] Mutation operators may need testing")
        
        # Test fitness function
        def simple_fitness(payload: str) -> float:
            return 0.5 if 'alert' in payload else 0.1
        
        # Quick evolution test (small population, few generations)
        seeds = ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>']
        evolved = mutator.evolve_population(seeds, simple_fitness, generations=2)
        
        if len(evolved) > 0:
            print(f"   [OK] Evolution test successful - {len(evolved)} payloads evolved")
            print(f"      Best fitness: {evolved[0].fitness:.3f}")
        else:
            print("   [WARN] Evolution test completed but no results")
        
        return True
        
    except Exception as e:
        print(f"   [FAIL] Genetic Mutator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print_banner()
    
    print("[START] Starting XSS Sentinel v2.0 Neural Engine Quick Test...")
    print("=" * 70)
    
    # Test imports
    import_results = test_imports()
    
    # Test genetic mutator
    mutator_result = test_genetic_mutator()
    
    # Summary
    print("\n" + "=" * 70)
    print("[SUMMARY] TEST SUMMARY")
    print("=" * 70)
    
    core_ok = all(import_results.get(name, False) for name in ["NumPy", "Scikit-learn", "Genetic Mutator"])
    
    if core_ok and mutator_result:
        print("[OK] Core components: WORKING")
    else:
        print("[FAIL] Core components: ISSUES DETECTED")
    
    if import_results.get("PyTorch", False):
        print("[OK] Neural dependencies: AVAILABLE")
    else:
        print("[WARN] Neural dependencies: NOT INSTALLED (Optional)")
        print("   Install with: pip install torch torchvision")
    
    print("\n" + "=" * 70)
    
    if core_ok and mutator_result:
        print("[SUCCESS] Installation test PASSED!")
        print("\nNext steps:")
        print("   1. Run full demo: python examples/simple_demo.py")
        print("   2. Read documentation: README_NEURAL_ENGINE.md")
        print("   3. Start using the neural engine!")
        return 0
    else:
        print("[WARN] Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("   1. Install missing dependencies: pip install -r requirements.txt")
        print("   2. Check Python version: python --version (need 3.8+)")
        print("   3. Verify installation: python -c 'import xss_sentinel'")
        return 1

if __name__ == "__main__":
    sys.exit(main())
