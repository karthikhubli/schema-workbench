import logging

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates

from app.services.schema_extraction_service import extract_schema_from_text

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/generate")
async def generate_candidate_schema(
    request: Request,
    vendor: str = Form(...),
    block_name: str = Form(...),
    block_type: str = Form(...),
    version: str = Form(...),
    snippet: str = Form(...),
):
    logger.info(
        "Received ingestion request: vendor=%s block_name=%s block_type=%s version=%s snippet_length=%s",
        vendor,
        block_name,
        block_type,
        version,
        len(snippet),
    )

    candidate_schema = extract_schema_from_text(
        vendor=vendor,
        block_name=block_name,
        block_type=block_type,
        version=version,
        snippet=snippet,
    )

    candidate = (
        candidate_schema.model_dump()
        if hasattr(candidate_schema, "model_dump")
        else candidate_schema.dict()
    )

    return templates.TemplateResponse(
        "partials/candidate_schema.html",
        {
            "request": request,
            "candidate": candidate,
        },
    )
