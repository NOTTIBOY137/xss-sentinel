# XSS Sentinel v2.0 Neural Engine - Troubleshooting Guide

## Common Issues and Solutions

### Issue: Import Errors

**Error**: `ModuleNotFoundError: No module named 'torch'`

**Solution**: 
```bash
pip install torch torchvision
```

**Error**: `ModuleNotFoundError: No module named 'selenium'`

**Solution**:
```bash
pip install selenium
```

**Error**: `ModuleNotFoundError: No module named 'aiohttp'`

**Solution**:
```bash
pip install aiohttp
```

### Issue: Genetic Mutator Not Evolving

**Symptoms**: Payloads don't improve over generations

**Solutions**:
1. Check fitness function - ensure it returns meaningful scores
2. Increase population size: `GeneticPayloadMutator(population_size=100)`
3. Adjust mutation rate: `mutation_rate=0.5` for more variation
4. Run more generations: `generations=20`

### Issue: GAN Training Fails

**Symptoms**: Training crashes or produces invalid payloads

**Solutions**:
1. Reduce batch size: `batch_size=8`
2. Use smaller model: `hidden_dim=128`
3. Ensure sufficient training data (20+ payloads)
4. Check GPU memory if using CUDA

### Issue: RL Agent Not Learning

**Symptoms**: Success rate doesn't improve

**Solutions**:
1. Adjust learning rate: `learning_rate=0.2`
2. Increase episodes: `episodes=200`
3. Improve test function - ensure it provides meaningful feedback
4. Check epsilon decay: `epsilon_decay=0.99`

### Issue: WAF Fingerprinting False Positives

**Symptoms**: Incorrect WAF detection

**Solutions**:
1. Provide test payloads: `fingerprint_waf(url, test_payloads=[...])`
2. Check network connectivity
3. Review signature database
4. Use ML model for better accuracy

### Issue: Visual Detection Not Working

**Symptoms**: No screenshots or browser errors

**Solutions**:
1. Install ChromeDriver: `pip install webdriver-manager`
2. Check headless mode: `VisualXSSDetector(headless=False)`
3. Verify Selenium installation
4. Check browser permissions

### Issue: Blind XSS Callbacks Not Received

**Symptoms**: No callbacks received

**Solutions**:
1. Verify callback domain is accessible
2. Check firewall rules (port 8888)
3. Ensure payload is actually executed
4. Check database: `sqlite3 blind_xss.db "SELECT * FROM callbacks"`

### Issue: Distributed Swarm Not Coordinating

**Symptoms**: Workers not processing tasks

**Solutions**:
1. Check Redis connection
2. Verify worker registration
3. Check network connectivity between nodes
4. Review coordinator logs

### Issue: Context Prediction Inaccurate

**Symptoms**: Wrong context type predicted

**Solutions**:
1. Provide more surrounding HTML context
2. Use rule-based refinement
3. Train custom model with domain-specific data
4. Check injection marker placement

### Issue: Memory Errors

**Symptoms**: Out of memory errors

**Solutions**:
1. Reduce batch sizes
2. Limit payload generation count
3. Use smaller models
4. Enable garbage collection

### Issue: Docker Containers Not Starting

**Symptoms**: Containers exit immediately

**Solutions**:
1. Check logs: `docker-compose logs`
2. Verify Dockerfile syntax
3. Check volume mounts
4. Ensure ports are not in use

### Issue: Performance Issues

**Symptoms**: Slow payload generation

**Solutions**:
1. Use multiprocessing for parallel generation
2. Cache results where possible
3. Optimize fitness functions
4. Use GPU acceleration for GAN/RL

## Getting Help

1. Check logs in `data/logs/`
2. Review error messages carefully
3. Test components individually
4. Check GitHub issues
5. Review documentation

## Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Health Checks

Test individual components:

```python
# Test genetic mutator
from xss_sentinel.neural_engine.genetic_mutator import GeneticPayloadMutator
mutator = GeneticPayloadMutator()
print("Genetic mutator: OK")

# Test GAN
from xss_sentinel.neural_engine.gan_payload_generator import GANPayloadGenerator
gan = GANPayloadGenerator()
print("GAN: OK")

# Test RL
from xss_sentinel.neural_engine.reinforcement_learner import ReinforcementLearner
rl = ReinforcementLearner()
print("RL: OK")
```
