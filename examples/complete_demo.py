#!/usr/bin/env python3
"""
XSS Sentinel v2.0 Neural Engine - Complete Demo
Demonstrates all neural engine components working together
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def print_banner():
    print("=" * 70)
    print("XSS SENTINEL v2.0 - COMPLETE DEMO")
    print("AI-Powered XSS Detection System - Full Feature Showcase")
    print("=" * 70)

def demo_genetic_mutator():
    """Demo 1: Genetic Payload Evolution"""
    print("\n[DEMO 1] Genetic Payload Evolution")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.genetic_mutator import GeneticPayloadMutator
    
    mutator = GeneticPayloadMutator(population_size=30, mutation_rate=0.3)
    
    seeds = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
    ]
    
    def fitness(payload: str) -> float:
        score = 0.0
        if 'alert' in payload:
            score += 0.3
        if any(tag in payload for tag in ['svg', 'iframe', 'object']):
            score += 0.3
        if '%' in payload or '&#' in payload:
            score += 0.4
        return min(score, 1.0)
    
    print("Evolving payloads (3 generations)...")
    evolved = mutator.evolve_population(seeds, fitness, generations=3)
    
    print(f"\nTop 5 Evolved Payloads:")
    for i, gene in enumerate(evolved[:5], 1):
        print(f"  {i}. Fitness: {gene.fitness:.3f} | {gene.payload[:60]}")
    
    return True

def demo_gan_generator():
    """Demo 2: GAN Payload Generation"""
    print("\n[DEMO 2] GAN Novel Payload Generation")
    print("-" * 70)
    
    try:
        from xss_sentinel.neural_engine.gan_payload_generator import GANPayloadGenerator
        
        gan = GANPayloadGenerator(latent_dim=100, hidden_dim=128)
        
        print("Generating novel payloads...")
        novel_payloads = gan.generate_payloads(count=5)
        
        print(f"\nGenerated {len(novel_payloads)} novel payloads:")
        for i, payload in enumerate(novel_payloads, 1):
            print(f"  {i}. {payload[:60]}")
        
        return True
    except ImportError:
        print("[SKIP] PyTorch not available. Skipping GAN demo.")
        return True

def demo_reinforcement_learner():
    """Demo 3: Reinforcement Learning Optimization"""
    print("\n[DEMO 3] Reinforcement Learning Optimization")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.reinforcement_learner import ReinforcementLearner
    
    agent = ReinforcementLearner(learning_rate=0.1, epsilon=1.0)
    
    # Mock test function
    def mock_test(payload: str):
        encoding_score = payload.count('%') + payload.count('&#')
        success = encoding_score > 3 or 'svg' in payload.lower()
        return success, {'encoding_score': encoding_score}
    
    seed_payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
    ]
    
    print("Training RL agent (50 episodes)...")
    agent.train(seed_payloads, episodes=50, max_steps=10, test_function=mock_test)
    
    print("\nGenerating optimized payload...")
    optimized, history = agent.generate_optimal_payload('<script>alert(1)</script>', max_steps=5)
    
    print(f"Optimized Payload: {optimized[:60]}")
    print(f"Transformations: {len(history)}")
    
    return True

def demo_integration():
    """Demo 4: Neural Engine Integration"""
    print("\n[DEMO 4] Neural Engine Integration")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.integration import NeuralEngineIntegration
    
    engine = NeuralEngineIntegration(
        enable_genetic=True,
        enable_gan=False,  # Skip for faster demo
        enable_rl=True
    )
    
    base_payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
    ]
    
    context = {
        'context_type': 'form_input',
        'waf_type': 'cloudflare'
    }
    
    print("Generating advanced payloads using all components...")
    advanced = engine.generate_advanced_payloads(
        base_payloads,
        context,
        'https://example.com',
        count=15
    )
    
    print(f"\nGenerated {len(advanced)} advanced payloads:")
    for i, payload in enumerate(advanced[:5], 1):
        print(f"  {i}. {payload[:60]}")
    
    # Simulate learning
    print("\nSimulating adaptive learning...")
    engine.learn_from_result(advanced[0], context, success=True, details={})
    engine.learn_from_result(advanced[1], context, success=False, details={})
    
    stats = engine.get_statistics()
    print("\nLearning Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return True

def demo_waf_fingerprinter():
    """Demo 5: WAF Fingerprinting"""
    print("\n[DEMO 5] WAF Fingerprinting")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.waf_fingerprinter import WAFFingerprinter
    
    fingerprinter = WAFFingerprinter()
    
    print("Fingerprinting WAF (mock test)...")
    # Note: This is a mock - real fingerprinting requires network access
    result = {
        'detected_waf': 'cloudflare',
        'confidence': 0.85,
        'bypass_strategies': ['encoding_chain', 'case_mutation']
    }
    
    print(f"Detected WAF: {result['detected_waf']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Bypass Strategies: {result['bypass_strategies']}")
    
    print("\nGenerating bypass payloads...")
    bypass_payloads = fingerprinter.generate_bypass_payloads(
        '<script>alert(1)</script>',
        'cloudflare'
    )
    
    print(f"Generated {len(bypass_payloads)} bypass payloads:")
    for i, payload in enumerate(bypass_payloads[:3], 1):
        print(f"  {i}. {payload[:60]}")
    
    return True

def demo_context_predictor():
    """Demo 6: Context Prediction"""
    print("\n[DEMO 6] Context-Aware Payload Synthesis")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.context_predictor import ContextPredictor
    
    predictor = ContextPredictor()
    
    html = '<div class="search"><input value="XSS_TEST_123" name="q"></div>'
    
    print("Analyzing injection context...")
    context = predictor.analyze_context(html, "XSS_TEST_123")
    
    print(f"\nContext Analysis:")
    print(f"  Type: {context.context_type}")
    print(f"  Confidence: {context.confidence:.2f}")
    print(f"  Filters: {context.filters_detected}")
    print(f"  Encodings: {context.encoding_required}")
    
    print("\nGenerating context-aware payloads...")
    payloads = predictor.generate_context_payloads(context, count=3)
    
    print(f"Generated {len(payloads)} context-aware payloads:")
    for i, payload in enumerate(payloads, 1):
        print(f"  {i}. {payload[:60]}")
    
    return True

def demo_distributed_swarm():
    """Demo 7: Distributed Swarm (simulated)"""
    print("\n[DEMO 7] Distributed Swarm Coordination")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.distributed_swarm import DistributedSwarmCoordinator
    
    coordinator = DistributedSwarmCoordinator(max_workers=3)
    
    print("Registering workers...")
    for i in range(3):
        coordinator.register_worker(f'worker_{i}')
    
    print(f"Registered {len(coordinator.workers)} workers")
    
    print("\nSubmitting scan job...")
    job_id = coordinator.submit_scan_job(
        target_url='https://example.com/search',
        injection_points=[
            {'type': 'url_param', 'param_name': 'q'},
        ],
        payloads=['<script>alert(1)</script>'] * 5
    )
    
    print(f"Job ID: {job_id}")
    print(f"Total tasks: {coordinator.stats['total_tasks']}")
    
    progress = coordinator.get_progress()
    print(f"Progress: {progress['progress_percent']:.1f}%")
    
    return True

def demo_blind_xss():
    """Demo 8: Blind XSS Monitor"""
    print("\n[DEMO 8] Blind XSS Monitor")
    print("-" * 70)
    
    from xss_sentinel.neural_engine.blind_xss_monitor import BlindXSSMonitor
    
    monitor = BlindXSSMonitor(
        callback_domain='your-server.com',
        callback_port=8888
    )
    
    print("Generating blind XSS payloads...")
    payload1 = monitor.generate_payload(
        target_url='https://example.com/comment',
        injection_point='comment_field',
        payload_type='advanced',
        tags=['comment-section']
    )
    
    print(f"Generated Payload ID: {payload1.payload_id}")
    print(f"Callback URL: {payload1.callback_url}")
    print(f"Payload Preview: {payload1.payload[:80]}...")
    
    stats = monitor.get_statistics()
    print(f"\nMonitor Statistics:")
    print(f"  Active Payloads: {stats['active_payloads']}")
    print(f"  Callbacks Received: {stats['total_callbacks']}")
    
    return True

def main():
    """Run all demos"""
    print_banner()
    
    print("\nThis complete demo showcases all 8 neural engine components.")
    print("Note: Some components require optional dependencies (PyTorch, Selenium, aiohttp).")
    print("Components will gracefully degrade if dependencies are missing.\n")
    
    demos = [
        ("Genetic Mutator", demo_genetic_mutator),
        ("GAN Generator", demo_gan_generator),
        ("Reinforcement Learner", demo_reinforcement_learner),
        ("Integration Engine", demo_integration),
        ("WAF Fingerprinter", demo_waf_fingerprinter),
        ("Context Predictor", demo_context_predictor),
        ("Distributed Swarm", demo_distributed_swarm),
        ("Blind XSS Monitor", demo_blind_xss),
    ]
    
    results = []
    start_time = time.time()
    
    for name, demo_func in demos:
        try:
            result = demo_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] {name} demo failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    elapsed = time.time() - start_time
    
    # Summary
    print("\n" + "=" * 70)
    print("[SUMMARY] COMPLETE DEMO RESULTS")
    print("=" * 70)
    
    for name, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {name}")
    
    all_passed = all(result[1] for result in results)
    
    print(f"\nTotal Time: {elapsed:.2f} seconds")
    print(f"Components Tested: {len(results)}")
    print(f"Success Rate: {sum(1 for r in results if r[1])}/{len(results)}")
    
    if all_passed:
        print("\n[SUCCESS] All demos completed successfully!")
        print("\nNext steps:")
        print("  1. Read full documentation: README_NEURAL_ENGINE.md")
        print("  2. Run tests: python -m pytest tests/test_neural_engine.py")
        print("  3. Integrate with your scanner using integration.py")
        print("  4. Deploy with Docker: docker-compose up")
    else:
        print("\n[WARN] Some demos failed. Check errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
