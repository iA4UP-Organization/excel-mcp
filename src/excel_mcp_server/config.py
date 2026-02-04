"""
Secure configuration module for Excel MCP Server.
Handles path sandboxing and security settings.

iA4UP Fork - No cloud, no telemetry, 100% local.
"""

import os
from pathlib import Path
from typing import List, Optional

# =============================================================================
# ALLOWED PATHS CONFIGURATION
# =============================================================================

def get_allowed_paths() -> List[Path]:
    """
    Get list of allowed paths from environment variable.
    
    Set ALLOWED_PATHS environment variable with comma-separated paths.
    Example: ALLOWED_PATHS=/home/user/documents,/data/excel
    
    If not set, defaults to user's home directory.
    """
    env_paths = os.environ.get("ALLOWED_PATHS", "")
    
    if env_paths:
        paths = [
            Path(p.strip()).resolve()
            for p in env_paths.split(",")
            if p.strip()
        ]
        return [p for p in paths if p.exists()]
    
    # Default: user's home directory
    home = Path.home()
    return [home] if home.exists() else []


ALLOWED_PATHS: List[Path] = get_allowed_paths()


# =============================================================================
# PATH SECURITY FUNCTIONS
# =============================================================================

def is_path_allowed(path: str) -> bool:
    """
    Check if a path is within allowed directories.
    
    Args:
        path: Path to check (can be relative or absolute)
        
    Returns:
        True if path is within an allowed directory, False otherwise
    """
    try:
        resolved = Path(path).resolve()
        return any(
            _is_subpath(resolved, allowed)
            for allowed in ALLOWED_PATHS
        )
    except (ValueError, RuntimeError, OSError):
        return False


def _is_subpath(path: Path, parent: Path) -> bool:
    """
    Check if path is a subpath of parent.
    Compatible with Python 3.9+ (uses is_relative_to if available).
    """
    try:
        # Python 3.9+
        return path.is_relative_to(parent)
    except AttributeError:
        # Python 3.8 fallback
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False


def get_allowed_paths_str() -> str:
    """Get allowed paths as human-readable string."""
    if not ALLOWED_PATHS:
        return "No paths configured (set ALLOWED_PATHS env variable)"
    return ", ".join(str(p) for p in ALLOWED_PATHS)


# =============================================================================
# SECURITY SETTINGS
# =============================================================================

# Dangerous Excel functions that could leak data or execute code
DANGEROUS_FUNCTIONS = [
    "CALL",           # Call external DLL
    "REGISTER",       # Register function
    "EXEC",           # Execute command
    "WEBSERVICE",     # HTTP request (data leak)
    "FILTERXML",      # External XML parsing
    "RTD",            # Real-time data (external connection)
]

# Maximum file size (100MB by default)
MAX_FILE_SIZE_MB = int(os.environ.get("MAX_FILE_SIZE_MB", "100"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Debug mode (disabled by default for security)
DEBUG_MODE = os.environ.get("MCP_DEBUG", "false").lower() == "true"


# =============================================================================
# LOGGING (local only, no external services)
# =============================================================================

import logging

def setup_logging() -> logging.Logger:
    """Setup local-only logging (no external services)."""
    log_level = os.environ.get("MCP_LOG_LEVEL", "INFO").upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]  # Local console only
    )
    
    return logging.getLogger("excel_mcp_server")


logger = setup_logging()


# =============================================================================
# STARTUP INFO
# =============================================================================

def log_startup_info():
    """Log configuration info at startup."""
    logger.info("=" * 50)
    logger.info("Excel MCP Server (Secure Fork by iA4UP)")
    logger.info("=" * 50)
    logger.info(f"Allowed paths: {get_allowed_paths_str()}")
    logger.info(f"Max file size: {MAX_FILE_SIZE_MB}MB")
    logger.info(f"Debug mode: {DEBUG_MODE}")
    logger.info(f"Blocked functions: {', '.join(DANGEROUS_FUNCTIONS)}")
    logger.info("=" * 50)
