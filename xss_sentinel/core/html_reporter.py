import os
from datetime import datetime
import json

class HTMLReporter:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_html_report(self, scan_results, target_url):
        """Generate an interactive HTML report of the scan results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"xss_scan_{timestamp}.html"
        report_path = os.path.join(self.output_dir, report_name)

        # Prepare data for charts
        context_counts = {}
        payload_counts = {}
        for vuln in scan_results:
            ctx = str(vuln.get('context', 'unknown'))
            context_counts[ctx] = context_counts.get(ctx, 0) + 1
            payload = vuln.get('payload', 'unknown')
            payload_counts[payload] = payload_counts.get(payload, 0) + 1

        # HTML template with embedded Chart.js and table
        html = f"""
<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <title>XSS Sentinel Report - {target_url}</title>
    <script src='https://cdn.jsdelivr.net/npm/chart.js'></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 40px auto; background: #fff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 8px #0001; }}
        h1, h2 {{ color: #2c3e50; }}
        .summary {{ margin-bottom: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 30px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background: #2c3e50; color: #fff; }}
        tr:nth-child(even) {{ background: #f2f2f2; }}
        input[type='text'] {{ width: 300px; padding: 6px; margin-bottom: 10px; }}
    </style>
</head>
<body>
<div class='container'>
    <h1>XSS Sentinel Interactive Report</h1>
    <div class='summary'>
        <h2>Summary</h2>
        <p><b>Target URL:</b> {target_url}</p>
        <p><b>Scan Time:</b> {datetime.now().isoformat()}</p>
        <p><b>Total Vulnerabilities Found:</b> {len(scan_results)}</p>
    </div>
    <div style='display: flex; gap: 40px;'>
        <div style='flex:1;'>
            <canvas id='contextChart'></canvas>
        </div>
        <div style='flex:1;'>
            <canvas id='payloadChart'></canvas>
        </div>
    </div>
    <h2>Vulnerabilities</h2>
    <input type='text' id='searchInput' onkeyup='filterTable()' placeholder='Search for payloads, URLs, context...'>
    <table id='vulnTable'>
        <thead>
            <tr>
                <th>#</th>
                <th>URL</th>
                <th>Parameter</th>
                <th>Type</th>
                <th>Context</th>
                <th>Payload</th>
            </tr>
        </thead>
        <tbody>
            {''.join([f"<tr><td>{i+1}</td><td>{vuln['url']}</td><td>{vuln.get('parameter','')}</td><td>{vuln.get('type','')}</td><td>{vuln.get('context','')}</td><td>{vuln.get('payload','')}</td></tr>" for i, vuln in enumerate(scan_results)])}
        </tbody>
    </table>
</div>
<script>
// Chart.js context breakdown
const ctxData = {{
    labels: {list(context_counts.keys())},
    datasets: [{{
        label: 'Context Breakdown',
        data: {list(context_counts.values())},
        backgroundColor: [
            '#3498db', '#e67e22', '#2ecc71', '#e74c3c', '#9b59b6', '#f1c40f', '#34495e', '#1abc9c', '#95a5a6', '#7f8c8d'
        ]
    }}]
}};
new Chart(document.getElementById('contextChart'), {{ type: 'pie', data: ctxData }});
// Chart.js payload effectiveness
const payloadData = {{
    labels: {list(payload_counts.keys())[:10]},
    datasets: [{{
        label: 'Top Payloads',
        data: {list(payload_counts.values())[:10]},
        backgroundColor: '#2ecc71'
    }}]
}};
new Chart(document.getElementById('payloadChart'), {{ type: 'bar', data: payloadData }});
// Table search/filter
function filterTable() {{
    var input = document.getElementById('searchInput');
    var filter = input.value.toLowerCase();
    var table = document.getElementById('vulnTable');
    var tr = table.getElementsByTagName('tr');
    for (var i = 1; i < tr.length; i++) {{
        var tds = tr[i].getElementsByTagName('td');
        var show = false;
        for (var j = 0; j < tds.length; j++) {{
            if (tds[j].innerText.toLowerCase().indexOf(filter) > -1) {{
                show = true;
                break;
            }}
        }}
        tr[i].style.display = show ? '' : 'none';
    }}
}}
</script>
</body>
</html>
"""
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"HTML report saved to: {report_path}")
        return report_path 