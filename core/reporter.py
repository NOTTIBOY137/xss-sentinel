import json
import os
import datetime
import time
from pathlib import Path

class Reporter:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, scan_results, target_url):
        """Generate a report of the scan results"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"xss_scan_{timestamp}.json"
        report_path = os.path.join(self.output_dir, report_name)
        
        # Compile report data
        report_data = {
            "target_url": target_url,
            "scan_time": datetime.datetime.now().isoformat(),
            "vulnerabilities_found": len(scan_results),
            "results": scan_results
        }
        
        # Write to file
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"Report saved to: {report_path}")
        return report_path
    
    def generate_html_report(self, scan_results, target_url):
        """Generate an HTML report of the scan results"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"xss_scan_{timestamp}.html"
        report_path = os.path.join(self.output_dir, report_name)
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>XSS Sentinel Scan Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
                h1, h2, h3 {{ color: #0066cc; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .summary {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                .summary-box {{ background-color: #f9f9f9; border-radius: 5px; padding: 15px; width: 30%; }}
                .summary-box.vulnerable {{ background-color: #ffebee; }}
                .vuln-item {{ background-color: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; }}
                .vuln-item h3 {{ margin-top: 0; }}
                .vuln-details {{ margin-left: 20px; }}
                .payload {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace; overflow-x: auto; }}
                .footer {{ margin-top: 30px; font-size: 0.8em; color: #666; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>XSS Sentinel Scan Report</h1>
                    <p>Target: {target_url}</p>
                    <p>Scan Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                
                <div class="summary">
                    <div class="summary-box {'vulnerable' if scan_results else ''}">
                        <h2>Vulnerabilities Found</h2>
                        <p style="font-size: 24px; font-weight: bold;">{len(scan_results)}</p>
                    </div>
                    <div class="summary-box">
                        <h2>Scan Duration</h2>
                        <p style="font-size: 24px; font-weight: bold;">
                            {scan_results[0].get("scan_duration", "N/A") if scan_results else "N/A"}
                        </p>
                    </div>
                    <div class="summary-box">
                        <h2>Security Level</h2>
                        <p style="font-size: 24px; font-weight: bold; color: {'red' if scan_results else 'green'};">
                            {'VULNERABLE' if scan_results else 'SECURE'}
                        </p>
                    </div>
                </div>
                
                <h2>Detailed Results</h2>
        """
        
        if not scan_results:
            html_content += """
                <p>No XSS vulnerabilities were detected in the target.</p>
            """
        else:
            for i, vuln in enumerate(scan_results, 1):
                html_content += f"""
                <div class="vuln-item">
                    <h3>Vulnerability #{i}</h3>
                    <div class="vuln-details">
                        <p><strong>URL:</strong> {vuln.get('url', 'N/A')}</p>
                        <p><strong>Parameter:</strong> {vuln.get('param_name', 'N/A')}</p>
                        <p><strong>Type:</strong> {vuln.get('point_type', 'N/A')}</p>
                        <p><strong>Context:</strong> {vuln.get('context', 'N/A')}</p>
                        <p><strong>Payload:</strong></p>
                        <div class="payload">{vuln.get('payload', 'N/A')}</div>
                    </div>
                </div>
                """
        
        html_content += """
                <div class="footer">
                    <p>Generated by XSS Sentinel - Advanced AI-Powered XSS Testing Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Write to file
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        print(f"HTML report saved to: {report_path}")
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
                print(f"{i}. URL: {vuln.get('url', 'N/A')}")
                print(f"   Parameter: {vuln.get('param_name', 'N/A')}")
                print(f"   Type: {vuln.get('point_type', 'N/A')}")
                print(f"   Context: {vuln.get('context', 'N/A')}")
                print(f"   Payload: {vuln.get('payload', 'N/A')}")
                print("-"*60)
        
        print("\nNote: This tool provides a basic assessment. Manual verification is recommended.")
        print("="*60 + "\n")
