import re
from bs4 import BeautifulSoup, Comment
import html
import urllib.parse

class AdvancedContextAnalyzer:
    def __init__(self):
        # Regexes for detecting different contexts
        self.js_regex = re.compile(r'<script[^>]*>|on\w+\s*=|javascript:|eval\(|setTimeout\(|Function\(')
        self.attribute_regex = re.compile(r'=\s*["\'][^"\']*$')
        self.url_regex = re.compile(r'(href|src|action|formaction)\s*=\s*["\']?[^"\']*$')
        self.style_regex = re.compile(r'<style[^>]*>|style\s*=\s*["\']')
        
        # DOM sink detection
        self.dom_sinks = [
            'document.write', 'innerHTML', 'outerHTML', 'insertAdjacentHTML',
            'eval', 'setTimeout', 'setInterval', 'execScript', 'Function',
            'location', 'location.href', 'location.replace', 'location.assign',
            'jQuery', '$', 'el.html', 'el.append'
        ]
    
    def identify_context(self, html_content, marker):
        """
        Advanced context identification for XSS vulnerabilities
        
        Args:
            html_content: The HTML content to analyze
            marker: The marker string to find in the HTML
            
        Returns:
            Dictionary with context information
        """
        if not marker in html_content:
            return {"context": "unknown", "confidence": 0, "details": {}}
        
        # Parse HTML
        try:
            marker_positions = self._find_marker_positions(html_content, marker)
            contexts = []
            
            for start_pos, end_pos in marker_positions:
                # Extract surrounding context (50 chars before and after)
                prefix = html_content[max(0, start_pos - 50):start_pos]
                suffix = html_content[end_pos:min(len(html_content), end_pos + 50)]
                
                context_info = self._analyze_context_at_position(prefix, suffix)
                contexts.append(context_info)
            
            # If multiple contexts found, return the one with highest confidence
            if contexts:
                best_context = max(contexts, key=lambda x: x["confidence"])
                return best_context
            else:
                return {"context": "html", "confidence": 0.5, "details": {}}
                
        except Exception as e:
            print(f"Error in advanced context analysis: {e}")
            return {"context": "html", "confidence": 0.1, "details": {}}
    
    def _find_marker_positions(self, content, marker):
        """Find all positions of the marker in the content"""
        positions = []
        start = 0
        
        while True:
            start = content.find(marker, start)
            if start == -1:
                break
                
            end = start + len(marker)
            positions.append((start, end))
            start = end
        
        return positions
    
    def _analyze_context_at_position(self, prefix, suffix):
        """Analyze the context at a specific position"""
        # Combined prefix and suffix for better analysis
        combined = prefix + "MARKER" + suffix
        
        # JavaScript context detection
        if self.js_regex.search(prefix):
            # Check if inside script tag
            if "<script" in prefix and "</script>" in suffix:
                return {
                    "context": "js",
                    "subcontext": "script_tag",
                    "confidence": 0.9,
                    "details": {"prefix": prefix, "suffix": suffix}
                }
            
            # Check if inside event handler
            event_match = re.search(r'on(\w+)\s*=\s*["\']([^"\']*$)', prefix)
            if event_match:
                event_type = event_match.group(1)
                return {
                    "context": "js",
                    "subcontext": "event_handler",
                    "confidence": 0.85,
                    "details": {"event": event_type, "prefix": prefix, "suffix": suffix}
                }
            
            # General JS context
            return {
                "context": "js",
                "subcontext": "general",
                "confidence": 0.7,
                "details": {"prefix": prefix, "suffix": suffix}
            }
        
        # URL context detection
        url_match = self.url_regex.search(prefix)
        if url_match:
            attr_type = url_match.group(1)
            return {
                "context": "url",
                "subcontext": attr_type,
                "confidence": 0.8,
                "details": {"attribute": attr_type, "prefix": prefix, "suffix": suffix}
            }
        
        # Attribute context detection
        if self.attribute_regex.search(prefix):
            # Try to determine attribute name
            attr_match = re.search(r'(\w+)\s*=\s*["\'][^"\']*$', prefix)
            attr_name = attr_match.group(1) if attr_match else "unknown"
            
            return {
                "context": "attribute",
                "subcontext": attr_name,
                "confidence": 0.75,
                "details": {"attribute": attr_name, "prefix": prefix, "suffix": suffix}
            }
        
        # Style context detection
        if self.style_regex.search(prefix):
            return {
                "context": "style",
                "subcontext": "css",
                "confidence": 0.7,
                "details": {"prefix": prefix, "suffix": suffix}
            }
        
        # Default to HTML context
        return {
            "context": "html",
            "subcontext": "general",
            "confidence": 0.6,
            "details": {"prefix": prefix, "suffix": suffix}
        }
    
    def extract_dom_sinks(self, js_code):
        """Extract potential DOM XSS sinks from JavaScript code"""
        sinks = []
        
        for sink in self.dom_sinks:
            positions = self._find_marker_positions(js_code, sink)
            for start, end in positions:
                # Get surrounding context (50 chars after the sink)
                context = js_code[start:min(len(js_code), end + 50)]
                sinks.append({
                    "sink": sink,
                    "position": start,
                    "context": context
                })
        
        return sinks
    
    def analyze_response_for_vulnerabilities(self, url, response_text, injected_payload):
        """
        Analyze a response for potential XSS vulnerabilities
        
        Args:
            url: The URL that was tested
            response_text: The HTML response
            injected_payload: The payload that was injected
            
        Returns:
            Dictionary with vulnerability information
        """
        results = {
            "url": url,
            "payload_reflected": injected_payload in response_text,
            "potential_vulnerability": False,
            "contexts": [],
            "confidence": 0,
            "payload_executed": False,
            "details": {}
        }
        
        if not injected_payload in response_text:
            return results
        
        # Find all reflections of the payload
        reflection_positions = self._find_marker_positions(response_text, injected_payload)
        
        for start, end in reflection_positions:
            # Extract surrounding context (100 chars before and after)
            prefix = response_text[max(0, start - 100):start]
            suffix = response_text[end:min(len(response_text), end + 100)]
            
            # Analyze context
            context_info = self._analyze_context_at_position(prefix, suffix)
            results["contexts"].append(context_info)
            
            # Check if execution is likely
            execution_likely = self._check_execution_likelihood(injected_payload, context_info, prefix, suffix)
            if execution_likely > results["confidence"]:
                results["confidence"] = execution_likely
                results["potential_vulnerability"] = True
        
        return results
    
    def _check_execution_likelihood(self, payload, context_info, prefix, suffix):
        """Check the likelihood that a payload would be executed"""
        context = context_info["context"]
        confidence = 0.0
        
        # Check for script tags
        if "<script" in payload and "</script>" in payload:
            if context == "html" and not "escaped" in context_info.get("details", {}):
                confidence = 0.9
        
        # Check for event handlers
        elif "on" in payload and "=" in payload:
            if context == "attribute" or context == "html":
                confidence = 0.8
        
        # Check for javascript: URLs
        elif "javascript:" in payload:
            if context == "url":
                confidence = 0.85
        
        # Check for eval or other JS execution sinks
        elif any(sink in payload for sink in self.dom_sinks):
            if context == "js":
                confidence = 0.9
        
        # General tests
        if context == "js" and "alert" in payload:
            confidence = max(confidence, 0.7)
        
        if context == "html" and ("<img" in payload or "<svg" in payload) and "onerror" in payload:
            confidence = max(confidence, 0.75)
        
        # Check encoding/escaping
        if "escaped" in context_info.get("details", {}) or "encoded" in context_info.get("details", {}):
            confidence *= 0.3
        
        return confidence
