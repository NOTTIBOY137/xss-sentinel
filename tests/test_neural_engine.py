"""
Comprehensive Test Suite for XSS Sentinel v2.0 Neural Engine
Tests all neural engine components
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xss_sentinel.neural_engine.genetic_mutator import GeneticPayloadMutator, PayloadGene
from xss_sentinel.neural_engine.gan_payload_generator import GANPayloadGenerator
from xss_sentinel.neural_engine.reinforcement_learner import ReinforcementLearner
from xss_sentinel.neural_engine.integration import NeuralEngineIntegration
from xss_sentinel.neural_engine.distributed_swarm import DistributedSwarmCoordinator
from xss_sentinel.neural_engine.waf_fingerprinter import WAFFingerprinter
from xss_sentinel.neural_engine.visual_xss_detector import VisualXSSDetector
from xss_sentinel.neural_engine.blind_xss_monitor import BlindXSSMonitor
from xss_sentinel.neural_engine.context_predictor import ContextPredictor


class TestGeneticMutator(unittest.TestCase):
    """Test Genetic Payload Mutator"""
    
    def setUp(self):
        self.mutator = GeneticPayloadMutator(population_size=20, mutation_rate=0.3)
    
    def test_initialization(self):
        """Test mutator initialization"""
        self.assertIsNotNone(self.mutator)
        self.assertEqual(self.mutator.population_size, 20)
        self.assertEqual(self.mutator.mutation_rate, 0.3)
    
    def test_payload_gene(self):
        """Test PayloadGene creation"""
        gene = PayloadGene(payload="<script>alert(1)</script>", fitness=0.5)
        self.assertEqual(gene.payload, "<script>alert(1)</script>")
        self.assertEqual(gene.fitness, 0.5)
        self.assertIsNotNone(gene.hash)
    
    def test_mutation_operators(self):
        """Test mutation operators"""
        test_payload = "<script>alert(1)</script>"
        
        # Test case mutation
        mutated = self.mutator._case_mutation(test_payload)
        self.assertNotEqual(mutated, test_payload)
        
        # Test encoding mutation
        encoded = self.mutator._encoding_mutation(test_payload)
        self.assertIsInstance(encoded, str)
    
    def test_evolution(self):
        """Test population evolution"""
        seeds = ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>']
        
        def fitness_func(payload: str) -> float:
            return 0.5 if 'alert' in payload else 0.1
        
        evolved = self.mutator.evolve_population(seeds, fitness_func, generations=2)
        self.assertGreater(len(evolved), 0)
        self.assertGreaterEqual(evolved[0].fitness, 0.0)


class TestGANGenerator(unittest.TestCase):
    """Test GAN Payload Generator"""
    
    def setUp(self):
        try:
            self.gan = GANPayloadGenerator(latent_dim=100, hidden_dim=128)
        except ImportError:
            self.skipTest("PyTorch not available")
    
    def test_initialization(self):
        """Test GAN initialization"""
        self.assertIsNotNone(self.gan)
        self.assertIsNotNone(self.gan.generator)
        self.assertIsNotNone(self.gan.discriminator)
    
    def test_payload_generation(self):
        """Test payload generation"""
        payloads = self.gan.generate_payloads(count=5)
        self.assertEqual(len(payloads), 5)
        self.assertTrue(all(isinstance(p, str) for p in payloads))


class TestReinforcementLearner(unittest.TestCase):
    """Test Reinforcement Learning Agent"""
    
    def setUp(self):
        self.rl = ReinforcementLearner(learning_rate=0.1, epsilon=1.0)
    
    def test_initialization(self):
        """Test RL agent initialization"""
        self.assertIsNotNone(self.rl)
        self.assertIsNotNone(self.rl.env)
        self.assertEqual(len(self.rl.env.actions), 15)
    
    def test_action_selection(self):
        """Test action selection"""
        state = self.rl.env.get_state("<script>alert(1)</script>")
        action = self.rl.select_action(state, training=True)
        self.assertGreaterEqual(action, 0)
        self.assertLess(action, len(self.rl.env.actions))
    
    def test_q_learning(self):
        """Test Q-learning update"""
        state = self.rl.env.get_state("<script>alert(1)</script>")
        next_state = self.rl.env.get_state("<script>alert(2)</script>")
        
        self.rl.learn(state, 0, 10.0, next_state, True)
        # Q-value should be updated
        state_key = self.rl._state_to_key(state)
        self.assertIn(state_key, self.rl.q_table)


class TestIntegration(unittest.TestCase):
    """Test Neural Engine Integration"""
    
    def setUp(self):
        try:
            self.integration = NeuralEngineIntegration(
                enable_genetic=True,
                enable_gan=False,  # Skip GAN for faster tests
                enable_rl=True
            )
        except ImportError:
            self.skipTest("Neural engine components not available")
    
    def test_initialization(self):
        """Test integration initialization"""
        self.assertIsNotNone(self.integration)
        self.assertIsNotNone(self.integration.genetic_mutator)
        self.assertIsNotNone(self.integration.rl_agent)
    
    def test_payload_generation(self):
        """Test advanced payload generation"""
        base_payloads = ['<script>alert(1)</script>']
        context = {'context_type': 'form_input'}
        
        advanced = self.integration.generate_advanced_payloads(
            base_payloads,
            context,
            'https://example.com',
            count=10
        )
        
        self.assertGreater(len(advanced), 0)
    
    def test_learning(self):
        """Test adaptive learning"""
        context = {'context_type': 'form_input'}
        self.integration.learn_from_result(
            '<script>alert(1)</script>',
            context,
            success=True,
            details={}
        )
        
        stats = self.integration.get_statistics()
        self.assertEqual(stats['successful_payloads'], 1)


class TestWAFFingerprinter(unittest.TestCase):
    """Test WAF Fingerprinter"""
    
    def setUp(self):
        self.fingerprinter = WAFFingerprinter()
    
    def test_initialization(self):
        """Test fingerprinter initialization"""
        self.assertIsNotNone(self.fingerprinter)
        self.assertGreater(len(self.fingerprinter.waf_signatures), 0)
    
    def test_bypass_generation(self):
        """Test bypass payload generation"""
        base_payload = '<script>alert(1)</script>'
        bypass_payloads = self.fingerprinter.generate_bypass_payloads(
            base_payload,
            'cloudflare'
        )
        
        self.assertGreater(len(bypass_payloads), 0)


class TestContextPredictor(unittest.TestCase):
    """Test Context Predictor"""
    
    def setUp(self):
        self.predictor = ContextPredictor()
    
    def test_initialization(self):
        """Test predictor initialization"""
        self.assertIsNotNone(self.predictor)
        self.assertGreater(len(self.predictor.context_types), 0)
    
    def test_context_prediction(self):
        """Test context prediction"""
        html = '<div><input value="test"></div>'
        injection_point = {'type': 'form_input'}
        
        prediction = self.predictor.predict_context(html, injection_point)
        self.assertIn('context_type', prediction)
        self.assertIn('confidence', prediction)
        self.assertIn('suggested_payloads', prediction)


class TestDistributedSwarm(unittest.TestCase):
    """Test Distributed Swarm Coordinator"""
    
    def setUp(self):
        self.coordinator = DistributedSwarmCoordinator(max_workers=5)
    
    def test_initialization(self):
        """Test coordinator initialization"""
        self.assertIsNotNone(self.coordinator)
        self.assertEqual(self.coordinator.max_workers, 5)
    
    def test_worker_registration(self):
        """Test worker registration"""
        worker = self.coordinator.register_worker('test_worker')
        self.assertIsNotNone(worker)
        self.assertEqual(worker.node_id, 'test_worker')
        self.assertIn('test_worker', self.coordinator.workers)


class TestBlindXSSMonitor(unittest.TestCase):
    """Test Blind XSS Monitor"""
    
    def setUp(self):
        self.monitor = BlindXSSMonitor(
            callback_domain='test.com',
            callback_port=8888
        )
    
    def test_initialization(self):
        """Test monitor initialization"""
        self.assertIsNotNone(self.monitor)
        self.assertEqual(self.monitor.callback_domain, 'test.com')
    
    def test_payload_generation(self):
        """Test payload generation"""
        payload = self.monitor.generate_payload(
            target_url='https://example.com',
            injection_point='comment',
            payload_type='simple'
        )
        
        self.assertIsNotNone(payload)
        self.assertIn('payload', payload.payload)
        self.assertIn('callback', payload.callback_url)


class TestVisualDetector(unittest.TestCase):
    """Test Visual XSS Detector"""
    
    def setUp(self):
        self.detector = VisualXSSDetector(headless=True)
    
    def test_initialization(self):
        """Test detector initialization"""
        self.assertIsNotNone(self.detector)
        self.assertTrue(self.detector.headless)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGeneticMutator))
    suite.addTests(loader.loadTestsFromTestCase(TestGANGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestReinforcementLearner))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestWAFFingerprinter))
    suite.addTests(loader.loadTestsFromTestCase(TestContextPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestDistributedSwarm))
    suite.addTests(loader.loadTestsFromTestCase(TestBlindXSSMonitor))
    suite.addTests(loader.loadTestsFromTestCase(TestVisualDetector))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
