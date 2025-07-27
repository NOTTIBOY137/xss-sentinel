"""
Basic tests for XSS Sentinel
"""
import pytest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from xss_sentinel.core.scanner import XSSScanner
from xss_sentinel.core.crawler import Crawler
from xss_sentinel.core.payload_manager import PayloadManager


class TestBasicFunctionality:
    """Test basic functionality of XSS Sentinel components"""
    
    def test_scanner_initialization(self):
        """Test that scanner can be initialized"""
        scanner = XSSScanner()
        assert scanner is not None
        assert hasattr(scanner, 'scan_url')
    
    def test_crawler_initialization(self):
        """Test that crawler can be initialized"""
        crawler = Crawler()
        assert crawler is not None
        assert hasattr(crawler, 'crawl')
    
    def test_payload_manager_initialization(self):
        """Test that payload manager can be initialized"""
        pm = PayloadManager()
        assert pm is not None
        assert hasattr(pm, 'get_payloads')
    
    def test_payload_manager_has_payloads(self):
        """Test that payload manager has payloads"""
        pm = PayloadManager()
        payloads = pm.get_payloads()
        assert len(payloads) > 0
        assert all(isinstance(payload, str) for payload in payloads)
    
    def test_url_validation(self):
        """Test URL validation"""
        scanner = XSSScanner()
        
        # Valid URLs
        valid_urls = [
            "http://example.com",
            "https://example.com",
            "http://test.example.com/path",
            "https://example.com:8080/path?param=value"
        ]
        
        for url in valid_urls:
            assert scanner._is_valid_url(url) is True
        
        # Invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "example.com",
            ""
        ]
        
        for url in invalid_urls:
            assert scanner._is_valid_url(url) is False


class TestCLI:
    """Test CLI functionality"""
    
    def test_cli_import(self):
        """Test that CLI can be imported"""
        try:
            from xss_sentinel.cli import main
            assert callable(main)
        except ImportError as e:
            pytest.fail(f"Failed to import CLI: {e}")
    
    def test_cli_help(self):
        """Test that CLI help works"""
        import subprocess
        import sys
        
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'xss_sentinel.cli', '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0
            assert 'XSS Sentinel' in result.stdout
        except subprocess.TimeoutExpired:
            pytest.fail("CLI help command timed out")
        except Exception as e:
            pytest.fail(f"CLI help test failed: {e}")


class TestDependencies:
    """Test that all required dependencies are available"""
    
    def test_required_dependencies(self):
        """Test that all required dependencies can be imported"""
        required_modules = [
            'requests',
            'beautifulsoup4',
            'scikit-learn',
            'numpy',
            'tqdm',
            'colorama',
            'joblib',
            'lxml',
            'selenium',
            'fake_useragent',
            'cloudscraper',
            'undetected_chromedriver',
            'requests_html',
            'aiohttp',
            'asyncio_throttle',
            'python_whois',
            'dns',
            'cryptography',
            'Crypto',
            'urllib3',
            'playwright'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Required dependency {module} not available: {e}")
    
    def test_optional_ai_dependencies(self):
        """Test optional AI dependencies (should not fail if missing)"""
        optional_modules = [
            'sentence_transformers',
            'transformers',
            'torch'
        ]
        
        for module in optional_modules:
            try:
                __import__(module)
            except ImportError:
                # This is expected for optional dependencies
                pass


if __name__ == '__main__':
    pytest.main([__file__]) 