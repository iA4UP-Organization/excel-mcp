# MCP Excel Server - Projet Custom iA4UP

> Fork sécurisé du serveur MCP Excel pour manipulation locale de fichiers .xlsx
> Sans télémétrie, sans cloud, 100% privé

## 📋 Origine du Projet

**Source** : [mort-lab/excel-mcp](https://github.com/mort-lab/excel-mcp)  
**Licence** : MIT  
**Analyse effectuée** : 04/02/2025  
**Auteur original** : Martin Irurozki

### Ce qu'on garde ✅

- Core openpyxl (lecture/écriture Excel native Python)
- Validation Pydantic des entrées
- Structure FastMCP pour le protocole MCP
- Blocage des formules dangereuses (CALL, REGISTER, EXEC)
- 20 outils : workbook, sheets, cells, formatting
- Tests unitaires existants

### Ce qu'on rejette ❌

- `server_smithery.py` (mode cloud - envoie les fichiers sur leurs serveurs)
- Dépendance `smithery>=0.4.2` (télémétrie potentielle)
- Configuration Smithery dans pyproject.toml
- Toute référence à smithery.ai

### Ce qu'on ajoute 🛡️

- Sandboxing des répertoires (ALLOWED_PATHS)
- Validation renforcée anti path-traversal
- Mode 100% offline garanti
- Configuration pour VPS Hostinger / N8N
- Support Docker isolé

---

## 🏗️ Architecture Cible

```
excel-mcp-secure/
├── src/
│   └── excel_mcp_server/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py          # Serveur MCP principal (sans Smithery)
│       ├── models.py          # Modèles Pydantic
│       ├── config.py          # 🆕 Configuration sécurisée
│       ├── operations/
│       │   ├── __init__.py
│       │   ├── workbook.py
│       │   ├── sheet.py
│       │   ├── cell.py
│       │   └── formatting.py
│       └── utils/
│           ├── __init__.py
│           ├── validators.py
│           └── sandbox.py     # 🆕 Sandboxing des chemins
├── tests/
├── pyproject.toml             # Sans Smithery
├── Dockerfile                 # 🆕 Pour VPS/N8N
├── docker-compose.yml         # 🆕 Stack complète
├── README.md
└── CLAUDE.md                  # Ce fichier
```

---

## 🔧 Scénarios d'Utilisation

### 1. Claude Desktop (Local - Recommandé pour démarrer)

**Fichier config** :
- MacOS : `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows : `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "excel": {
      "command": "python",
      "args": ["-m", "excel_mcp_server"],
      "env": {
        "ALLOWED_PATHS": "G:/Mon Drive/iA4UP,G:/Mon Drive/Savpro"
      }
    }
  }
}
```

**Usage** : Parler directement à Claude Desktop pour manipuler les fichiers Excel.

### 2. N8N sur VPS Hostinger (Automatisation)

```yaml
# docker-compose.yml (à ajouter à ta stack N8N existante)
services:
  excel-mcp:
    build: ./excel-mcp-secure
    container_name: excel-mcp
    restart: unless-stopped
    volumes:
      - /data/excel:/data/excel:rw
    environment:
      - ALLOWED_PATHS=/data/excel
      - MCP_MODE=http
      - MCP_PORT=3100
    ports:
      - "3100:3100"
    networks:
      - n8n-network

networks:
  n8n-network:
    external: true
```

**Intégration N8N** : Appeler le serveur MCP via HTTP Request node.

### 3. Claude.ai via Tunnel Sécurisé (Avancé)

```bash
# Option A : Cloudflare Tunnel (gratuit, recommandé)
cloudflared tunnel --url http://localhost:3100

# Option B : ngrok (simple mais limité)
ngrok http 3100
```

---

## 📦 Dépendances (version sécurisée)

```toml
[project]
name = "excel-mcp-server-secure"
version = "0.1.0"
description = "Serveur MCP Excel sécurisé - Fork sans télémétrie"
requires-python = ">=3.10"

dependencies = [
    "mcp>=1.15.0",
    "fastmcp>=2.0.0",
    "openpyxl>=3.1.0",
    "pydantic>=2.0.0",
    # PAS de smithery - supprimé volontairement
]

[project.scripts]
excel-mcp-server = "excel_mcp_server:main"
```

---

## 🛠️ Outils Disponibles (20 tools)

### Workbook Operations (3 outils)

| Tool | Description | Paramètres |
|------|-------------|------------|
| `create_workbook` | Créer un nouveau fichier .xlsx | `file_path` |
| `get_workbook_info` | Métadonnées du fichier | `file_path` |
| `list_sheets` | Lister les feuilles | `file_path` |

### Sheet Operations (4 outils)

| Tool | Description | Paramètres |
|------|-------------|------------|
| `create_sheet` | Créer une feuille | `workbook_path`, `sheet_name`, `index?` |
| `delete_sheet` | Supprimer une feuille | `workbook_path`, `sheet_name` |
| `rename_sheet` | Renommer une feuille | `workbook_path`, `old_name`, `new_name` |
| `copy_sheet` | Copier une feuille | `workbook_path`, `source_sheet`, `new_name` |

### Cell Operations (5 outils)

| Tool | Description | Paramètres |
|------|-------------|------------|
| `write_cell` | Écrire dans une cellule | `workbook_path`, `sheet_name`, `cell`, `value` |
| `read_cell` | Lire une cellule | `workbook_path`, `sheet_name`, `cell` |
| `write_range` | Écrire une plage | `workbook_path`, `sheet_name`, `start_cell`, `data[][]` |
| `read_range` | Lire une plage | `workbook_path`, `sheet_name`, `range_ref` |
| `write_formula` | Écrire une formule | `workbook_path`, `sheet_name`, `cell`, `formula` |

### Formatting Operations (5 outils)

| Tool | Description | Paramètres |
|------|-------------|------------|
| `format_font` | Police (gras, italique, couleur, taille) | `workbook_path`, `sheet_name`, `range_ref`, options... |
| `format_fill` | Couleur de fond | `workbook_path`, `sheet_name`, `range_ref`, `color` |
| `format_border` | Bordures | `workbook_path`, `sheet_name`, `range_ref`, `style`, `sides[]` |
| `format_alignment` | Alignement | `workbook_path`, `sheet_name`, `range_ref`, `horizontal`, `vertical` |
| `format_number` | Format nombre/date/monnaie | `workbook_path`, `sheet_name`, `range_ref`, `format_string` |

---

## 🔒 Sécurité Implémentée

### 1. Sandboxing des Chemins (NOUVEAU)

```python
# config.py
import os
from pathlib import Path

