# msedgedriver

Automated Microsoft Edge WebDriver management for Python.

Stop manually checking your Edge browser version and downloading the matching WebDriver. `msedgedriver` automatically detects your local Microsoft Edge version, fetches the exact matching WebDriver from Microsoft's official servers, and extracts it directly into your working directory so your Selenium automation scripts can run seamlessly.

## Features
* **Zero-Config Automation:** Automatically detects your Edge version via the Windows Registry.
* **Version Matching:** Downloads the exact corresponding `msedgedriver.exe` binary.
* **Smart Caching:** Checks your current driver version and only downloads a new one if your browser has updated.

## Installation

You can install the package directly via PyPI:

```bash
pip install msedgedriver
```

## Usage

### Quick Start
To download or update your WebDriver, simply import the package and call the `install()` function. 

```python
import msedgedriver

# Detects your Edge version, downloads the matching driver, 
# and extracts msedgedriver.exe to your current directory.
msedgedriver.install()
```

### Example with Selenium
Here is how it looks integrated into a standard Selenium automation script:

```python
import msedgedriver
from selenium import webdriver
from selenium.webdriver.edge.service import Service

# 1. Fetch the driver
msedgedriver.install()

# 2. Initialize Selenium using the downloaded driver
service = Service('msedgedriver.exe')
driver = webdriver.Edge(service=service)

# 3. Run your automation!
driver.get("[https://github.com](https://github.com)")
print(driver.title)
driver.quit()
```

## System Requirements
* **OS:** Windows (Relies on `winreg` to detect the Edge version).
* **Browser:** Microsoft Edge must be installed on the system.
