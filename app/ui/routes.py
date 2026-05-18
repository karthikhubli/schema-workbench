import json
import logging
from collections import defaultdict

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.services.schema_service import get_schema_by_id, list_schemas, get_all_schemas
from app.services.mapping_service import list_mappings

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _pretty_json(value) -> str:
    if isinstance(value, str):
        try:
            return json.dumps(json.loads(value or "[]"), indent=2)
        except json.JSONDecodeError:
            return value
    return json.dumps(value or [], indent=2)


def _group_by_vendor(schemas: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for schema in schemas:
        grouped[schema.get("vendor") or "Unknown Vendor"].append(schema)
    return dict(grouped)


@router.get("/")
async def home(request: Request):
    schemas = get_all_schemas()
    grouped_schemas = _group_by_vendor(schemas)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "grouped_schemas": grouped_schemas,
        },
    )


@router.get("/schemas/new")
async def new_schema(request: Request):
    logger.info("Loading create schema page")
    return templates.TemplateResponse(
        "schema_form.html",
        {"request": request},
    )


@router.get("/schemas/{schema_id}/edit")
async def edit_schema(request: Request, schema_id: int):
    logger.info("Loading edit schema page for id=%s", schema_id)

    schema = get_schema_by_id(schema_id)
    if schema:
        schema["pins_json"] = _pretty_json(schema.get("pins_json"))
        schema["parameters_json"] = _pretty_json(schema.get("parameters_json"))

    return templates.TemplateResponse(
        "schema_edit.html",
        {"request": request, "schema": schema},
    )


@router.get("/mappings")
async def mappings_page(request: Request):
    schemas = get_all_schemas()
    mappings = list_mappings()

    return templates.TemplateResponse(
        "mappings.html",
        {
            "request": request,
            "schemas": schemas,
            "mappings": mappings,
        },
    )
