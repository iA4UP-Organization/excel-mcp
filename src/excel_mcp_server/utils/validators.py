"""Validation utilities for Excel operations.

Note: Pour la validation des chemins fichiers, utiliser utils/sandbox.py
qui fournit une couche de sécurité complète (ALLOWED_PATHS, anti path-traversal).
"""

import re
from pathlib import Path

from .sandbox import validate_secure_path, SecurityError


def validate_file_path(path: str, must_exist: bool = False) -> tuple[bool, str | None]:
    """Validate file path for Excel operations.

    Utilise le module sandbox pour la validation sécurisée.

    Args:
        path: File path to validate.
        must_exist: If True, file must exist.

    Returns:
        Tuple of (is_valid, error_message).
    """
    try:
        validate_secure_path(path, must_exist=must_exist)
        return True, None
    except SecurityError as e:
        return False, f"Accès refusé: {str(e)}"
    except FileNotFoundError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Chemin invalide: {str(e)}"


def validate_cell_reference(cell: str) -> tuple[bool, str | None]:
    """Validate Excel cell reference.

    Args:
        cell: Cell reference (e.g., 'A1', 'Z100').

    Returns:
        Tuple of (is_valid, error_message).
    """
    pattern = r"^[A-Z]{1,3}[1-9]\d*$"

    if not re.match(pattern, cell.upper()):
        return False, f"Invalid cell reference: {cell}. Expected format like 'A1' or 'B10'"

    row_match = re.search(r"\d+", cell)
    if row_match:
        row = int(row_match.group())
        if row > 1048576:  # Excel's max row
            return False, f"Row number {row} exceeds Excel's maximum (1048576)"

    return True, None


def validate_range_reference(range_ref: str) -> tuple[bool, str | None]:
    """Validate Excel range reference.

    Args:
        range_ref: Range reference (e.g., 'A1:B10').

    Returns:
        Tuple of (is_valid, error_message).
    """
    pattern = r"^[A-Z]{1,3}[1-9]\d*:[A-Z]{1,3}[1-9]\d*$"

    if not re.match(pattern, range_ref.upper()):
        return False, f"Invalid range reference: {range_ref}. Expected format like 'A1:B10'"

    cells = range_ref.split(":")
    for cell in cells:
        is_valid, error = validate_cell_reference(cell)
        if not is_valid:
            return False, error

    return True, None


def validate_formula(formula: str) -> tuple[bool, str | None]:
    """Validate Excel formula.

    Bloque les fonctions dangereuses qui pourraient:
    - Exécuter du code externe (CALL, REGISTER, EXEC)
    - Envoyer des données vers l'extérieur (WEBSERVICE)
    - Parser du contenu externe (FILTERXML)

    Args:
        formula: Excel formula string.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not formula:
        return False, "Formula cannot be empty"

    if not formula.startswith("="):
        return False, "Formula must start with '='"

    # Fonctions dangereuses bloquées
    dangerous_functions = [
        "CALL",           # Appel DLL externe
        "REGISTER",       # Enregistrement fonction externe
        "EXEC",           # Exécution commande système
        "WEBSERVICE",     # Appel HTTP (fuite de données)
        "FILTERXML",      # Parsing XML externe
    ]

    formula_upper = formula.upper()
    for func in dangerous_functions:
        if func in formula_upper:
            return False, f"Fonction interdite pour raison de sécurité: {func}"

    return True, None


def validate_sheet_name(name: str) -> tuple[bool, str | None]:
    """Validate Excel sheet name.

    Args:
        name: Sheet name to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not name:
        return False, "Sheet name cannot be empty"

    if len(name) > 31:
        return False, "Sheet name cannot exceed 31 characters"

    invalid_chars = [":", "\\", "/", "?", "*", "[", "]"]
    for char in invalid_chars:
        if char in name:
            return False, f"Sheet name cannot contain '{char}'"

    return True, None


def validate_color_hex(color: str) -> tuple[bool, str | None]:
    """Validate hex color code.

    Args:
        color: Hex color code (with or without #).

    Returns:
        Tuple of (is_valid, error_message).
    """
    color = color.lstrip("#")

    if not re.match(r"^[0-9A-Fa-f]{6}$", color):
        return False, f"Invalid hex color: {color}. Expected format like 'FF0000' or '#FF0000'"

    return True, None


def column_letter_to_number(column: str) -> int:
    """Convert column letter to number (A=1, B=2, ..., Z=26, AA=27, etc.)."""
    number = 0
    for char in column.upper():
        number = number * 26 + (ord(char) - ord("A") + 1)
    return number


def column_number_to_letter(number: int) -> str:
    """Convert column number to letter (1=A, 2=B, ..., 26=Z, 27=AA, etc.)."""
    letter = ""
    while number > 0:
        number -= 1
        letter = chr(number % 26 + ord("A")) + letter
        number //= 26
    return letter
