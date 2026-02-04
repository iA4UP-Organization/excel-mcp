"""Secure path sandboxing for Excel MCP Server - iA4UP Fork."""

from pathlib import Path
from typing import Tuple, Optional
from ..config import is_path_allowed, DANGEROUS_FUNCTIONS, MAX_FILE_SIZE_BYTES, logger


class SecurityError(Exception):
    """Security violation exception."""
    pass


def validate_secure_path(path: str, must_exist: bool = False, check_size: bool = True) -> Path:
    """Validate path with security checks (traversal, sandbox, size)."""
    try:
        clean_path = Path(path).resolve()
    except (ValueError, RuntimeError, OSError):
        raise SecurityError(f"Invalid path format: {path}")
    
    if ".." in str(path):
        raise SecurityError(f"Path traversal not allowed: {path}")
    
    if clean_path.suffix.lower() != ".xlsx":
        raise SecurityError(f"Only .xlsx files allowed, got: {clean_path.suffix}")
    
    if not is_path_allowed(str(clean_path)):
        raise SecurityError(f"Access denied: path outside allowed directories")
    
    if clean_path.is_symlink():
        real_path = clean_path.resolve()
        if not is_path_allowed(str(real_path)):
            raise SecurityError(f"Symlink target outside allowed directories")
    
    if must_exist:
        if not clean_path.exists():
            raise FileNotFoundError(f"File not found: {clean_path}")
        if check_size and clean_path.is_file():
            if clean_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                raise SecurityError(f"File size exceeds limit")
    
    if not must_exist and not clean_path.parent.exists():
        raise SecurityError(f"Parent directory does not exist")
    
    return clean_path


def validate_formula_secure(formula: str) -> Tuple[bool, Optional[str]]:
    """Validate formula - block dangerous functions."""
    if not formula or not formula.startswith("="):
        return False, "Formula must start with '='"
    
    formula_upper = formula.upper()
    for func in DANGEROUS_FUNCTIONS:
        if f"{func}(" in formula_upper:
            return False, f"Blocked function: {func}"
    
    return True, None
