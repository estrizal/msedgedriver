"""
Verification test for msedgedriver v0.1.0
Tests:
  1. get_edge_version()         — detects installed Edge version
  2. install()                  — downloads driver, returns path
  3. install() (cached)         — skips download on second call
  4. install(quiet=True)        — no output, still returns path
  5. install(version=...)       — version pinning
  6. get_driver_path()          — returns cached path without downloading
  7. cleanup()                  — removes old versions from cache
  8. MsEdgeDriverException      — is importable and is an Exception
  9. Selenium integration        — launches Edge, navigates, quits
 10. install_path override       — custom cache directory
"""

import logging
import os
import sys
import shutil
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path

# ── Enable logging so we can see what the library does ──────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

PASS = " [PASS]"
FAIL = " [FAIL]"
HEAD = ""
RESET = ""

results = []

def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    tag = "[OK]" if condition else "[!!]"
    print(f"  {tag}{status}  {name}" + (f"  ->  {detail}" if detail else ""))
    results.append((name, condition))


# ── Import ───────────────────────────────────────────────────────────────────
print(f"\n{HEAD}{'='*60}\n  msedgedriver Verification Suite  (selenium 4.2.0)\n{'='*60}{RESET}\n")

try:
    import msedgedriver
    from msedgedriver import (
        install, get_edge_version, get_driver_path,
        cleanup, MsEdgeDriverException,
    )
    check("Import msedgedriver", True, f"version={msedgedriver.__version__}")
except Exception as e:
    check("Import msedgedriver", False, str(e))
    sys.exit(1)

# ── Selenium version ─────────────────────────────────────────────────────────
try:
    import selenium
    check("Selenium version is 4.2.0", selenium.__version__ == "4.2.0", selenium.__version__)
