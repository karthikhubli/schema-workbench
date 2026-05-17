import logging

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.mapping_service import save_mapping_from_form
from app.services.schema_service import get_schema_by_id
from app.services.schema_compatibility_service import calculate_schema_compatibility

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/compatibility")
async def check_schema_compatibility(
    request: Request,
    source_schema_id: int = Form(...),
    target_schema_id: int = Form(...),
):
    logger.info(
        "Checking mapping compatibility source_schema_id=%s target_schema_id=%s",
        source_schema_id,
        target_schema_id,
    )

    source_schema = get_schema_by_id(source_schema_id)
    target_schema = get_schema_by_id(target_schema_id)

    if source_schema is None:
        return HTMLResponse(
            f'<div class="error">Source schema not found for ID: {source_schema_id}</div>',
            status_code=404,
        )

    if target_schema is None:
        return HTMLResponse(
            f'<div class="error">Target schema not found for ID: {target_schema_id}</div>',
            status_code=404,
        )

    compatibility = calculate_schema_compatibility(
        source_schema,
        target_schema,
    )

    return templates.TemplateResponse(
        "partials/schema_compatibility.html",
        {
            "request": request,
            "compatibility": compatibility,
            "source_schema": source_schema,
            "target_schema": target_schema,
        },
    )


@router.post("/save")
async def save_mapping(
    source_schema_id: int = Form(...),
    target_schema_id: int = Form(...),
    mapping_json: str = Form("[]"),
    notes: str = Form(""),
):
    logger.info(
        "Saving reviewed mapping source_schema_id=%s target_schema_id=%s",
        source_schema_id,
        target_schema_id,
    )

    try:
        mapping_id = save_mapping_from_form(
            source_schema_id=source_schema_id,
            target_schema_id=target_schema_id,
            mapping_json=mapping_json,
            notes=notes,
            status="Draft",
        )
    except ValueError as exc:
        return HTMLResponse(f'<div class="error">{exc}</div>', status_code=400)

    return HTMLResponse(
        f"""
        <div class="success">
            Mapping saved successfully. Mapping ID: {mapping_id}
            <br>
            <a href="/mappings">Back to mappings</a>
        </div>
        """
    )
