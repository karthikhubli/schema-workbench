import logging

from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

from app.services.schema_service import save_schema_from_form, save_schema_new_version_from_form

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
    original_schema_id: int = Form(...),
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
        "Creating new schema version: original_schema_id=%s vendor=%s block_name=%s block_type=%s version=%s",
        original_schema_id,
        vendor,
        block_name,
        block_type,
        version,
    )

    try:
        result = save_schema_new_version_from_form(
            original_schema_id=original_schema_id,
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

    if result["is_breaking"]:
        reasons_html = "".join(f"<li>{reason}</li>" for reason in result["reasons"])
        return HTMLResponse(
            f"""
            <div class="warning">
                New schema version created. ID: {result["schema_id"]}<br>
                <strong>Breaking change detected.</strong><br>
                {result["mappings_marked"]} mapping(s) marked as <strong>Needs Update</strong>.
                <ul>{reasons_html}</ul>
                <a href="/">View saved schemas</a>
            </div>
            """
        )

    return HTMLResponse(
        f"""
        <div class="success">
            New schema version created. ID: {result["schema_id"]}<br>
            <strong>No breaking change detected.</strong><br>
            Existing mappings were not marked for update.
            <br>
            <a href="/">View saved schemas</a>
        </div>
        """
    )
