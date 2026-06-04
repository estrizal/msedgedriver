"""
msedgedriver - Automated Microsoft Edge WebDriver management for Python.

Automatically detects your Edge browser version, downloads the matching
msedgedriver binary, caches it under ~/.msedgedriver/, and returns its
absolute path so you can pass it straight to Selenium.

Public API
----------
install(version, install_path, quiet)  -> str   (path to driver binary)
get_edge_version()                     -> str   (e.g. "125.0.2535.51")
get_driver_path(version, install_path) -> str | None
cleanup(install_path)                  -> None

Note: Microsoft dropped 32-bit Edge support. Only 64-bit platforms are
      supported (win64, mac64, mac64_m1, linux64).
"""

import logging
import os
import platform
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

__version__ = "0.1.0"
__author__ = "estriadi (Aditya Maurya)"
__all__ = [
    "install",
    "get_edge_version",
    "get_driver_path",
    "cleanup",
    "MsEdgeDriverException",
]

log = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# Custom exception
# ──────────────────────────────────────────────────────────────────────────────

class MsEdgeDriverException(Exception):
    """Raised when msedgedriver cannot detect, download, or install the driver."""


# ──────────────────────────────────────────────────────────────────────────────
# Internal platform helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_platform() -> str:
    """Return one of: 'win', 'mac', 'mac_m1', 'linux'."""
    system = platform.system()
    if system == "Windows":
        return "win"
    elif system == "Darwin":
        return "mac_m1" if platform.machine() == "arm64" else "mac"
    elif system == "Linux":
        return "linux"
    else:
        raise MsEdgeDriverException(
            f"Unsupported operating system: {system!r}. "
            "msedgedriver supports Windows, macOS, and Linux."
        )


# Mapping: platform key -> (zip filename, driver binary name inside zip)
_PLATFORM_MAP = {
    "win":    ("edgedriver_win64.zip",    "msedgedriver.exe"),
    "mac":    ("edgedriver_mac64.zip",    "msedgedriver"),
    "mac_m1": ("edgedriver_mac64_m1.zip", "msedgedriver"),
    "linux":  ("edgedriver_linux64.zip",  "msedgedriver"),
}


def _driver_binary_name() -> str:
    return _PLATFORM_MAP[_get_platform()][1]


def _download_url_and_zip(version: str, plat: str):
    zip_name, _ = _PLATFORM_MAP[plat]
    url = f"https://msedgedriver.microsoft.com/{version}/{zip_name}"
    return url, zip_name


# ──────────────────────────────────────────────────────────────────────────────
# Edge version detection  (cross-platform)
# ──────────────────────────────────────────────────────────────────────────────

def get_edge_version() -> str:
    """
    Detect the installed Microsoft Edge browser version.

    Returns
    -------
    str
        Full version string, e.g. ``"125.0.2535.51"``.

    Raises
    ------
    MsEdgeDriverException
        If the Edge version cannot be determined.
    """
    plat = _get_platform()
    if plat == "win":
        return _edge_version_windows()
    elif plat in ("mac", "mac_m1"):
        return _edge_version_mac()
    else:
        return _edge_version_linux()


def _edge_version_windows() -> str:
    import winreg  # only available on Windows

    # Primary key: per-user BLBeacon (most reliable for stable channel)
    candidates = [
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Edge\BLBeacon",               "version"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Edge\BLBeacon",               "version"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Edge\BLBeacon",   "version"),
    ]
    for hive, key_path, value_name in candidates:
        try:
            with winreg.OpenKey(hive, key_path) as key:
                version, _ = winreg.QueryValueEx(key, value_name)
                if version:
                    return version
        except OSError:
            continue

    raise MsEdgeDriverException(
        "Could not detect Microsoft Edge version from the Windows Registry. "
        "Is Microsoft Edge installed?"
    )


def _edge_version_mac() -> str:
    app_path = "/Applications/Microsoft Edge.app"
    plist = os.path.join(app_path, "Contents", "Info.plist")

    if not os.path.exists(plist):
        raise MsEdgeDriverException(
            f"Microsoft Edge not found at {app_path!r}. "
            "Is Microsoft Edge installed?"
        )
    try:
        result = subprocess.run(
            ["defaults", "read", plist, "CFBundleShortVersionString"],
            capture_output=True, text=True, check=True,
        )
        version = result.stdout.strip()
        if version:
            return version
    except subprocess.CalledProcessError as exc:
        raise MsEdgeDriverException(
            "Could not read Edge version from macOS plist."
        ) from exc

    raise MsEdgeDriverException("Edge version string was empty on macOS.")


