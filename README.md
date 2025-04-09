# XSS Sentinel: Advanced AI-Powered XSS Testing Platform

XSS Sentinel is a next-generation cross-site scripting detection tool that leverages AI/ML capabilities to identify and exploit XSS vulnerabilities in web applications.

## Features

- **AI-Powered Payload Generation**: Creates context-aware payloads that evolve based on testing results
- **Advanced Crawling**: Combines standard crawling with Wayback Machine and CommonCrawl for comprehensive URL discovery
- **Context Analysis**: Identifies the exact context where user input is reflected for precise payload generation
- **Parallel Scanning**: Tests multiple injection points simultaneously for faster results
- **Continuous Learning**: Improves detection capabilities over time by learning from successful exploits
- **Enterprise Integration**: Seamlessly integrates with security workflows

## Installation

```bash
# Clone the repository
git clone https://github.com/NOTTIBOY137/xss-sentinel.git
cd xss-sentinel

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .


## Usage
Basic Scan
Copyxss-sentinel https://example.com --ai-payloads --context-analysis
Advanced Scan with Wayback Machine
Copyxss-sentinel https://example.com --mode thorough --use-wayback --scan-js
Quick Scan
Copyxss-sentinel https://example.com --mode quick --evasion-level 2
Scan from URL List
Copyxss-sentinel https://example.com --urls-file targets.txt
Command Line Options
usage: xss-sentinel [-h] [-d DEPTH] [-o OUTPUT] [--no-ml] [-p PAYLOADS] [-m MODEL] [-v]
                   [--include-subdomains] [--use-wayback] [--use-commoncrawl]
                   [--max-urls MAX_URLS] [--respect-robots] [--timeout TIMEOUT]
                   [--delay DELAY] [--max-tests MAX_TESTS] [--user-agent USER_AGENT]
                   [--cookie COOKIE] [--parallel PARALLEL]
                   [--scan-time-limit SCAN_TIME_LIMIT] [--ai-payloads]
                   [--context-analysis] [--evasion-level {0,1,2,3}]
                   [--payloads-per-point PAYLOADS_PER_POINT]
                   [--mode {standard,thorough,quick,passive}] [--scan-js]
                   [--urls-file URLS_FILE]
                   url