except ImportError as e:
    check("Selenium import", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{HEAD}[1] get_edge_version(){RESET}")
# ─────────────────────────────────────────────────────────────────────────────
try:
    ver = get_edge_version()
    check("Returns a non-empty string", isinstance(ver, str) and len(ver) > 0, ver)
    parts = ver.split(".")
    check("Version has 4 dot-separated parts", len(parts) == 4, ver)
    check("All parts are numeric", all(p.isdigit() for p in parts), ver)
    EDGE_VERSION = ver
except MsEdgeDriverException as e:
    check("get_edge_version() did not raise", False, str(e))
    EDGE_VERSION = None

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{HEAD}[2] install() — first download{RESET}")
# ─────────────────────────────────────────────────────────────────────────────
CUSTOM_CACHE = Path.home() / ".msedgedriver_test_cache"
# Clean up any previous test run
if CUSTOM_CACHE.exists():
    shutil.rmtree(CUSTOM_CACHE)

try:
    driver_path = install(install_path=str(CUSTOM_CACHE))
    check("Returns a string", isinstance(driver_path, str), driver_path)
    check("Path exists on disk", os.path.isfile(driver_path), driver_path)
    check("File is msedgedriver.exe", driver_path.endswith("msedgedriver.exe"), driver_path)
    DRIVER_PATH = driver_path
except MsEdgeDriverException as e:
    check("install() did not raise MsEdgeDriverException", False, str(e))
    DRIVER_PATH = None
except Exception as e:
    check("install() did not raise unexpected exception", False, str(e))
    DRIVER_PATH = None

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{HEAD}[3] install() — cached (should skip download){RESET}")
# ─────────────────────────────────────────────────────────────────────────────
if DRIVER_PATH:
    try:
        import time
        t0 = time.time()
        path2 = install(install_path=str(CUSTOM_CACHE))
        elapsed = time.time() - t0
        check("Returns same path", path2 == DRIVER_PATH, path2)
        check("Cache hit is fast (<2 s)", elapsed < 2.0, f"{elapsed:.2f}s")
    except Exception as e:
        check("Cached install() did not raise", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{HEAD}[4] install(quiet=True){RESET}")
# ─────────────────────────────────────────────────────────────────────────────
if CUSTOM_CACHE.exists():
    try:
        path_q = install(quiet=True, install_path=str(CUSTOM_CACHE))
        check("quiet=True still returns path", isinstance(path_q, str) and path_q, path_q)
    except Exception as e:
        check("install(quiet=True) did not raise", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{HEAD}[5] install(version=...) — version pinning{RESET}")
# ─────────────────────────────────────────────────────────────────────────────
# Use the same version we already downloaded — so it should be instant (cached)
if EDGE_VERSION:
    try:
        path_v = install(version=EDGE_VERSION, install_path=str(CUSTOM_CACHE))
        check("Pinned version returns path", isinstance(path_v, str) and path_v, path_v)
        check("Pinned path exists on disk", os.path.isfile(path_v), path_v)
    except Exception as e:
        check("Pinned install() did not raise", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{HEAD}[6] get_driver_path(){RESET}")
# ─────────────────────────────────────────────────────────────────────────────
try:
    cached = get_driver_path(install_path=str(CUSTOM_CACHE))
    check("Returns a string when cached", isinstance(cached, str), cached)
    check("Path matches install() path", cached == DRIVER_PATH, cached)
except Exception as e:
    check("get_driver_path() did not raise", False, str(e))

try:
    not_cached = get_driver_path(version="0.0.0.0", install_path=str(CUSTOM_CACHE))
    check("Returns None for non-existent version", not_cached is None, str(not_cached))
except Exception as e:
    check("get_driver_path(missing) did not raise", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{HEAD}[7] MsEdgeDriverException{RESET}")
# ─────────────────────────────────────────────────────────────────────────────
check("Is a subclass of Exception", issubclass(MsEdgeDriverException, Exception))
try:
    raise MsEdgeDriverException("test error")
except MsEdgeDriverException as e:
    check("Can be raised and caught", str(e) == "test error", str(e))

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{HEAD}[8] cleanup(){RESET}")
# ─────────────────────────────────────────────────────────────────────────────
# Create a fake old version folder to test cleanup
fake_old = CUSTOM_CACHE / "1.0.0.0"
fake_old.mkdir(parents=True, exist_ok=True)
(fake_old / "msedgedriver.exe").write_bytes(b"fake")

try:
    cleanup(install_path=str(CUSTOM_CACHE))
    check("Old version folder removed", not fake_old.exists(), str(fake_old))
    check("Current version folder kept", os.path.isfile(DRIVER_PATH or ""), DRIVER_PATH)
except Exception as e:
    check("cleanup() did not raise", False, str(e))

# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{HEAD}[9] Selenium 4.2.0 Integration — Launch Edge{RESET}")
# ─────────────────────────────────────────────────────────────────────────────
if DRIVER_PATH:
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options

        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        service = Service(executable_path=DRIVER_PATH)
        driver = webdriver.Edge(service=service, options=opts)

        check("webdriver.Edge launched", True, "headless mode")

        driver.get("https://example.com")
        title = driver.title
        check("Navigated to example.com", "Example" in title, f'title="{title}"')

        current_url = driver.current_url
        check("URL is correct", "example.com" in current_url, current_url)

        driver.quit()
        check("driver.quit() succeeded", True)

    except Exception as e:
        check("Selenium integration", False, str(e))
else:
    print("  ⚠  Skipped — driver binary not available")

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{HEAD}{'='*60}\n  Results\n{'='*60}{RESET}")
passed = sum(1 for _, ok in results if ok)
failed = sum(1 for _, ok in results if not ok)
print(f"  {passed} passed  |  {failed} failed  |  {len(results)} total\n")

if failed:
    print("Failed tests:")
    for name, ok in results:
        if not ok:
            print(f"  [!!]  {name}")
    sys.exit(1)
else:
    print(f"  {PASS}  All tests passed!")
    sys.exit(0)
