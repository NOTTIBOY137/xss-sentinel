# XSS Sentinel v2.0 Neural Engine - Usage Guide

## Quick Start

### Basic Usage

```python
from xss_sentinel.neural_engine.integration import NeuralEngineIntegration

# Initialize neural engine
engine = NeuralEngineIntegration(
    enable_genetic=True,
    enable_gan=True,
    enable_rl=True
)

# Generate advanced payloads
base_payloads = ['<script>alert(1)</script>']
context = {'context_type': 'form_input', 'waf_type': 'cloudflare'}

advanced_payloads = engine.generate_advanced_payloads(
    base_payloads,
    context,
    'https://example.com',
    count=50
)

# Learn from results
engine.learn_from_result(
    advanced_payloads[0],
    context,
    success=True,
    details={}
)
```

## Component Usage

### 1. Genetic Mutator

```python
from xss_sentinel.neural_engine.genetic_mutator import GeneticPayloadMutator

mutator = GeneticPayloadMutator(population_size=50, mutation_rate=0.3)

def fitness_func(payload: str) -> float:
    # Define your fitness function
    score = 0.0
    if 'alert' in payload:
        score += 0.3
    if '%' in payload:  # Encoding bonus
        score += 0.4
    return min(score, 1.0)

evolved = mutator.evolve_population(
    seed_payloads=['<script>alert(1)</script>'],
    fitness_func=fitness_func,
    generations=10
)
```

### 2. GAN Payload Generator

```python
from xss_sentinel.neural_engine.gan_payload_generator import GANPayloadGenerator

gan = GANPayloadGenerator(latent_dim=100, hidden_dim=256)

# Train on successful payloads
successful_payloads = ['<script>alert(1)</script>', ...]
gan.train(successful_payloads, epochs=100, batch_size=32)

# Generate novel payloads
novel_payloads = gan.generate_payloads(count=10)
```

### 3. Reinforcement Learning

```python
from xss_sentinel.neural_engine.reinforcement_learner import ReinforcementLearner

agent = ReinforcementLearner(learning_rate=0.1, epsilon=1.0)

def test_function(payload: str):
    # Test if payload bypasses WAF
    success = test_against_waf(payload)
    return success, {}

# Train agent
agent.train(seed_payloads, episodes=100, test_function=test_function)

# Generate optimized payload
optimized, history = agent.generate_optimal_payload(base_payload)
```

### 4. WAF Fingerprinting

```python
from xss_sentinel.neural_engine.waf_fingerprinter import WAFFingerprinter

fingerprinter = WAFFingerprinter()

# Fingerprint WAF
result = fingerprinter.fingerprint_waf("https://example.com")

print(f"Detected WAF: {result['detected_waf']}")
print(f"Confidence: {result['confidence']}")

# Generate bypass payloads
bypass_payloads = fingerprinter.generate_bypass_payloads(
    '<script>alert(1)</script>',
    result['detected_waf']
)
```

### 5. Context Prediction

```python
from xss_sentinel.neural_engine.context_predictor import ContextPredictor

predictor = ContextPredictor()

# Analyze context
html = '<div><input value="XSS_TEST_123"></div>'
context = predictor.analyze_context(html, "XSS_TEST_123")

print(f"Context Type: {context.context_type}")
print(f"Confidence: {context.confidence}")

# Generate context-aware payloads
payloads = predictor.generate_context_payloads(context)
```

### 6. Distributed Swarm

```python
from xss_sentinel.neural_engine.distributed_swarm import DistributedSwarmCoordinator
import asyncio

coordinator = DistributedSwarmCoordinator(max_workers=10)

async def run_scan():
    results = await coordinator.run_distributed_scan(
        target_url="https://example.com",
        injection_points=[{'type': 'url_param', 'param_name': 'q'}],
        payloads=['<script>alert(1)</script>'] * 100,
        num_local_workers=4
    )
    return results

results = asyncio.run(run_scan())
```

### 7. Blind XSS Monitor

```python
from xss_sentinel.neural_engine.blind_xss_monitor import BlindXSSMonitor
import asyncio

monitor = BlindXSSMonitor(
    callback_domain='your-server.com',
    callback_port=8888
)

# Generate payload
payload = monitor.generate_payload(
    target_url='https://example.com/comment',
    injection_point='comment_field',
    payload_type='advanced'
)

# Start server
async def main():
    await monitor.start_server()
    # Server runs until interrupted

asyncio.run(main())
```

## Command Line Usage

### Run Quick Test

```bash
python examples/quick_test.py
```

### Run Simple Demo

```bash
python examples/simple_demo.py
```

### Run Complete Demo

```bash
python examples/complete_demo.py
```

### Run Tests

```bash
python -m pytest tests/test_neural_engine.py -v
```

## Docker Usage

### Build and Run

```bash
cd docker
docker-compose up -d
```

### View Logs

```bash
docker-compose logs -f scanner
```

### Stop Services

```bash
docker-compose down
```

## Integration with Existing Scanner

```python
from xss_sentinel.neural_engine.integration import patch_scanner_with_neural_engine
from your_scanner import XSSScanner

@patch_scanner_with_neural_engine
class EnhancedXSSScanner(XSSScanner):
    pass

# Use enhanced scanner
scanner = EnhancedXSSScanner(target_url="https://example.com")
scanner.scan()  # Now uses neural engine automatically
```

## Best Practices

1. **Start Small**: Begin with genetic mutator, then add GAN/RL as needed
2. **Monitor Performance**: Track success rates and adjust parameters
3. **Save Models**: Use `save_models()` to persist learned patterns
4. **Adaptive Learning**: Enable adaptive learning for continuous improvement
5. **Error Handling**: Always wrap neural engine calls in try-except blocks

## Troubleshooting

### PyTorch Not Available
- Install: `pip install torch torchvision`
- Components will gracefully degrade if not available

### Selenium Not Available
- Install: `pip install selenium`
- Visual detection will be limited

### aiohttp Not Available
- Install: `pip install aiohttp`
- Blind XSS monitor server will not start

For more details, see TROUBLESHOOTING.md
