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
    outer_namespace = bool(request.get("outer_namespace", False))
    timeout_ms = int(request["timeout_ms"])
    screenshot = Path(request["screenshot"])
    from playwright.sync_api import sync_playwright
    blocked: list[str] = []
    with sync_playwright() as p:
        bundled = Path(p.chromium.executable_path)
        system = next(
            (shutil.which(x) for x in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable") if shutil.which(x)),
            None,
        )
        if bundled.is_file():
            executable_path = None
            browser_source = "playwright_bundled"
        elif system:
            executable_path = system
            browser_source = "host_system"
        else:
            raise RuntimeError("no pre-provisioned Playwright Chromium or supported system Chromium/Chrome executable")

        args = [
            "--disable-background-networking", "--disable-component-update",
            "--disable-sync", "--disable-extensions", "--no-first-run",
            "--host-resolver-rules=MAP * ~NOTFOUND",
            "--proxy-server=http://127.0.0.1:9",
        ]
        outer_container = bool(request.get("outer_container", False))
        if outer_container:
            # The browser process is already inside the dedicated A5 Docker
            # security boundary: non-root user, network=none, built-in seccomp,
            # all capabilities dropped, no-new-privileges and read-only root.
            # Chromium's nested Linux sandbox is therefore not the authority
            # boundary on this path.
            args.extend(["--no-sandbox", "--disable-dev-shm-usage"])
            sandbox_mode = "outer_container"
            chromium_sandbox = False
        elif os.geteuid() == 0:
            if not outer_namespace:
                raise RuntimeError("root browser worker requires outer namespace isolation")
            args.extend(["--no-sandbox", "--disable-dev-shm-usage"])
            sandbox_mode = "outer_namespace"
            chromium_sandbox = False
        else:
            sandbox_mode = "native"
            chromium_sandbox = True

        browser = p.chromium.launch(
            headless=True,
            executable_path=executable_path,
            args=args,
            chromium_sandbox=chromium_sandbox,
            timeout=timeout_ms,
        )
        context = browser.new_context(accept_downloads=False, service_workers="block")
        page = context.new_page()

        def route_handler(route, req):
            parsed = urlsplit(req.url)
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
        page.screenshot(path=str(screenshot), full_page=True, timeout=timeout_ms)
        rendered = page.content().encode("utf-8")
        result = {
            "title": page.title()[:500],
            "rendered_sha256": hashlib.sha256(rendered).hexdigest(),
            "rendered_bytes": len(rendered),
            "blocked_origins": sorted(set(blocked)),
            "offline_render": True,
            "chromium_sandbox": sandbox_mode,
            "browser_source": browser_source,
        }
        browser.close()
    sys.stdout.write(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
