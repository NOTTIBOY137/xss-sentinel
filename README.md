# 🛡️ XSS Sentinel: Advanced AI-Powered XSS Testing Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](setup.py)

**XSS Sentinel** is a next-generation cross-site scripting detection tool that leverages AI/ML capabilities to identify and exploit XSS vulnerabilities in web applications. Built with modern Python technologies and designed for both security researchers and penetration testers.

## 🚀 Key Features

### 🤖 AI-Powered Capabilities
- **Intelligent Payload Generation**: Creates context-aware payloads that evolve based on testing results
- **Adaptive Learning**: Improves detection capabilities over time by learning from successful exploits
- **Context Analysis**: Identifies the exact context where user input is reflected for precise payload generation
- **Transformer-based Models**: Advanced NLP models for payload generation and context understanding

### 🌐 Advanced Crawling
- **Multi-Source Discovery**: Combines standard crawling with Wayback Machine and CommonCrawl
- **JavaScript Analysis**: Deep scanning of JavaScript files for DOM XSS vulnerabilities
- **Subdomain Enumeration**: Comprehensive subdomain discovery and testing
- **Robots.txt Compliance**: Respectful crawling with configurable robots.txt handling

### ⚡ Performance & Efficiency
- **Parallel Scanning**: Tests multiple injection points simultaneously for faster results
- **Stealth Mode**: Advanced evasion techniques to bypass WAFs and detection systems
- **Configurable Throttling**: Rate limiting and delay controls for responsible testing
- **Memory Optimization**: Efficient resource usage for large-scale scans

### 📊 Comprehensive Reporting
- **Multiple Formats**: JSON, HTML, and text report formats
- **Interactive Dashboards**: Visual charts and searchable vulnerability tables
- **Detailed Evidence**: Complete payload analysis and context information
- **Export Capabilities**: Easy integration with security workflows

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Installation
```bash
# Clone the repository
git clone https://github.com/NOTTIBOY137/xss-sentinel.git
cd xss-sentinel

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Optional AI Dependencies
For full AI capabilities, install additional dependencies:
```bash
pip install sentence-transformers transformers torch
```

## 🎯 Usage Examples

### Basic Scan
```bash
# Simple XSS scan with default settings
xss-sentinel https://example.com
```

### Advanced AI-Powered Scan
```bash
# Full AI-powered scan with context analysis
xss-sentinel https://example.com \
  --ai-payloads \
  --context-analysis \
  --mode thorough \
  --evasion-level 3
```

### Quick Security Assessment
```bash
# Fast scan for immediate results
xss-sentinel https://example.com \
  --mode quick \
  --depth 1 \
  --max-urls 50 \
  --parallel 10
```

### Comprehensive Penetration Test
```bash
# Deep penetration testing with all features
xss-sentinel https://example.com \
  --mode thorough \
  --use-wayback \
  --use-commoncrawl \
  --include-subdomains \
  --scan-js \
  --ai-payloads \
  --context-analysis \
  --evasion-level 3 \
  --parallel 15 \
  --max-urls 10000
```

### Custom Payload Testing
```bash
# Use custom payload file
xss-sentinel https://example.com \
  --payloads custom_payloads.txt \
  --payloads-per-point 10
```

### Enterprise Integration
```bash
# Generate reports for security workflows
xss-sentinel https://example.com \
  --report-format html \
  --output enterprise_reports \
  --cookie "session=abc123; auth=xyz789"