def _edge_version_linux() -> str:
    binaries = [
        "microsoft-edge",
        "microsoft-edge-stable",
        "microsoft-edge-beta",
        "microsoft-edge-dev",
    ]
    for binary in binaries:
        if not shutil.which(binary):
            continue
        try:
            result = subprocess.run(
                [binary, "--version"],
                capture_output=True, text=True, check=True,
            )
            # Typical output: "Microsoft Edge 125.0.2535.51 \n"
            parts = result.stdout.strip().split()
            if len(parts) >= 3:
                return parts[2]
        except subprocess.CalledProcessError:
            continue

    raise MsEdgeDriverException(
        "Could not detect Microsoft Edge version on Linux. "
        "Is microsoft-edge installed and on PATH?"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Cache / path helpers
# ──────────────────────────────────────────────────────────────────────────────

def _default_cache_dir() -> Path:
    """~/.msedgedriver  — no admin rights required."""
    return Path.home() / ".msedgedriver"


def _versioned_driver_path(version: str, base: Path) -> Path:
    return base / version / _driver_binary_name()


def get_driver_path(
    version: Optional[str] = None,
    install_path: Optional[str] = None,
) -> Optional[str]:
    """
    Return the path to a cached msedgedriver binary, or ``None`` if not found.

    Parameters
    ----------
    version : str, optional
        Driver version to look for. Defaults to the installed Edge version.
    install_path : str, optional
        Cache directory. Defaults to ``~/.msedgedriver``.

    Returns
    -------
    str or None
        Absolute path to the binary if it exists, otherwise ``None``.
    """
    try:
        ver = version or get_edge_version()
    except MsEdgeDriverException:
        return None

    base = Path(install_path) if install_path else _default_cache_dir()
    path = _versioned_driver_path(ver, base)
    return str(path) if path.exists() else None


# ──────────────────────────────────────────────────────────────────────────────
# Download & install
# ──────────────────────────────────────────────────────────────────────────────

def install(
    version: Optional[str] = None,
    install_path: Optional[str] = None,
    quiet: bool = False,
) -> str:
    """
    Download and install the msedgedriver binary.

    Parameters
    ----------
    version : str, optional
        Pin a specific driver version, e.g. ``"125.0.2535.51"``.
        Defaults to the version of Edge installed on this machine.
    install_path : str, optional
        Directory in which to cache the downloaded driver.
        Defaults to ``~/.msedgedriver/<version>/``.
    quiet : bool, optional
        If ``True``, suppress all logging output. Default ``False``.

    Returns
    -------
    str
        Absolute path to the ``msedgedriver`` (or ``msedgedriver.exe``) binary.

    Raises
    ------
    MsEdgeDriverException
        If the Edge version cannot be detected or the driver download fails.

    Example
    -------
    >>> import msedgedriver
    >>> from selenium import webdriver
    >>> from selenium.webdriver.edge.service import Service
    >>>
    >>> path = msedgedriver.install()
    >>> driver = webdriver.Edge(service=Service(path))
    """
    _lvl = logging.CRITICAL if quiet else logging.NOTSET
    logging.disable(_lvl)

    try:
        # 1. Resolve version
        ver = version or get_edge_version()
        log.info("Detected Edge version: %s", ver)

        # 2. Resolve install path
        base = Path(install_path) if install_path else _default_cache_dir()
        driver_path = _versioned_driver_path(ver, base)

        # 3. Already cached?
        if driver_path.exists():
            log.info("Driver is already up-to-date: %s", driver_path)
            return str(driver_path)

        # 4. Download
        plat = _get_platform()
        url, zip_name = _download_url_and_zip(ver, plat)
        zip_path = base / zip_name

        base.mkdir(parents=True, exist_ok=True)
        driver_path.parent.mkdir(parents=True, exist_ok=True)

        log.info("Downloading msedgedriver %s for %s ...", ver, plat)
        log.info("URL: %s", url)
        try:
            urllib.request.urlretrieve(url, zip_path)
        except Exception as exc:
            raise MsEdgeDriverException(
                f"Failed to download msedgedriver from {url!r}. "
                "Check your internet connection and that the version exists."
            ) from exc
        log.info("Download complete.")

        # 5. Extract driver binary from zip
        binary_name = _driver_binary_name()
        log.info("Extracting %s ...", binary_name)
        with ZipFile(zip_path, "r") as zf:
            members = zf.namelist()
            if binary_name in members:
                # Flat zip: extract just the binary
                zf.extract(binary_name, driver_path.parent)
            else:
                # Some builds nest inside a folder; find it
                nested = next(
                    (m for m in members if m.endswith("/" + binary_name)), None
                )
                if nested:
                    data = zf.read(nested)
                    driver_path.write_bytes(data)
                else:
                    # Last resort: extract everything
                    zf.extractall(driver_path.parent)

        # 6. Make executable on Unix
        if plat != "win" and driver_path.exists():
            driver_path.chmod(driver_path.stat().st_mode | 0o111)

        # 7. Cleanup zip file
        try:
            zip_path.unlink()
        except OSError:
            pass

        if not driver_path.exists():
            raise MsEdgeDriverException(
                f"Extraction finished but driver binary not found at {driver_path}. "
                "The zip may have an unexpected structure."
            )

        log.info("msedgedriver ready at: %s", driver_path)
        return str(driver_path)

    finally:
        # Always re-enable logging, even if quiet=True
        logging.disable(logging.NOTSET)


# ──────────────────────────────────────────────────────────────────────────────
# Cleanup
# ──────────────────────────────────────────────────────────────────────────────

def cleanup(install_path: Optional[str] = None) -> None:
    """
    Remove all cached msedgedriver versions except the currently installed one.

    Parameters
    ----------
    install_path : str, optional
        Cache directory. Defaults to ``~/.msedgedriver``.

    Raises
    ------
    MsEdgeDriverException
        If the current Edge version cannot be detected.
    """
    base = Path(install_path) if install_path else _default_cache_dir()
    current = get_edge_version()
    log.info("Cleaning up old driver versions in %s (keeping %s) ...", base, current)

    if not base.exists():
        log.info("Cache directory %s does not exist — nothing to clean.", base)
        return

    removed = 0
    for child in base.iterdir():
        if child.is_dir() and child.name != current:
            shutil.rmtree(child, ignore_errors=True)
            log.info("Removed old version: %s", child.name)
            removed += 1

    log.info("Cleanup complete. Removed %d old version(s).", removed)
