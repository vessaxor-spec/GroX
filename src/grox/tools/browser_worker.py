from __future__ import annotations

import hashlib
import json
from pathlib import Path
import os
import shutil
import sys
from urllib.parse import urlsplit


def origin(value: str) -> str:
    p = urlsplit(value)
    if p.scheme not in {"http", "https"} or not p.hostname:
        return ""
    scheme = p.scheme.lower(); host = p.hostname.lower(); port = p.port
    default = 80 if scheme == "http" else 443
    return f"{scheme}://{host}" if port is None or port == default else f"{scheme}://{host}:{port}"


def main() -> int:
    request = json.loads(sys.stdin.read())
    html = str(request["html"])
    timeout_ms = int(request["timeout_ms"])
    screenshot = Path(request["screenshot"])
    executable = next((shutil.which(x) for x in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable") if shutil.which(x)), None)
    if not executable:
        raise RuntimeError("no supported Chromium/Chrome executable on host")
    from playwright.sync_api import sync_playwright
    blocked: list[str] = []
    with sync_playwright() as p:
        args=["--disable-background-networking", "--disable-component-update", "--disable-sync", "--disable-extensions", "--no-first-run"]
        if os.geteuid() == 0:
            # The worker already runs inside a dedicated user/PID/network namespace.
            args.extend(["--no-sandbox", "--disable-dev-shm-usage"])
        browser = p.chromium.launch(headless=True, executable_path=executable, args=args)
        context = browser.new_context(accept_downloads=False, service_workers="block")
        page = context.new_page()
        def route_handler(route, req):
            parsed=urlsplit(req.url)
            if parsed.scheme in {"data", "blob", "about"}:
                route.continue_()
                return
            o = origin(req.url)
            blocked.append(o or f"scheme:{parsed.scheme or 'unknown'}")
            route.abort()
        page.route("**/*", route_handler)
        page.set_content(html, wait_until="load", timeout=timeout_ms)
        page.wait_for_timeout(100)
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot), full_page=True)
        rendered = page.content().encode("utf-8")
        result = {
            "title": page.title()[:500],
            "rendered_sha256": hashlib.sha256(rendered).hexdigest(),
            "rendered_bytes": len(rendered),
            "blocked_origins": sorted(set(blocked)),
            "offline_render": True,
        }
        browser.close()
    sys.stdout.write(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
