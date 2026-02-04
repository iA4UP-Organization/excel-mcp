# MCP Excel Server - Projet Custom iA4UP

> Fork sécurisé du serveur MCP Excel pour manipulation locale de fichiers .xlsx
> Sans télémétrie, sans cloud, 100% privé

## ⚠️ NOTE IMPORTANTE POUR CLAUDE
> Ce fichier `/CLAUDE.md` est le **NÔTRE** (iA4UP).
> Le dossier `/.claude/` qui existe encore contient des résidus de l'auteur original (mort-lab) — des commands/agents/skills pour Claude Code. Ce dossier n'a RIEN à voir avec ce fichier. Il doit être supprimé (nettoyage cosmétique en attente, voir section "Nettoyage restant").

---

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

### Ce qu'on a supprimé ❌

- ~~`server_smithery.py`~~ → supprimé (mode cloud qui envoyait les fichiers sur leurs serveurs)
- ~~Dépendance `smithery>=0.4.2`~~ → retirée de pyproject.toml
- ~~`smithery.yaml`~~ → supprimé
- ~~`.smithery/`~~ → supprimé
- ~~`CLAUDE_SETUP.md`~~ → doc en espagnol de l'auteur (chemins vers son PC perso)
- ~~`PRD.md`~~ → product requirements de l'auteur
- ~~`SUMMARY.md`~~ → résumé de l'auteur
- ~~`TOOLS.md`~~ → déjà documenté dans ce CLAUDE.md
- ~~`verify_installation.py`~~ → script de l'auteur

### Ce qu'on a ajouté 🛡️

- `config.py` : Sandboxing des répertoires (ALLOWED_PATHS)
- `utils/sandbox.py` : Validation renforcée anti path-traversal
- `server.py` nettoyé : Mode 100% offline, nom "iA4UP Secure"
- `validators.py` réécrit : Branche vers sandbox, formules dangereuses étendues (WEBSERVICE, FILTERXML)
- `pyproject.toml` : Renommé "excel-mcp-server-secure", smithery retiré

### 🧹 Nettoyage restant (cosmétique, pas de risque sécurité)

Le dossier `.claude/` contient encore des fichiers markdown de l'auteur original (commands, agents, skills pour Claude Code). Ils ne sont PAS exécutables et ne posent aucun risque. Pour les supprimer proprement :

```bash
# Cloner le repo localement puis :
git rm -r .claude/
git commit -m "chore: supprimer dossier .claude/ résiduel de l'auteur original"
git push origin main
```

---

## 🏗️ Architecture Actuelle

```
iA4UP-Organization/excel-mcp (GitHub)
├── .claude/                   # ⚠️ RÉSIDU auteur original - À SUPPRIMER
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
├── CLAUDE.md                  # ✅ CE FICHIER (iA4UP)
└── README.md                  # À réécrire (encore celui de mort-lab)
```

---

## 🔧 Scénarios d'Utilisation

### 1. Claude Desktop (Local - Recommandé pour démarrer)

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

### 3. Claude.ai via Tunnel Sécurisé

```bash
cloudflared tunnel --url http://localhost:3100
```

---

## 📦 Dépendances

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

### Workbook (3) | Sheet (4) | Cell (5) | Formatting (5)

Voir la documentation complète des paramètres dans `src/excel_mcp_server/models.py`.

---

## 🔒 Sécurité

1. **Sandboxing** (config.py) : ALLOWED_PATHS via env
2. **Anti Path-Traversal** (sandbox.py) : blocage `../`, extension `.xlsx` obligatoire, liens symboliques vérifiés
3. **Formules dangereuses** (validators.py) : CALL, REGISTER, EXEC, WEBSERVICE, FILTERXML bloquées
4. **Zéro réseau** : aucun import réseau dans tout le code

---

## 📝 Checklist

### Phase 1 : Setup Initial ✅ TERMINÉE
- [x] Fork + CLAUDE.md iA4UP
- [x] Suppression Smithery (server_smithery.py, smithery.yaml, .smithery/)
- [x] Suppression docs auteur (CLAUDE_SETUP.md, PRD.md, SUMMARY.md, TOOLS.md, verify_installation.py)
- [x] Ajout config.py + sandbox.py
- [x] Nettoyage server.py + validators.py + pyproject.toml

### Phase 1b : Nettoyage cosmétique ⏳ EN ATTENTE
- [ ] Supprimer dossier `.claude/` (résidu auteur, `git rm -r .claude/`)
- [ ] Réécrire README.md (encore celui de mort-lab)

### Phase 2 : Tests ⏳ À FAIRE
- [ ] Installer en local avec `pip install -e .`
- [ ] Tester avec Claude Desktop
- [ ] Valider les 20 outils
- [ ] Tests sécurité (path traversal, extension, etc.)
- [ ] Tests unitaires sandbox.py + config.py

### Phase 3 : Dockerisation ⏳ À FAIRE
- [ ] Dockerfile + docker-compose.yml
- [ ] Tester sur VPS Hostinger + intégrer N8N

---

## 📜 Historique

| Date | Action |
|------|--------|
| 04/02/2025 | Analyse sécurité repo mort-lab/excel-mcp |
| 04/02/2025 | Fork vers iA4UP-Organization/excel-mcp |
| 04/02/2025 | CLAUDE.md iA4UP + config.py + sandbox.py |
| 04/02/2025 | Suppression Smithery + docs auteur original |
| 04/02/2025 | Nettoyage partiel .claude/ (agents, skills, PRPs, settings) |
| 04/02/2025 | **Phase 1 terminée** — reste .claude/commands/ à supprimer |

---

*Projet iA4UP / Raphael Depré — Organisation GitHub : iA4UP-Organization*
