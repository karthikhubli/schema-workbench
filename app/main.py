import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import ingest, mappings, schemas, suggest, vendors
from app.db.session import init_db, reset_db
from app.ui.routes import router as ui_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s : %(message)s",
)

app = FastAPI(title="Schema Workbench")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def startup() -> None:
    reset_db()
    init_db()


app.include_router(ui_router)
app.include_router(vendors.router, prefix="/api/vendors", tags=["vendors"])
app.include_router(schemas.router, prefix="/api/schemas", tags=["schemas"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])
app.include_router(suggest.router, prefix="/api/suggest", tags=["suggest"])
app.include_router(mappings.router, prefix="/api/mappings", tags=["mappings"])
