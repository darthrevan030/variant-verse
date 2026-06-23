# Variant-Verse

A bioinformatics tool to search, analyze, and classify genetic variants by gene name, pulling from ClinVar clinical interpretation data and mapping diseases to the MONDO disease ontology.

---

## Architecture

```
React Frontend (port 3000)
    |  POST /api/variants/process {geneName}
    v
FastAPI Server -- src/api/main.py (port 8001)   <- active server
    |
    |-- SQLite: clinvar.db
    |     |-- submissions  (variant x submitter x significance)
    |     |-- comparisons  (pairs of submissions for conflict analysis)
    |     |-- mutations    (curated mutations table)
    |     `-- mondo_clinvar_relationships
    |
    `-- Mondo class (parses mondo.owl OWL file)
          `-- disease name -> MONDO ID lookup + ontology hierarchy

FastAPI Server -- backend_server.py (port 8000)   <- richer query layer
    `-- GET /variants/, /genes, /conditions, /submissions
```

---

## Key Components

| File                                              | Role                                                                |
| ------------------------------------------------- | ------------------------------------------------------------------- |
| frontend/src/App.js                               | Single React page: gene name input -> calls backend                 |
| mutation-generator-backend/src/api/main.py        | Active FastAPI server on port 8001                                  |
| mutation-generator-backend/src/backend_server.py  | Richer query API on port 8000                                       |
| mutation-generator-backend/clinvar_setup/db.py    | DB class with ~20 methods for querying ClinVar SQLite               |
| mutation-generator-backend/backend/app/mondo.py   | MONDO ontology parser: ancestor/descendant traversal, LCA algorithm |
| mutation-generator-backend/src/models/mutation.py | Pydantic models: Mutation, MutationType enum                        |

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

- /api/variants/process (port 8001) returns early -- echoes gene name only, actual DB query is dead code
- Frontend shows no results -- just alert('Success!') after API call
- import-clinvar-xml.py is empty -- data import pipeline is missing

---

## Running the App

```bash
# Backend (port 8001 -- what the frontend calls)
cd mutation-generator-backend
uvicorn src.api.main:app --reload --port 8001

# Backend (port 8000 -- richer query API)
python src/backend_server.py

# Frontend
cd frontend && npm start
```
