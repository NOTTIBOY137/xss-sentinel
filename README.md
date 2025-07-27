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

### Quick Installation (Recommended)
```bash
# Clone the repository
git clone https://github.com/NOTTIBOY137/xss-sentinel.git
cd xss-sentinel

# Run the automated installation script
python install.py
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/NOTTIBOY137/xss-sentinel.git
cd xss-sentinel

# Install core dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### AI Dependencies (Optional)
For full AI capabilities, install additional dependencies:
```bash
# Install AI/ML dependencies
pip install sentence-transformers transformers torch tensorflow

# Or install with extras
pip install -e .[ai]
```

### Troubleshooting

#### Common Issues

1. **AI modules not available error**
   ```bash
   # Install AI dependencies
   pip install sentence-transformers transformers torch tensorflow
   ```

2. **JavaScript protocol errors**
   - This has been fixed in the latest version
   - The tool now properly validates URLs before making requests

3. **Malformed URL errors**
   - URL validation has been improved
   - Invalid URLs are now skipped automatically

4. **Import errors**
   ```bash
   # Reinstall the package
   pip uninstall xss-sentinel
   pip install -e .
   ```

#### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+ for AI features
- **Storage**: 2GB+ free space (more for AI models)
- **Network**: Stable internet connection for downloading models

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
│   │   ├── parallel_scanner.py
│   │   └── payload_manager.py
│   ├── crawlers/              # Advanced crawling
│   │   ├── advanced_crawler.py
│   │   ├── js_crawler.py
│   │   └── wayback_crawler.py
│   ├── ml/                    # Legacy ML components
│   │   ├── model.py
│   │   ├── payload_generator.py
│   │   └── context_analyzer.py
│   ├── utils/                 # Utility functions
│   │   ├── http_utils.py
│   │   ├── browser_verifier.py
│   │   ├── dom_utils.py
│   │   └── deep_context.py
│   └── cli.py                 # Command-line interface
├── tests/                     # Test suite
├── data/                      # Data files and payloads
├── reports/                   # Generated reports
├── requirements.txt           # Dependencies
├── setup.py                   # Package configuration
├── install.py                 # Installation script
└── README.md                  # This file
```

## 🔧 Development

### Setting up Development Environment
```bash
# Clone and install in development mode
git clone https://github.com/NOTTIBOY137/xss-sentinel.git
cd xss-sentinel
python install.py

# Run tests
pytest tests/

# Code formatting
black xss_sentinel/
flake8 xss_sentinel/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 🛡️ Security

### Responsible Disclosure
- This tool is for authorized security testing only
- Always obtain proper authorization before testing
- Respect rate limits and robots.txt
- Report vulnerabilities responsibly

### Legal Notice
- Use only on systems you own or have explicit permission to test
- The authors are not responsible for misuse of this tool
- Comply with all applicable laws and regulations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

### Getting Help
- Check the [troubleshooting section](#troubleshooting) above
- Review the [configuration options](#configuration-options)
- Open an issue on GitHub for bugs
- Join discussions for feature requests

### Community
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and community support
- **Wiki**: Detailed documentation and guides

## 🚀 Roadmap

### Upcoming Features
- [ ] Enhanced AI model training capabilities
- [ ] Integration with vulnerability management platforms
- [ ] Advanced WAF bypass techniques
- [ ] Real-time collaboration features
- [ ] Mobile application testing support

### Version History
- **v1.0.0**: Initial release with AI-powered XSS detection
- **v1.1.0**: Enhanced URL validation and error handling
- **v1.2.0**: Improved AI dependency management

---

**Made with ❤️ by the XSS Sentinel Team**
