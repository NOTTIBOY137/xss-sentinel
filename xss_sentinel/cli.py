import argparse
import sys
import os
import time
from urllib.parse import urlparse
from .core.crawler import Crawler
from .core.scanner import XSSScanner
from .core.reporter import Reporter
from .core.payload_manager import PayloadManager
from .core.parallel_scanner import ParallelScanner
from .ml.model import XSSClassifier
from .ml.payload_generator import PayloadGenerator
from .ml.context_analyzer import ContextAnalyzer
from .crawlers.wayback_crawler import WaybackCrawler, CommonCrawlService
from .crawlers.advanced_crawler import AdvancedCrawler
from .crawlers.js_crawler import JSCrawler, SPACrawler

def main():
    parser = argparse.ArgumentParser(description='XSS Sentinel - AI-Powered XSS vulnerability scanner')
    
    # Required arguments
    parser.add_argument('url', help='Target URL to scan')
    
    # Optional arguments
    parser.add_argument('-d', '--depth', type=int, default=2, help='Crawling depth (default: 2)')
    parser.add_argument('-o', '--output', default='reports', help='Output directory for reports (default: reports)')
    parser.add_argument('--no-ml', action='store_true', help='Disable ML-based features')
    parser.add_argument('-p', '--payloads', help='Path to custom XSS payloads file')
    parser.add_argument('-m', '--model', help='Path to trained model directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    
    # Advanced crawling options
    parser.add_argument('--include-subdomains', action='store_true', help='Include subdomains during crawling')
    parser.add_argument('--use-wayback', action='store_true', help='Use Wayback Machine to discover URLs')
    parser.add_argument('--use-commoncrawl', action='store_true', help='Use CommonCrawl to discover URLs')
    parser.add_argument('--max-urls', type=int, default=10000, help='Maximum number of URLs to crawl (default: 10000)')
    parser.add_argument('--respect-robots', action='store_true', help='Respect robots.txt directives')
    
    # Scanning options
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between requests in seconds (default: 0.5)')
    parser.add_argument('--max-tests', type=int, help='Maximum number of XSS tests to perform')
    parser.add_argument('--user-agent', help='Custom User-Agent string')
    parser.add_argument('--cookie', help='Cookies to include with requests (format: name=value; name2=value2)')
    parser.add_argument('--parallel', type=int, default=5, help='Number of parallel scanning threads (default: 5)')
    parser.add_argument('--scan-time-limit', type=int, help='Limit scanning time in seconds')
    
    # AI/ML options
    parser.add_argument('--ai-payloads', action='store_true', help='Use AI-generated payloads')
    parser.add_argument('--context-analysis', action='store_true', help='Use advanced context analysis')
    parser.add_argument('--evasion-level', type=int, default=1, choices=[0, 1, 2, 3], 
                      help='WAF evasion level (0=none, 1=basic, 2=advanced, 3=extreme)')
    parser.add_argument('--payloads-per-point', type=int, default=5, 
                      help='Number of payloads to test per injection point (default: 5)')
    
    # Scan mode
    parser.add_argument('--mode', choices=['standard', 'thorough', 'quick', 'passive'], default='standard',
                      help='Scanning mode (default: standard)')
    parser.add_argument('--scan-js', action='store_true', help='Scan JavaScript files for DOM XSS vulnerabilities')
    parser.add_argument('--urls-file', help='File with URLs to scan (one per line)')
    
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
    
    print(f"XSS Sentinel v1.0.0")
    print(f"Target: {args.url}")
    print(f"Mode: {args.mode}")
    print(f"AI/ML features: {'Disabled' if args.no_ml else 'Enabled'}")
    print("="*60)
    
    try:
        # Create output directory
        os.makedirs(args.output, exist_ok=True)
        
        # Initialize URL collection
        all_urls = set()
        
        # Add URLs from file if provided
        if args.urls_file and os.path.exists(args.urls_file):
            with open(args.urls_file, 'r') as f:
                for line in f:
                    url = line.strip()
                    if url and url.startswith(('http://', 'https://')):
                        all_urls.add(url)
            print(f"Loaded {len(all_urls)} URLs from {args.urls_file}")
        
        # Standard crawling
        if args.mode != 'passive':
            print(f"Starting crawl with depth {args.depth}...")
            crawler = AdvancedCrawler(
                args.url,
                max_depth=args.depth,
                max_urls=args.max_urls,
                include_subdomains=args.include_subdomains,
                respect_robots=args.respect_robots,
                delay=args.delay
            )
            
            crawl_results = crawler.crawl()
            crawled_urls = crawl_results['urls']
            forms = crawl_results['forms']
            
            print(f"Discovered {len(crawled_urls)} URLs through standard crawling")
            all_urls.update(crawled_urls)
        
        # Use Wayback Machine if requested
        if args.use_wayback:
            print("Using Wayback Machine to discover additional URLs...")
            wayback = WaybackCrawler(delay=args.delay)
            domain = urlparse(args.url).netloc
            wayback_urls = wayback.get_wayback_urls(domain, limit=args.max_urls)
            
            print(f"Discovered {len(wayback_urls)} URLs through Wayback Machine")
            all_urls.update(wayback_urls)
        
        # Use CommonCrawl if requested
        if args.use_commoncrawl:
            print("Using CommonCrawl to discover additional URLs...")
            cc = CommonCrawlService()
            domain = urlparse(args.url).netloc
            cc_urls = cc.get_urls_for_domain(domain, limit=args.max_urls)
            
            print(f"Discovered {len(cc_urls)} URLs through CommonCrawl")
            all_urls.update(cc_urls)
        
        # Scan JavaScript files if requested
        js_analysis_results = {}
        if args.scan_js:
            print("Scanning JavaScript files for DOM XSS vulnerabilities...")
            js_crawler = JSCrawler()
            
            # Find JS files in URLs
            js_files = [url for url in all_urls if url.endswith('.js')]
            
            print(f"Found {len(js_files)} JavaScript files")
            
            # Analyze each JS file
            for js_file in js_files:
                js_analysis_results[js_file] = js_crawler.analyze_js_file(js_file)
        
        # SPA scanning if in thorough mode
        spa_results = {}
        if args.mode == 'thorough':
            print("Scanning for Single Page Application (SPA) specific vulnerabilities...")
            spa_crawler = SPACrawler()
            
            # Select a few URLs to scan as potential SPAs
            potential_spas = [args.url]  # Start with the main URL
            spa_indicators = ['/app', '/dashboard', '/portal', '/console']
            
            for url in all_urls:
                for indicator in spa_indicators:
                    if indicator in url:
                        potential_spas.append(url)
                        break
            
            # Limit to 5 potential SPAs
            potential_spas = potential_spas[:5]
            
            for spa_url in potential_spas:
                print(f"Analyzing SPA: {spa_url}")
                spa_results[spa_url] = spa_crawler.crawl_spa(spa_url)
        
        # Print summary of discovered URLs
        print(f"Total unique URLs discovered: {len(all_urls)}")
        
        # Initialize scanning based on mode
        if args.mode == 'passive':
            print("Passive mode: No active scanning will be performed")
            
            # Generate a report of discovered URLs and resources
            report = Reporter(args.output)
            passive_report = {
                'urls': list(all_urls),
                'js_analysis': js_analysis_results,
                'spa_analysis': spa_results
            }
            
            report_path = os.path.join(args.output, f"passive_scan_{int(time.time())}.json")
            with open(report_path, 'w') as f:
                import json
                json.dump(passive_report, f, indent=2)
            
            print(f"Passive scan report saved to: {report_path}")
            sys.exit(0)
        
        # Initialize AI components if enabled
        if not args.no_ml and (args.ai_payloads or args.context_analysis):
            print("Initializing AI components...")
            
            if args.ai_payloads:
                payload_generator = PayloadGenerator()
                print("AI payload generator initialized")
            
            if args.context_analysis:
                context_analyzer = ContextAnalyzer()
                print("Advanced context analyzer initialized")
        
        # Determine which URLs to scan based on mode
        urls_to_scan = list(all_urls)
        if args.mode == 'quick':
            # In quick mode, limit to 100 URLs with parameters
            urls_with_params = [u for u in urls_to_scan if '?' in u]
            urls_to_scan = urls_with_params[:100] if urls_with_params else urls_to_scan[:100]
            print(f"Quick mode: Scanning limited to {len(urls_to_scan)} URLs")
        
        # Initialize parallel scanner
        print("Initializing scanner...")
        scanner = ParallelScanner(
            target_domain=urlparse(args.url).netloc,
            max_workers=args.parallel,
            delay=args.delay,
            results_dir=args.output
        )
        
        # Add URLs to scan
        scanner.add_urls(urls_to_scan)
        
        # Start scanning
        print(f"Starting scan with {args.parallel} parallel workers...")
        start_time = time.time()
        
        vulnerabilities = scanner.scan(timeout=args.scan_time_limit)
        
        scan_time = time.time() - start_time
        
        # Print results
        print("\n" + "="*60)
        print(f"Scan completed in {scan_time:.2f} seconds")
        print(f"Discovered {len(vulnerabilities)} potential XSS vulnerabilities")
        print("="*60)
        
        if vulnerabilities:
            print("\nVulnerabilities found:")
            for i, vuln in enumerate(vulnerabilities, 1):
                print(f"{i}. URL: {vuln['url']}")
                print(f"   Parameter: {vuln['param_name']}")
                print(f"   Payload: {vuln['payload']}")
                print(f"   Context: {vuln['context']}")
                print("-"*60)
        
        # Generate report
        report_path = os.path.join(args.output, f"xss_scan_{int(time.time())}.json")
        with open(report_path, 'w') as f:
            import json
            json.dump({
                'target': args.url,
                'scan_time': scan_time,
                'urls_discovered': len(all_urls),
                'vulnerabilities': vulnerabilities
            }, f, indent=2)
        
        print(f"Detailed report saved to: {report_path}")
        
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
