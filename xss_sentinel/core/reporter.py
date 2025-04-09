import json
import os
from datetime import datetime

class Reporter:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, scan_results, target_url):
        """Generate a report of the scan results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"xss_scan_{timestamp}.json"
        report_path = os.path.join(self.output_dir, report_name)
        
        # Compile report data
        report_data = {
            "target_url": target_url,
            "scan_time": datetime.now().isoformat(),
            "vulnerabilities_found": len(scan_results),
            "results": scan_results
        }
        
        # Write to file
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=4)
        
        print(f"Report saved to: {report_path}")
        return report_path
    
    def print_summary(self, scan_results, target_url):
        """Print a summary of scan results to the console"""
        print("\n" + "="*60)
        print(f"XSS Sentinel Scan Summary for: {target_url}")
        print("="*60)
        
        if not scan_results:
            print("No XSS vulnerabilities were found.")
        else:
            print(f"Found {len(scan_results)} potential XSS vulnerabilities:")
            print("-"*60)
            
            for i, vuln in enumerate(scan_results, 1):
                print(f"{i}. URL: {vuln['url']}")
                print(f"   Parameter: {vuln['parameter']}")
                print(f"   Injection Type: {vuln['type']}")
                print(f"   Context: {vuln['context']}")
                print(f"   Payload: {vuln['payload']}")
                print("-"*60)
        
        print("\nNote: This tool provides a basic assessment. Manual verification is recommended.")
        print("="*60 + "\n")