ALLOWED_PATHS = [
    Path(p.strip()).resolve() 
    for p in os.environ.get("ALLOWED_PATHS", "").split(",") 
    if p.strip()
]

def is_path_allowed(path: str) -> bool:
    """Vérifie que le chemin est dans un répertoire autorisé."""
    try:
        resolved = Path(path).resolve()
        return any(
            resolved.is_relative_to(allowed)
            for allowed in ALLOWED_PATHS
        )
    except (ValueError, RuntimeError):
        return False
```

### 2. Validation Anti Path-Traversal (RENFORCÉ)

```python
# utils/sandbox.py
from pathlib import Path
from .config import is_path_allowed

class SecurityError(Exception):
    """Erreur de sécurité - accès non autorisé."""
    pass

def validate_secure_path(path: str, must_exist: bool = False) -> Path:
    clean_path = Path(path).resolve()
    
    if ".." in str(path):
        raise SecurityError(f"Path traversal détecté: {path}")
    
    if clean_path.suffix.lower() != ".xlsx":
        raise SecurityError(f"Extension non autorisée: {clean_path.suffix}")
    
    if not is_path_allowed(str(clean_path)):
        raise SecurityError(f"Chemin hors zone autorisée: {clean_path}")
    
    if must_exist and not clean_path.exists():
        raise FileNotFoundError(f"Fichier non trouvé: {clean_path}")
    
    if clean_path.is_symlink():
        real_path = clean_path.resolve()
        if not is_path_allowed(str(real_path)):
            raise SecurityError(f"Lien symbolique vers zone non autorisée: {path}")
    
    return clean_path
```

### 3. Formules Dangereuses Bloquées

```python
DANGEROUS_FUNCTIONS = [
    "CALL",           # Appel DLL externe
    "REGISTER",       # Enregistrement fonction
    "EXEC",           # Exécution commande
    "WEBSERVICE",     # Appel HTTP (fuite données)
    "FILTERXML",      # Parsing XML externe
    "HYPERLINK",      # Peut exécuter du code (optionnel)
]
```

### 4. Aucune Connexion Réseau

```python
# Le serveur n'importe AUCUNE bibliothèque réseau
# Pas de: requests, httpx, aiohttp, urllib, socket
# Uniquement: openpyxl (fichiers locaux), pydantic (validation), fastmcp (protocole)
```

---

## 📝 Checklist de Développement

### Phase 1 : Setup Initial
- [x] Fork du repo original vers iA4UP-Organization
- [x] Remplacement du CLAUDE.md par version iA4UP
- [ ] Supprimer fichiers Smithery (.smithery/, smithery.yaml, server_smithery.py)
- [ ] Créer `config.py` avec ALLOWED_PATHS
- [ ] Créer `sandbox.py` avec validation sécurisée
- [ ] Modifier `pyproject.toml` (retirer smithery)

### Phase 2 : Intégration Sécurité
- [ ] Intégrer `validate_secure_path()` dans toutes les opérations
- [ ] Ajouter tests de sécurité (path traversal, etc.)
- [ ] Vérifier qu'aucun appel réseau n'est possible
- [ ] Documenter les variables d'environnement

### Phase 3 : Test Local
- [ ] Installer en local avec `pip install -e .`
- [ ] Tester avec Claude Desktop
- [ ] Valider les 20 outils
- [ ] Tester les cas d'erreur (sécurité)

### Phase 4 : Dockerisation
- [ ] Créer Dockerfile
- [ ] Créer docker-compose.yml
- [ ] Tester sur VPS Hostinger
- [ ] Intégrer avec N8N

### Phase 5 : Documentation
- [ ] README.md complet
- [ ] Exemples d'utilisation
- [ ] Guide de déploiement

---

## 🎯 Cas d'Usage Prioritaires (Savpro / iA4UP)

### 1. Analyse de l'outil de cotation BESS
- Lire les formules complexes
- Comprendre la structure des feuilles
- Extraire les paramètres clés

### 2. Base de prospection éolien
- Créer/modifier la base de données Excel
- Ajouter des colonnes calculées
- Formater pour export

### 3. Rapports automatisés
- Générer des rapports mensuels
- Appliquer un formatage standardisé
- Intégrer dans workflows N8N

---

## 🔗 Références

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [Repo original mort-lab/excel-mcp](https://github.com/mort-lab/excel-mcp)

---

## 📜 Historique

| Date | Action |
|------|--------|
| 04/02/2025 | Analyse du repo original, identification des risques sécurité |
| 04/02/2025 | Création du CLAUDE.md version iA4UP |
| 04/02/2025 | Fork vers iA4UP-Organization/excel-mcp |
| 04/02/2025 | Remplacement du CLAUDE.md original par version sécurisée |

---

*Projet initié le 04/02/2025 - iA4UP / Raphael Depré*
*Organisation GitHub : iA4UP-Organization*
