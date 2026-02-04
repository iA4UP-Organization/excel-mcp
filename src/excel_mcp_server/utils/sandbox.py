"""Module de sandboxing pour la validation sécurisée des chemins.

Protège contre:
- Path traversal (../, ..\\)
- Accès hors zones autorisées (ALLOWED_PATHS)
- Extensions non .xlsx
- Liens symboliques sortants
"""

import logging
from pathlib import Path

from ..config import is_path_allowed, SANDBOX_ENABLED

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Erreur de sécurité - accès non autorisé."""
    pass


def validate_secure_path(path: str, must_exist: bool = False) -> Path:
    """Valide un chemin de manière sécurisée.

    Effectue les vérifications suivantes:
    1. Détection de path traversal (../ ou ..\\)
    2. Vérification de l'extension (.xlsx uniquement)
    3. Vérification que le chemin est dans ALLOWED_PATHS
    4. Vérification que le répertoire parent existe
    5. Détection des liens symboliques sortants

    Args:
        path: Chemin du fichier à valider.
        must_exist: Si True, le fichier doit exister.

    Returns:
        Chemin résolu et validé.

    Raises:
        SecurityError: Si le chemin ne passe pas les validations de sécurité.
        FileNotFoundError: Si must_exist=True et le fichier n'existe pas.
    """
    if not path or not path.strip():
        raise SecurityError("Le chemin ne peut pas être vide.")

    # 1. Bloquer path traversal explicite
    if ".." in str(path):
        logger.warning(f"Path traversal détecté: {path}")
        raise SecurityError(f"Path traversal détecté: {path}")

    try:
        clean_path = Path(path).resolve()
    except (ValueError, RuntimeError) as e:
        raise SecurityError(f"Chemin invalide: {path} ({e})")

    # 2. Vérifier l'extension
    if clean_path.suffix.lower() != ".xlsx":
        raise SecurityError(
            f"Extension non autorisée: '{clean_path.suffix}'. "
            f"Seuls les fichiers .xlsx sont autorisés."
        )

    # 3. Vérifier que le chemin est dans ALLOWED_PATHS
    if SANDBOX_ENABLED and not is_path_allowed(str(clean_path)):
        logger.warning(f"Accès refusé - chemin hors zone autorisée: {clean_path}")
        raise SecurityError(
            f"Chemin hors zone autorisée: {clean_path}. "
            f"Vérifiez la variable d'environnement ALLOWED_PATHS."
        )

    # 4. Vérifier que le répertoire parent existe
    if not clean_path.parent.exists():
        raise SecurityError(f"Le répertoire parent n'existe pas: {clean_path.parent}")

    # 5. Vérifier existence si requis
    if must_exist and not clean_path.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {clean_path}")

    # 6. Vérifier les liens symboliques
    if clean_path.exists() and clean_path.is_symlink():
        real_path = clean_path.resolve()
        if SANDBOX_ENABLED and not is_path_allowed(str(real_path)):
            logger.warning(f"Lien symbolique vers zone non autorisée: {path} -> {real_path}")
            raise SecurityError(
                f"Lien symbolique vers zone non autorisée: {path}"
            )

    return clean_path
