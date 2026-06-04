# msedgedriver

Automated Microsoft Edge WebDriver management for Python.

Stop manually checking your Edge browser version and downloading the matching WebDriver.
`msedgedriver` automatically detects your local Microsoft Edge version, fetches the exact
matching driver from Microsoft's official servers, caches it under `~/.msedgedriver/`, and
**returns its path** so your Selenium scripts can run seamlessly — on Windows, macOS, and Linux.

## Features

* **Zero-Config Automation:** Auto-detects your Edge version (Windows Registry / macOS plist / Linux binary).
* **Cross-Platform:** Windows (win64), macOS Intel (mac64), macOS Apple Silicon (mac64 M1/ARM64), Linux (linux64).
* **Returns Driver Path:** `install()` returns the absolute path to `msedgedriver.exe` — pass it straight to Selenium's `Service()`.
* **Smart Caching:** Downloads only when your browser version changes; subsequent calls are instant.
* **Version Pinning:** Pin a specific driver version with `install(version="125.0.2535.51")`.
* **Custom Install Path:** Override the cache directory with `install(install_path="/my/dir")`.
* **Quiet Mode:** Suppress all output with `install(quiet=True)`.
* **Proper Error Handling:** Raises `MsEdgeDriverException` instead of silently swallowing errors.
* **Logging Support:** Uses Python's `logging` module — integrate with your own log config.

## Installation

```bash
pip install msedgedriver
```

## Quick Start

```python
import msedgedriver
from selenium import webdriver
from selenium.webdriver.edge.service import Service

# Auto-detects Edge version, downloads driver if needed, returns path
path = msedgedriver.install()

driver = webdriver.Edge(service=Service(path))
driver.get("https://github.com")
print(driver.title)
driver.quit()
```

## Full API Reference

### `msedgedriver.install(version=None, install_path=None, quiet=False) -> str`

Downloads and caches the msedgedriver binary. Returns its absolute path.

```python
# Auto-detect version (most common)
path = msedgedriver.install()

# Pin a specific version
path = msedgedriver.install(version="125.0.2535.51")

# Custom cache directory
path = msedgedriver.install(install_path="C:/my/drivers")

# Silent mode (no log output)
path = msedgedriver.install(quiet=True)
```

### `msedgedriver.get_edge_version() -> str`

Returns the installed Microsoft Edge version string.

```python
ver = msedgedriver.get_edge_version()
print(ver)  # e.g. "148.0.3967.96"
```

### `msedgedriver.get_driver_path(version=None, install_path=None) -> str | None`

Returns the path to a cached driver without downloading. Returns `None` if not cached.

```python
path = msedgedriver.get_driver_path()
if path:
    print(f"Already cached at: {path}")
```

### `msedgedriver.cleanup(install_path=None) -> None`

Removes all cached driver versions except the currently installed Edge version.

```python
msedgedriver.cleanup()
```

### `msedgedriver.MsEdgeDriverException`

Exception raised when version detection or download fails.

```python
try:
    path = msedgedriver.install()
except msedgedriver.MsEdgeDriverException as e:
    print(f"Driver setup failed: {e}")
```

## Enable Logging

```python
import logging
logging.basicConfig(level=logging.INFO)

import msedgedriver
msedgedriver.install()
# INFO  msedgedriver: Detected Edge version: 148.0.3967.96
# INFO  msedgedriver: Driver already up-to-date: C:\Users\You\.msedgedriver\148.0.3967.96\msedgedriver.exe
```

## System Requirements

* **Python:** 3.8 or newer
* **OS:** Windows, macOS, or Linux
* **Browser:** Microsoft Edge must be installed

## Version Detection by Platform

| Platform | Method |
|---|---|
| Windows | Windows Registry (`HKCU\SOFTWARE\Microsoft\Edge\BLBeacon`) |
| macOS | `defaults read /Applications/Microsoft Edge.app/Contents/Info.plist` |
| Linux | `microsoft-edge --version` (tries stable, beta, dev channels) |