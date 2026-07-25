# Variant-Verse

A bioinformatics tool to search, analyze, and classify genetic variants by gene name, pulling from ClinVar clinical interpretation data and mapping diseases to the MONDO disease ontology.

---

## Architecture

```text
React Frontend (port 3000)
    |  POST /api/variants/process {geneName}
    v
FastAPI Server -- backend_server.py (port 8000)
    |
    |-- SQLite: clinvar.db
    |     |-- submissions  (variant x submitter x significance)
    |     |-- comparisons  (pairs of submissions for conflict analysis)
    |     `-- mondo_clinvar_relationships
    |
    `-- Mondo class (parses mondo.owl OWL file)
          `-- disease name -> MONDO ID lookup + ontology hierarchy
```

See `docs/superpowers/specs/2026-07-26-production-redesign-design.md` for the
in-progress redesign (Postgres, consolidated single server, real data pipeline).

---

## Key Components

| File                                              | Role                                                                |
| ------------------------------------------------- | ------------------------------------------------------------------- |
| frontend/src/App.js                               | Single React page: gene name input -> calls backend                 |
| mutation-generator-backend/src/backend_server.py  | FastAPI server on port 8000 -- query API                            |
| mutation-generator-backend/clinvar_setup/db.py    | DB class with ~20 methods for querying ClinVar SQLite               |
| mutation-generator-backend/backend/app/mondo.py   | MONDO ontology parser: ancestor/descendant traversal, LCA algorithm |

---

## Data Sources

### ClinVar

NCBI's crowdsourced database of genetic variants and their clinical significance. Imported from ClinVar XML dumps into clinvar.db.

The comparisons table is the core -- it stores pairs of clinical interpretations for the same variant by two different submitters, enabling conflict detection. Fields include significance1/2, star_level1/2, normalized_method1/2, conflict_level.

### MONDO Ontology

A unified disease ontology in OWL format (data/mondo.owl). The Mondo class parses it and provides:

- Disease name / synonym -> MONDO ID lookup
- Cross-reference mapping (OMIM IDs, ORPHA IDs -> MONDO IDs)
- Hierarchical traversal: ancestors, descendants, Lowest Common Ancestor

---

## Stack

- Frontend: React 18, Headless UI, Lucide React icons
- Backend: FastAPI + Uvicorn (Python)
- Database: SQLite (clinvar.db)
- Key libs: Biopython, pandas, numpy, lxml, BeautifulSoup4, selenium, openpyxl

---

## What's Working vs. What's Not

Working:

- MONDO ontology parsing (OWL XML -> name/ID maps + hierarchy navigation)
- ClinVar DB query layer (db.py) -- filtering by gene, condition, submitter, method, significance, conflict level, country, date
- Port 8000 API -- listing variants/genes/conditions with conflict detection

Half-baked / WIP:

- Frontend doesn't call backend_server.py's endpoints yet -- just alert('Success!') after a request to a since-removed endpoint
- import-clinvar-xml.py is empty -- data import pipeline is missing
- "Similar genes" (via MONDO) is designed but not yet implemented -- see the redesign spec

---

## Running the App

```bash
# Backend (port 8000)
cd mutation-generator-backend
python src/backend_server.py

# Frontend
cd frontend && npm start
```