```

## ⚙️ Configuration Options

### Core Options
| Option | Description | Default |
|--------|-------------|---------|
| `url` | Target URL to scan | Required |
| `-d, --depth` | Crawling depth | 2 |
| `-o, --output` | Output directory | reports |
| `--mode` | Scan mode (standard/thorough/quick/passive) | standard |
| `--report-format` | Report format (json/html/txt) | json |

### AI/ML Options
| Option | Description | Default |
|--------|-------------|---------|
| `--ai-payloads` | Use AI-generated payloads | False |
| `--context-analysis` | Use advanced context analysis | False |
| `--evasion-level` | WAF evasion level (0-3) | 1 |
| `--payloads-per-point` | Payloads per injection point | 5 |

### Crawling Options
| Option | Description | Default |
|--------|-------------|---------|
| `--include-subdomains` | Include subdomains | False |
| `--use-wayback` | Use Wayback Machine | False |
| `--use-commoncrawl` | Use CommonCrawl | False |
| `--max-urls` | Maximum URLs to crawl | 10000 |
| `--respect-robots` | Respect robots.txt | False |

### Performance Options
| Option | Description | Default |
|--------|-------------|---------|
| `--parallel` | Parallel scanning threads | 5 |
| `--timeout` | Request timeout (seconds) | 10 |
| `--delay` | Delay between requests | 0.5 |
| `--scan-time-limit` | Maximum scan time | None |

## 📁 Project Structure

```
xss-sentinel/
├── xss_sentinel/
│   ├── ai/                    # AI/ML modules
│   │   ├── adaptive_learning.py
│   │   ├── adversarial_fuzzer.py
│   │   ├── core_ai.py
│   │   └── transformer_generator.py
│   ├── core/                  # Core scanning engine
│   │   ├── crawler.py
│   │   ├── scanner.py
│   │   ├── reporter.py
│   │   └── parallel_scanner.py
│   ├── crawlers/              # Advanced crawling
│   │   ├── advanced_crawler.py
│   │   ├── js_crawler.py
│   │   └── wayback_crawler.py
│   ├── ml/                    # Machine learning
│   │   ├── context_analyzer.py
│   │   ├── model.py
│   │   └── payload_generator.py
│   ├── utils/                 # Utility functions
│   │   ├── browser_verifier.py
│   │   ├── dom_utils.py
│   │   └── http_utils.py
│   └── cli.py                 # Command-line interface
├── data/                      # Payload data
├── reports/                   # Generated reports
├── requirements.txt           # Dependencies
└── setup.py                   # Package configuration
```

## 🔧 Advanced Configuration

### Custom Payload Files
Create custom payload files for specific testing scenarios:
```txt
# custom_payloads.txt
<script>alert('XSS')</script>
javascript:alert('XSS')
<img src=x onerror=alert('XSS')>
```

### Environment Variables
```bash
export XSS_SENTINEL_TIMEOUT=30
export XSS_SENTINEL_USER_AGENT="Custom User Agent"
export XSS_SENTINEL_VERBOSE=1
```

### Configuration Files
Create `config.json` for persistent settings:
```json
{
  "default_mode": "thorough",
  "evasion_level": 2,
  "parallel_workers": 10,
  "timeout": 15,
  "user_agent": "XSS-Sentinel/1.0"
}
```

## 📊 Report Analysis

### JSON Reports
Detailed machine-readable reports with full vulnerability data:
```json
{
  "scan_info": {
    "target": "https://example.com",
    "timestamp": "2025-01-22T10:30:00",
    "duration": 45.2
  },
  "vulnerabilities": [
    {
      "url": "https://example.com/search?q=test",
      "parameter": "q",
      "payload": "<script>alert('XSS')</script>",
      "context": "html",
      "confidence": 0.95
    }
  ]
}
```

### HTML Reports
Interactive web-based reports with:
- Vulnerability charts and statistics
- Searchable vulnerability tables
- Payload analysis and context information
- Export capabilities

## 🛡️ Security Considerations

### Responsible Disclosure
- Always obtain proper authorization before testing
- Respect rate limits and robots.txt
- Use appropriate delays between requests
- Report vulnerabilities through proper channels

### Legal Compliance
- Ensure compliance with local laws and regulations
- Obtain written permission for testing
- Follow responsible disclosure practices
- Respect privacy and data protection laws

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/NOTTIBOY137/xss-sentinel.git
cd xss-sentinel
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest tests/

# Run linting
flake8 xss_sentinel/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python security testing practices
- Inspired by the security research community
- Uses state-of-the-art AI/ML technologies
- Designed for enterprise security workflows

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/NOTTIBOY137/xss-sentinel/issues)
- **Documentation**: [Wiki](https://github.com/NOTTIBOY137/xss-sentinel/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/NOTTIBOY137/xss-sentinel/discussions)

---

**⚠️ Disclaimer**: This tool is for authorized security testing only. Always obtain proper permission before testing any systems. The authors are not responsible for any misuse of this software.
