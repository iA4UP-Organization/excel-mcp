"""Configuration sécurisée du serveur MCP Excel.

Gère les chemins autorisés via la variable d'environnement ALLOWED_PATHS.
Si ALLOWED_PATHS n'est pas défini, tous les chemins sont autorisés (mode développement).
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _parse_allowed_paths() -> list[Path]:
    """Parse la variable d'environnement ALLOWED_PATHS.

    Returns:
        Liste de chemins absolus autorisés.
        Liste vide si ALLOWED_PATHS n'est pas défini (mode permissif).
    """
    raw = os.environ.get("ALLOWED_PATHS", "").strip()
    if not raw:
        logger.warning(
            "ALLOWED_PATHS non défini - mode permissif activé. "
            "Définir ALLOWED_PATHS pour restreindre l'accès aux fichiers."
        )
        return []

    paths = []
    for p in raw.split(","):
        p = p.strip()
        if p:
            resolved = Path(p).resolve()
            if resolved.exists():
                paths.append(resolved)
                logger.info(f"Chemin autorisé: {resolved}")
            else:
                logger.warning(f"Chemin autorisé ignoré (n'existe pas): {resolved}")

    if not paths:
        logger.warning("ALLOWED_PATHS défini mais aucun chemin valide trouvé.")

    return paths


# Chemins autorisés (chargés au démarrage)
ALLOWED_PATHS: list[Path] = _parse_allowed_paths()

# Mode sandboxing actif si ALLOWED_PATHS est défini
SANDBOX_ENABLED: bool = len(ALLOWED_PATHS) > 0


def is_path_allowed(path: str) -> bool:
    """Vérifie que le chemin est dans un répertoire autorisé.

    Args:
        path: Chemin à vérifier.

    Returns:
        True si le chemin est autorisé, False sinon.
        Toujours True si ALLOWED_PATHS n'est pas défini.
    """
    if not SANDBOX_ENABLED:
        return True

    try:
        resolved = Path(path).resolve()
        return any(
            resolved == allowed or resolved.is_relative_to(allowed)
            for allowed in ALLOWED_PATHS
        )
    except (ValueError, RuntimeError):
        return False
