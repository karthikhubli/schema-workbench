# schema-workbench

Minimal Schema Workbench prototype for industrial control-system schema ingestion and cross-vendor mapping.

This version keeps the UI intentionally simple because the prototype focus is the backend workflow:

- list schemas
- create/edit schema
- create a new schema version
- paste a PDF/document snippet
- generate a candidate schema
- review/save the candidate
- generate mapping suggestions
- save a mapping

Current backend handlers log submitted input to the console. Persistence, SQLite migrations, and Ollama inference can be plugged into the existing route/service structure next.

## Tech stack

- Python
- FastAPI
- Jinja2
- HTMX
- SQLite / SQLAlchemy planned
- Ollama planned

## Project structure

```text
app/
  api/routes/          API handlers
  ui/routes.py         UI page routes
  templates/           Jinja2 templates
  templates/partials/  HTMX partials
  static/              CSS and JS
  services/            business logic placeholder
  models/              DB models placeholder
  schemas/             Pydantic schemas placeholder
```

## Run locally

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the environment

Mac/Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the app

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

## Pages

- `/` - schema list
- `/schemas/new` - create/edit schema
- `/ingest` - ingest snippet and create mapping

## Notes

The route handlers currently log form input to the console, for example:

```text
INFO app.api.routes.schemas : Saving schema draft: {...}
INFO app.api.routes.ingest : Generating candidate schema from snippet: {...}
INFO app.api.routes.suggest : Generating mapping suggestions: {...}
INFO app.api.routes.mappings : Saving mapping: {...}
```
