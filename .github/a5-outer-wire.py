from pathlib import Path

for fn in ['tests/unit/test_tool_gateway_v2.py', 'tests/integration/test_governed_capabilities.py']:
    p = Path(fn)
    s = p.read_text()
    s = s.replace('BROWSER_SECCOMP_PROFILE = os.environ.get("A5_BROWSER_SECCOMP_PROFILE")\n', '')
    s = s.replace('                    browser_docker_seccomp_profile=BROWSER_SECCOMP_PROFILE,\n', '')
    s = s.replace('test ! -e /etc/passwd;', 'test ! -e /host;')
    s = s.replace(
        '                self.assertIn("chromium_native_sandbox", result["browser_isolation"])\n                self.assertIn("playwright_seccomp", result["browser_isolation"])\n',
        '                self.assertIn("outer_container_sandbox", result["browser_isolation"])\n                self.assertIn("docker_builtin_seccomp", result["browser_isolation"])\n',
    )
    s = s.replace(
        "                self.assertIn('chromium_native_sandbox', browser['browser_isolation'])\n                self.assertIn('playwright_seccomp', browser['browser_isolation'])\n",
        "                self.assertIn('outer_container_sandbox', browser['browser_isolation'])\n                self.assertIn('docker_builtin_seccomp', browser['browser_isolation'])\n",
    )
    assert 'BROWSER_SECCOMP_PROFILE' not in s
    assert 'playwright_seccomp' not in s
    assert 'chromium_native_sandbox' not in s
    p.write_text(s)

p = Path('docs/specification/GOVERNED_CAPABILITIES.md')
s = p.read_text()
old_start = 'Where the host supports the full A5 namespace set, the browser worker runs inside user, PID, and network namespaces.'
start = s.index(old_start)
marker = '\n\nBrowser evidence lives under the private `configs/state/browser/` path'
end = s.index(marker, start)
new = '''Where the host supports the full A5 namespace set, the browser worker runs inside user, PID, and network namespaces. Where that namespace set is blocked, GroX uses a separately commissioned Docker browser image as the outer sandbox. The image is built from the Playwright v1.62.0 Noble base pinned by registry digest, installs the matching Python Playwright package, and runs as the dedicated non-root `groxbrowser` user. The Docker boundary uses `network=none`, all Linux capabilities dropped, `no-new-privileges`, Docker built-in seccomp, a read-only root, bounded resources, private tmpfs/shared memory, and only an ephemeral screenshot scratch directory mounted writable. Chromium's nested Linux sandbox is disabled only inside this already-isolated Docker boundary because the hosted qualification environment rejects Chromium's `/proc/self/fdinfo` chroot path. Runtime uses `--pull never` and never builds or downloads the image.\n\nIf neither the outer namespace path nor the pre-provisioned Docker browser boundary is available, browser capture is denied. This keeps network authority in the Gateway rather than silently falling back to an unsandboxed host browser.'''
s = s[:start] + new + s[end:]
s = s.replace('selected browser isolation controls and Chromium sandbox mode;', 'selected browser backend, isolation controls, browser sandbox mode, and container image ID when Docker is used;')
s = s.replace('the resulting image and seccomp profile are host/private operational assets rather than command authority or Vessel memory.', 'the resulting image is a host operational asset rather than command authority or Vessel memory.')
assert 'playwright_seccomp' not in s
p.write_text(s)
