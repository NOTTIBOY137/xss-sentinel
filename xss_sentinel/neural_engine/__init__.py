"""
XSS Sentinel v2.0 Neural Engine
Revolutionary AI-powered XSS detection system with self-learning capabilities
"""

__version__ = "2.0.0"
__author__ = "XSS Sentinel Team"

# Neural Engine Components
try:
    from .genetic_mutator import GeneticPayloadMutator, PayloadGene
    from .gan_payload_generator import GANPayloadGenerator
    from .reinforcement_learner import ReinforcementLearner, WAFEnvironment
    from .integration import NeuralEngineIntegration
    from .distributed_swarm import DistributedSwarmCoordinator, ScanTask, WorkerNode
    from .visual_xss_detector import VisualXSSDetector
    from .waf_fingerprinter import WAFFingerprinter
    from .blind_xss_monitor import BlindXSSMonitor
    from .context_predictor import ContextPredictor
    
    __all__ = [
        'GeneticPayloadMutator',
        'PayloadGene',
        'GANPayloadGenerator',
        'ReinforcementLearner',
        'WAFEnvironment',
        'NeuralEngineIntegration',
        'DistributedSwarmCoordinator',
        'ScanTask',
        'WorkerNode',
        'VisualXSSDetector',
        'WAFFingerprinter',
        'BlindXSSMonitor',
        'ContextPredictor',
    ]
except ImportError as e:
    # Graceful degradation if components not available
    import warnings
    warnings.warn(f"Some neural engine components not available: {e}")
    __all__ = []
