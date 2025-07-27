import asyncio
from playwright.async_api import async_playwright
import os
from datetime import datetime

async def _verify_xss_execution_async(url, payload, param_name, method='get', context=None, output_dir='reports'):
    evidence = {'screenshot': None, 'console': [], 'alert': False}
    os.makedirs(output_dir, exist_ok=True)
    screenshot_path = os.path.join(output_dir, f'xss_verify_{datetime.now().strftime("%Y%m%d_%H%M%S%f")}.png')
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        alert_triggered = False

        async def on_dialog(dialog):
            nonlocal alert_triggered
            if dialog.type == 'alert':
                alert_triggered = True
                await dialog.dismiss()
        page.on('dialog', on_dialog)
        page.on('console', lambda msg: evidence['console'].append(msg.text))

        # Prepare URL or form submission
        if method == 'get':
            from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
            parsed = urlparse(url)
            qs = parse_qs(parsed.query)
            qs[param_name] = [payload]
            new_query = urlencode(qs, doseq=True)
            url_parts = list(parsed)
            url_parts[4] = new_query
            test_url = urlunparse(url_parts)
            await page.goto(test_url)
        else:
            # For POST, navigate to the form page and submit
            await page.goto(url)
            await page.fill(f'input[name="{param_name}"]', payload)
            await page.click('input[type="submit"],button[type="submit"]')

        # Wait for possible XSS execution
        await page.wait_for_timeout(3000)
        await page.screenshot(path=screenshot_path)
        evidence['screenshot'] = screenshot_path
        evidence['alert'] = alert_triggered
        await browser.close()
    return alert_triggered, evidence

def verify_xss_execution(url, payload, param_name, method='get', context=None, output_dir='reports'):
    """
    Synchronously verify if XSS is executed using Playwright. Returns (True/False, evidence dict).
    """
    return asyncio.run(_verify_xss_execution_async(url, payload, param_name, method, context, output_dir)) 