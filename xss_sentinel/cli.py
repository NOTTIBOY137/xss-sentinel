import argparse
import sys
import os
from urllib.parse import urlparse
from .core.crawler import Crawler
from .core.scanner import XSSScanner
from .core.reporter import Reporter
from .ml.model import XSSClassifier

def main():
    parser = argparse.ArgumentParser(description='XSS Sentinel - ML-powered XSS vulnerability scanner')
    
    # Required arguments
    parser.add_argument('url', help='Target URL to scan')
    
    # Optional arguments
    parser.add_argument('-d', '--depth', type=int, default=2, help='Crawling depth (default: 2)')
    parser.add_argument('-o', '--output', default='reports', help='Output directory for reports (default: reports)')
    parser.add_argument('--no-ml', action='store_true', help='Disable ML-based features')
    parser.add_argument('-p', '--payloads', help='Path to custom XSS payloads file')
    parser.add_argument('-m', '--model', help='Path to trained model directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'http://' + args.url
    
    try:
        parsed_url = urlparse(args.url)
        if not parsed_url.netloc:
            print("Error: Invalid URL format")
            sys.exit(1)
    except Exception:
        print("Error: Could not parse URL")
        sys.exit(1)
    
    print(f"XSS Sentinel v0.1.0")
    print(f"Target: {args.url}")
    print(f"Crawl depth: {args.depth}")
    print(f"ML features: {'Disabled' if args.no_ml else 'Enabled'}")
    print("="*60)
    
    try:
        # Crawl the website
        crawler = Crawler(args.url, max_depth=args.depth)
        urls = crawler.crawl()
        
        print(f"Discovered {len(urls)} URLs for scanning")
        
        # Initialize scanner
        scanner = XSSScanner(args.url, depth=args.depth, use_ml=not args.no_ml)
        
        # Run the scan
        results = scanner.scan()
        
        # Generate report
        reporter = Reporter(args.output)
        reporter.print_summary(results, args.url)
        report_path = reporter.generate_report(results, args.url)
        
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
