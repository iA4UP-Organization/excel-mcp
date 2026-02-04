# MCP Excel Server - Projet Custom iA4UP

> Fork sécurisé du serveur MCP Excel pour manipulation locale de fichiers .xlsx
> Sans télémétrie, sans cloud, 100% privé

## 📋 Origine du Projet

**Source** : [mort-lab/excel-mcp](https://github.com/mort-lab/excel-mcp)  
**Fork** : [iA4UP-Organization/excel-mcp](https://github.com/iA4UP-Organization/excel-mcp)  
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

### Ce qu'on rejette ❌ (SUPPRIMÉ)

- ~~`server_smithery.py`~~ → supprimé (mode cloud)
- ~~Dépendance `smithery>=0.4.2`~~ → retirée de pyproject.toml
- ~~`smithery.yaml`~~ → supprimé
- ~~`.smithery/`~~ → supprimé

### Ce qu'on a ajouté 🛡️ (FAIT)

- `config.py` : Sandboxing des répertoires (ALLOWED_PATHS)
- `utils/sandbox.py` : Validation renforcée anti path-traversal
- `server.py` nettoyé : Mode 100% offline, nom "iA4UP Secure"
- `validators.py` réécrit : Branche vers sandbox, formules dangereuses étendues (WEBSERVICE, FILTERXML)
- `pyproject.toml` : Renommé "excel-mcp-server-secure", smithery retiré

---

## 🏗️ Architecture Actuelle

```
iA4UP-Organization/excel-mcp (GitHub)
├── src/
│   └── excel_mcp_server/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py          # Serveur MCP principal (SANS Smithery)
│       ├── models.py          # Modèles Pydantic
│       ├── config.py          # ✅ Configuration sécurisée (ALLOWED_PATHS)
│       ├── operations/
│       │   ├── __init__.py
│       │   ├── workbook.py
│       │   ├── sheet.py
│       │   ├── cell.py
│       │   └── formatting.py
│       └── utils/
│           ├── __init__.py
│           ├── validators.py  # ✅ Réécrit avec intégration sandbox
│           └── sandbox.py     # ✅ Sandboxing des chemins
├── tests/
├── pyproject.toml             # ✅ Sans Smithery
├── CLAUDE.md                  # Ce fichier
└── README.md
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

### 2. N8N sur VPS Hostinger (Automatisation)

```yaml
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
```

### 3. Claude.ai via Tunnel Sécurisé (Avancé)

```bash
cloudflared tunnel --url http://localhost:3100
```

---

## 📦 Dépendances (version sécurisée)

```toml
dependencies = [
    "mcp>=1.15.0",
    "fastmcp>=2.0.0",
    "openpyxl>=3.1.0",
    "pydantic>=2.0.0",
    # PAS de smithery - supprimé volontairement
]
```

---

## 🛠️ Outils Disponibles (20 tools)

### Workbook Operations (3)
| Tool | Description | Paramètres |
|------|-------------|------------|
| `create_workbook` | Créer un nouveau .xlsx | `file_path` |
| `get_workbook_info` | Métadonnées du fichier | `file_path` |
| `list_sheets` | Lister les feuilles | `file_path` |

### Sheet Operations (4)
| Tool | Description | Paramètres |
|------|-------------|------------|
| `create_sheet` | Créer une feuille | `workbook_path`, `sheet_name`, `index?` |
| `delete_sheet` | Supprimer une feuille | `workbook_path`, `sheet_name` |
| `rename_sheet` | Renommer une feuille | `workbook_path`, `old_name`, `new_name` |
| `copy_sheet` | Copier une feuille | `workbook_path`, `source_sheet`, `new_name` |

### Cell Operations (5)
| Tool | Description | Paramètres |
|------|-------------|------------|
| `write_cell` | Écrire dans une cellule | `workbook_path`, `sheet_name`, `cell`, `value` |
| `read_cell` | Lire une cellule | `workbook_path`, `sheet_name`, `cell` |
| `write_range` | Écrire une plage | `workbook_path`, `sheet_name`, `start_cell`, `data[][]` |
| `read_range` | Lire une plage | `workbook_path`, `sheet_name`, `range_ref` |
| `write_formula` | Écrire une formule | `workbook_path`, `sheet_name`, `cell`, `formula` |

### Formatting Operations (5)
| Tool | Description | Paramètres |
|------|-------------|------------|
| `format_font` | Police | `workbook_path`, `sheet_name`, `range_ref`, options... |
| `format_fill` | Couleur de fond | `workbook_path`, `sheet_name`, `range_ref`, `color` |
| `format_border` | Bordures | `workbook_path`, `sheet_name`, `range_ref`, `style`, `sides[]` |
| `format_alignment` | Alignement | `workbook_path`, `sheet_name`, `range_ref`, `horizontal`, `vertical` |
| `format_number` | Format nombre/date | `workbook_path`, `sheet_name`, `range_ref`, `format_string` |

---

## 🔒 Sécurité Implémentée

### 1. Sandboxing (config.py)
- Variable `ALLOWED_PATHS` (env) → liste de répertoires autorisés
- Si non défini → mode permissif avec warning
- Validation au démarrage (chemins existants uniquement)

### 2. Anti Path-Traversal (utils/sandbox.py)
- Blocage `../` et `..\`
- Extension `.xlsx` obligatoire
- Vérification liens symboliques sortants
- Exception `SecurityError` dédiée

### 3. Formules Dangereuses (validators.py)
- CALL, REGISTER, EXEC (existant)
- WEBSERVICE, FILTERXML (ajouté)

### 4. Zéro Réseau
- Aucun import réseau (requests, httpx, aiohttp, urllib, socket)
- Uniquement openpyxl + pydantic + fastmcp

---

## 📝 Checklist de Développement

### Phase 1 : Setup Initial ✅ TERMINÉE
- [x] Fork du repo original vers iA4UP-Organization
- [x] Remplacement du CLAUDE.md par version iA4UP
- [x] Supprimer fichiers Smithery (.smithery/, smithery.yaml, server_smithery.py)
- [x] Créer `config.py` avec ALLOWED_PATHS
- [x] Créer `sandbox.py` avec validation sécurisée
- [x] Modifier `pyproject.toml` (retirer smithery)
- [x] Nettoyer `server.py` (retirer imports smithery, renommer)
- [x] Réécrire `validators.py` (intégration sandbox)

### Phase 2 : Tests ⏳ À FAIRE
- [ ] Installer en local avec `pip install -e .`
- [ ] Tester avec Claude Desktop
- [ ] Valider les 20 outils
- [ ] Tester les cas d'erreur (path traversal, extension, etc.)
- [ ] Ajouter tests unitaires pour sandbox.py et config.py

### Phase 3 : Dockerisation ⏳ À FAIRE
- [ ] Créer Dockerfile
- [ ] Créer docker-compose.yml
- [ ] Tester sur VPS Hostinger
- [ ] Intégrer avec N8N

### Phase 4 : Documentation ⏳ À FAIRE
- [ ] README.md complet (remplacer celui de mort-lab)
- [ ] Exemples d'utilisation
- [ ] Guide de déploiement

---

## 🎯 Cas d'Usage Prioritaires (Savpro / iA4UP)

1. **Analyse outil cotation BESS** : Lire formules complexes, structure des feuilles
2. **Base prospection éolien** : Créer/modifier la base Excel, colonnes calculées
3. **Rapports automatisés** : Génération mensuelle via N8N

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
| 04/02/2025 | Analyse sécurité du repo mort-lab/excel-mcp |
| 04/02/2025 | Fork vers iA4UP-Organization/excel-mcp |
| 04/02/2025 | Remplacement CLAUDE.md par version iA4UP |
| 04/02/2025 | Ajout config.py (ALLOWED_PATHS) + sandbox.py (anti path-traversal) |
| 04/02/2025 | Nettoyage server.py, validators.py, pyproject.toml |
| 04/02/2025 | Suppression server_smithery.py, smithery.yaml, .smithery/ |
| 04/02/2025 | **Phase 1 terminée** - Repo sécurisé, prêt pour tests |

---

*Projet initié le 04/02/2025 - iA4UP / Raphael Depré*
*Organisation GitHub : iA4UP-Organization*
