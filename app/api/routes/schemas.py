import logging

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

from app.services.schema_service import save_schema_from_form

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("")
async def save_schema(
    vendor: str = Form(...),
    block_name: str = Form(...),
    block_type: str = Form(...),
    version: str = Form(...),
    description: str = Form(""),
    pins_json: str = Form("[]"),
    parameters_json: str = Form("[]"),
    notes: str = Form(""),
):
    logger.info(
        "Saving schema draft: vendor=%s block_name=%s block_type=%s version=%s",
        vendor,
        block_name,
        block_type,
        version,
    )

    try:
        schema_id = save_schema_from_form(
            vendor=vendor,
            block_name=block_name,
            block_type=block_type,
            version=version,
            description=description,
            pins_json=pins_json,
            parameters_json=parameters_json,
            notes=notes,
            review_status="Draft",
            change_summary="Initial schema created",
        )
    except ValueError as exc:
        return HTMLResponse(f'<div class="error">{exc}</div>', status_code=400)

    return HTMLResponse(
        f'<div class="success">Schema saved successfully. ID: {schema_id}<br><a href="/">View saved schemas</a></div>'
    )


@router.post("/new-version")
async def create_new_version(
    vendor: str = Form(...),
    block_name: str = Form(...),
    block_type: str = Form(...),
    version: str = Form(...),
    description: str = Form(""),
    pins_json: str = Form("[]"),
    parameters_json: str = Form("[]"),
    notes: str = Form(""),
):
    logger.info(
        "Creating new schema version: vendor=%s block_name=%s block_type=%s version=%s",
        vendor,
        block_name,
        block_type,
        version,
    )

    try:
        schema_id = save_schema_from_form(
            vendor=vendor,
            block_name=block_name,
            block_type=block_type,
            version=version,
            description=description,
            pins_json=pins_json,
            parameters_json=parameters_json,
            notes=notes,
            review_status="Draft",
            change_summary="New version created from existing schema",
        )
    except ValueError as exc:
        return HTMLResponse(f'<div class="error">{exc}</div>', status_code=400)

    return HTMLResponse(
        f'<div class="success">New schema version created. ID: {schema_id}<br><a href="/">View saved schemas</a></div>'
    )
