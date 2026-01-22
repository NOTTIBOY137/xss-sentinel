"""
Visual XSS Detection using Computer Vision
Detects XSS through visual analysis of rendered pages
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import time
import base64
import io

# Optional dependencies with graceful fallback
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False


@dataclass
class VisualDifference:
    """Represents a visual difference detected"""
    diff_score: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    screenshot: Optional[str] = None  # Base64 encoded
    description: str = ""


class VisualXSSDetector:
    """
    Detects XSS vulnerabilities by analyzing visual changes in the browser
    Uses computer vision to identify alert dialogs, DOM mutations, visual anomalies
    """
    
    def __init__(self, headless=True):
        self.headless = headless
        self.baseline_screenshots = {}
        self.alert_patterns = []
        
        if not SELENIUM_AVAILABLE:
            print("[WARN] Selenium not available. Visual detection will be limited.")
        if not CV2_AVAILABLE:
            print("[WARN] OpenCV not available. Screenshot comparison will be limited.")
        
        print("[VISUAL] Visual XSS Detector initialized")
    
    def _init_browser(self) -> Optional[object]:
        """Initialize headless Chrome browser"""
        if not SELENIUM_AVAILABLE:
            return None
        
        try:
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            print(f"[WARN] Could not initialize browser: {e}")
            return None
    
    def detect_xss_visually(self, url: str, payload: str, 
                           injection_method: str = 'url_param',
                           param_name: str = 'q') -> Dict:
        """
        Detect XSS by visual analysis
        
        Args:
            url: Target URL
            payload: XSS payload to test
            injection_method: 'url_param' or 'form'
            param_name: Parameter name to inject into
        
        Returns:
            Detection results with visual evidence
        """
        print(f"[VISUAL] Visually testing: {payload[:50]}...")
        
        if not SELENIUM_AVAILABLE:
            return {
                'vulnerable': False,
                'detection_method': [],
                'visual_evidence': [],
                'confidence': 0.0,
                'note': 'Selenium required for visual detection'
            }
        
        driver = self._init_browser()
        if not driver:
            return {
                'vulnerable': False,
                'detection_method': [],
                'visual_evidence': [],
                'confidence': 0.0,
                'note': 'Could not initialize browser'
            }
        
        results = {
            'vulnerable': False,
            'detection_method': [],
            'visual_evidence': [],
            'confidence': 0.0
        }
        
        try:
            # 1. Capture baseline (clean page)
            if url not in self.baseline_screenshots:
                driver.get(url)
                time.sleep(2)
                self.baseline_screenshots[url] = self._capture_screenshot(driver)
            
            baseline = self.baseline_screenshots[url]
            
            # 2. Inject payload and capture
            if injection_method == 'url_param':
                from urllib.parse import quote
                test_url = f"{url}?{param_name}={quote(payload)}"
                driver.get(test_url)
            else:
                driver.get(url)
                # Find form and inject
                try:
                    input_element = driver.find_element(By.NAME, param_name)
                    input_element.send_keys(payload)
                    input_element.submit()
                except:
                    pass
            
            time.sleep(2)
            injected = self._capture_screenshot(driver)
            
            # 3. Check for alert dialog
            alert_detected = self._detect_alert_dialog(driver)
            if alert_detected:
                results['vulnerable'] = True
                results['detection_method'].append('alert_dialog')
                results['confidence'] += 0.9
                print("   [OK] Alert dialog detected!")
            
            # 4. Visual difference analysis
            if CV2_AVAILABLE and baseline is not None and injected is not None:
                diff_score, differences = self._compare_screenshots(baseline, injected)
                if diff_score > 0.1:  # 10% difference threshold
                    results['vulnerable'] = True
                    results['detection_method'].append('visual_difference')
                    results['confidence'] += min(diff_score, 0.5)
                    results['visual_evidence'] = differences
                    print(f"   [OK] Visual differences detected (score: {diff_score:.3f})")
            
            # 5. DOM mutation analysis
            dom_mutations = self._analyze_dom_mutations(driver, payload)
            if dom_mutations:
                results['vulnerable'] = True
                results['detection_method'].append('dom_mutation')
                results['confidence'] += 0.3
                print(f"   [OK] DOM mutations detected: {len(dom_mutations)}")
            
            # 6. Console error analysis
            console_errors = self._check_console_errors(driver)
            if any('XSS' in err or 'script' in err.lower() for err in console_errors):
                results['confidence'] += 0.2
            
            results['confidence'] = min(results['confidence'], 1.0)
        
        except Exception as e:
            print(f"   [WARN] Error during visual detection: {e}")
        
        finally:
            try:
                driver.quit()
            except:
                pass
        
        return results
    
    def _capture_screenshot(self, driver) -> Optional[np.ndarray]:
        """Capture screenshot as numpy array"""
        if not SELENIUM_AVAILABLE or not PIL_AVAILABLE:
            return None
        
        try:
            screenshot = driver.get_screenshot_as_png()
            image = Image.open(io.BytesIO(screenshot))
            return np.array(image)
        except Exception as e:
            print(f"   [WARN] Screenshot capture failed: {e}")
            return None
    
    def _detect_alert_dialog(self, driver) -> bool:
        """Detect JavaScript alert dialog"""
        if not SELENIUM_AVAILABLE:
            return False
        
        try:
            # Check if alert is present
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()  # Close the alert
            return True
        except:
            return False
    
    def _compare_screenshots(self, img1: np.ndarray, img2: np.ndarray) -> Tuple[float, List[VisualDifference]]:
        """Compare two screenshots and find differences"""
        if not CV2_AVAILABLE:
            return 0.0, []
        
        try:
            # Ensure same size
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Convert to grayscale
            gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
            
            # Compute structural similarity
            diff = cv2.absdiff(gray1, gray2)
            diff_score = np.sum(diff) / (diff.shape[0] * diff.shape[1] * 255.0)
            
            # Find contours of differences
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            differences = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Ignore small differences
                    x, y, w, h = cv2.boundingRect(contour)
                    differences.append(VisualDifference(
                        diff_score=area / (img1.shape[0] * img1.shape[1]),
                        bbox=(x, y, w, h),
                        description=f"Visual change detected at ({x},{y}) size {w}x{h}"
                    ))
            
            return diff_score, differences
        except Exception as e:
            print(f"   [WARN] Screenshot comparison failed: {e}")
            return 0.0, []
    
    def _analyze_dom_mutations(self, driver, payload: str) -> List[Dict]:
        """Analyze DOM mutations caused by payload"""
        if not SELENIUM_AVAILABLE:
            return []
        
        mutations = []
        
        try:
            # Check if payload appears in DOM
            page_source = driver.page_source
            
            # Look for unencoded payload
            if payload in page_source:
                mutations.append({
                    'type': 'unencoded_injection',
                    'payload': payload,
                    'context': 'page_source'
                })
            
            # Check for script tags
            try:
                script_tags = driver.find_elements(By.TAG_NAME, 'script')
                for script in script_tags:
                    script_content = script.get_attribute('innerHTML') or ''
                    if any(kw in script_content for kw in [payload, 'alert', 'eval']):
                        mutations.append({
                            'type': 'script_injection',
                            'content': script_content[:100]
                        })
            except:
                pass
            
            # Check for event handlers
            try:
                elements_with_events = driver.execute_script("""
                    var elements = document.querySelectorAll('*');
                    var withEvents = [];
                    for(var i=0; i<elements.length; i++) {
                        var attrs = elements[i].attributes;
                        for(var j=0; j<attrs.length; j++) {
                            if(attrs[j].name.startsWith('on')) {
                                withEvents.push({
                                    tag: elements[i].tagName,
                                    attribute: attrs[j].name,
                                    value: attrs[j].value
                                });
                            }
                        }
                    }
                    return withEvents;
                """)
                
                for elem in elements_with_events:
                    if payload in elem.get('value', ''):
                        mutations.append({
                            'type': 'event_handler_injection',
                            'tag': elem.get('tag'),
                            'attribute': elem.get('attribute'),
                            'value': elem.get('value')
                        })
            except:
                pass
        
        except Exception as e:
            print(f"   [WARN] DOM analysis error: {e}")
        
        return mutations
    
    def _check_console_errors(self, driver) -> List[str]:
        """Check browser console for errors"""
        if not SELENIUM_AVAILABLE:
            return []
        
        try:
            logs = driver.get_log('browser')
            errors = [log['message'] for log in logs if log['level'] == 'SEVERE']
            return errors
        except:
            return []
    
    def batch_visual_test(self, url: str, payloads: List[str], 
                         injection_point: Dict) -> List[Dict]:
        """Test multiple payloads with visual detection"""
        print(f"\n[VISUAL] Visual Batch Testing: {len(payloads)} payloads")
        
        results = []
        vulnerable_count = 0
        
        for i, payload in enumerate(payloads, 1):
            print(f"\r   Testing payload {i}/{len(payloads)}...", end='', flush=True)
            
            result = self.detect_xss_visually(
                url,
                payload,
                injection_method=injection_point.get('type', 'url_param'),
                param_name=injection_point.get('param_name', 'q')
            )
            
            results.append({
                'payload': payload,
                'result': result
            })
            
            if result['vulnerable']:
                vulnerable_count += 1
        
        print(f"\n\n[VISUAL] Visual testing complete: {vulnerable_count}/{len(payloads)} payloads successful")
        
        return results


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    detector = VisualXSSDetector(headless=True)
    
    # Test single payload
    result = detector.detect_xss_visually(
        url="https://example.com/search",
        payload='<script>alert(1)</script>',
        injection_method='url_param',
        param_name='q'
    )
    
    print(f"\nVulnerable: {result['vulnerable']}")
    print(f"Detection methods: {result['detection_method']}")
    print(f"Confidence: {result['confidence']:.2f}")
