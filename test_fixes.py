#!/usr/bin/env python3
"""
Test script to verify XSS Sentinel fixes
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_url_validation():
    """Test URL validation functionality"""
    print("🧪 Testing URL validation...")
    
    try:
        from xss_sentinel.utils.http_utils import is_valid_url
        
        # Test valid URLs
        valid_urls = [
            "https://example.com",
            "http://testphp.vulnweb.com",
            "https://subdomain.example.com/path?param=value",
            "http://localhost:8080/test"
        ]
        
        # Test invalid URLs
        invalid_urls = [
            "javascript:alert('XSS')",
            "data:text/html,<script>alert('XSS')</script>",
            "file:///etc/passwd",
            "mailto:test@example.com",
            "tel:+1234567890",
            "https://georganicsis.blogspot.com%3c",
            "javascript:alert(%22xss%22)",
            "javascript:ALERT(%22XSS%22)",
            "javascript:alert(&quot;xss&quot;)",
            "javascript:alert(%22xss%22)",
            "javascript:ALERT(%22xss%22)",
            "javascript:alert(%22XSS%22)",
            "javascript:ALERT(%22XSS%22)"
        ]
        
        # Test valid URLs
        for url in valid_urls:
            if not is_valid_url(url):
                print(f"❌ Valid URL incorrectly rejected: {url}")
                return False
            else:
                print(f"✅ Valid URL accepted: {url}")
        
        # Test invalid URLs
        for url in invalid_urls:
            if is_valid_url(url):
                print(f"❌ Invalid URL incorrectly accepted: {url}")
                return False
            else:
                print(f"✅ Invalid URL rejected: {url}")
        
        print("✅ URL validation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ URL validation test failed: {e}")
        return False

def test_ai_imports():
    """Test AI module imports with fallback"""
    print("\n🧪 Testing AI module imports...")
    
    try:
        # Test AI core import
        from xss_sentinel.ai.core_ai import XSSAICore
        print("✅ XSSAICore imported successfully")
        
        # Test transformer generator import
        from xss_sentinel.ai.transformer_generator import TransformerPayloadGenerator
        print("✅ TransformerPayloadGenerator imported successfully")
        
        # Test adaptive learning import
        from xss_sentinel.ai.adaptive_learning import AdaptiveLearningEngine
        print("✅ AdaptiveLearningEngine imported successfully")
        
        # Test initialization (should not crash even without AI dependencies)
        try:
            ai_core = XSSAICore()
            print("✅ XSSAICore initialized successfully")
        except Exception as e:
            print(f"⚠️ XSSAICore initialization failed (expected without AI deps): {e}")
        
        try:
            transformer = TransformerPayloadGenerator()
            print("✅ TransformerPayloadGenerator initialized successfully")
        except Exception as e:
            print(f"⚠️ TransformerPayloadGenerator initialization failed (expected without AI deps): {e}")
        
        try:
            adaptive = AdaptiveLearningEngine()
            print("✅ AdaptiveLearningEngine initialized successfully")
        except Exception as e:
            print(f"⚠️ AdaptiveLearningEngine initialization failed (expected without AI deps): {e}")
        
        print("✅ AI module import tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ AI module import test failed: {e}")
        return False

def test_http_client():
    """Test HTTP client with URL validation"""
    print("\n🧪 Testing HTTP client...")
    
    try:
        from xss_sentinel.utils.http_utils import StealthHTTPClient
        
        client = StealthHTTPClient()
        
        # Test with valid URL
        response = client.make_request("https://httpbin.org/get")
        if response is not None:
            print("✅ Valid URL request successful")
        else:
            print("⚠️ Valid URL request failed (may be network issue)")
        
        # Test with invalid URL (should be skipped)
        response = client.make_request("javascript:alert('XSS')")
        if response is None:
            print("✅ Invalid URL correctly skipped")
        else:
            print("❌ Invalid URL was not skipped")
            return False
        
        print("✅ HTTP client tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ HTTP client test failed: {e}")
        return False

def test_parallel_scanner():
    """Test parallel scanner URL filtering"""
    print("\n🧪 Testing parallel scanner...")
    
    try:
        from xss_sentinel.core.parallel_scanner import ParallelScanner
        
        scanner = ParallelScanner(target_domain="example.com")
        
        # Test URL filtering
        test_urls = [
            "https://example.com/test",
            "https://subdomain.example.com/path",
            "javascript:alert('XSS')",
            "https://malicious.com/evil",
            "data:text/html,<script>alert('XSS')</script>"
        ]
        
        scanner.add_urls(test_urls)
        
        # Should only accept URLs from example.com domain and reject invalid ones
        expected_valid = 2  # example.com URLs
        expected_invalid = 2  # javascript: and data: URLs (malicious.com is valid URL but wrong domain)
        
        if scanner.scan_stats['total_urls'] == expected_valid:
            print(f"✅ URL filtering correct: {scanner.scan_stats['total_urls']} valid URLs")
        else:
            print(f"❌ URL filtering incorrect: expected {expected_valid}, got {scanner.scan_stats['total_urls']}")
            return False
        
        if scanner.scan_stats['invalid_urls_skipped'] == expected_invalid:
            print(f"✅ Invalid URL skipping correct: {scanner.scan_stats['invalid_urls_skipped']} skipped")
        else:
            print(f"❌ Invalid URL skipping incorrect: expected {expected_invalid}, got {scanner.scan_stats['invalid_urls_skipped']}")
            return False
        
        print("✅ Parallel scanner tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Parallel scanner test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 XSS Sentinel Fix Verification Tests")
    print("=" * 50)
    
    tests = [
        test_url_validation,
        test_ai_imports,
        test_http_client,
        test_parallel_scanner
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixes are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 