import json
import logging
from typing import Any

from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates

from app.services.ollama_service import call_ollama_json
from app.services.schema_service import get_schema_by_id

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _compact_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Keep only the fields the LLM needs for mapping suggestions."""
    return {
        "id": schema.get("id"),
        "vendor": schema.get("vendor"),
        "block_name": schema.get("block_name"),
        "block_type": schema.get("block_type"),
        "version": schema.get("version"),
        "description": schema.get("description"),
        "pins": schema.get("pins", []),
        "parameters": schema.get("parameters", []),
    }


def _build_mapping_prompt(source_schema: dict[str, Any], target_schema: dict[str, Any]) -> str:
    source_json = json.dumps(_compact_schema(source_schema), indent=2)
    target_json = json.dumps(_compact_schema(target_schema), indent=2)

    return f"""
You are helping a control-systems engineer map function block schemas between two vendors.

Compare the source schema and target schema below. Suggest mappings between semantically equivalent pins and parameters.

Rules:
- Return ONLY valid JSON.
- Do not include markdown.
- Do not include explanations outside JSON.
- Map pins only to pins.
- Map parameters only to parameters.
- If no good target exists, use an empty string for target and confidence "low".
- Confidence must be one of: "high", "medium", "low".

Return this exact JSON structure:
{{
  "mappings": [
    {{
      "type": "pin",
      "source": "source field name",
      "target": "target field name",
      "confidence": "high",
      "reason": "short reason"
    }}
  ]
}}

Source Schema:
{source_json}

Target Schema:
{target_json}
"""


def _normalize_ollama_response(response: Any) -> list[dict[str, Any]]:

    if isinstance(response, dict):
        mappings = response.get("mappings", [])
    elif isinstance(response, list):
        mappings = response
    else:
        mappings = []

    if not isinstance(mappings, list):
        return []

    normalized: list[dict[str, Any]] = []
    for item in mappings:
        if not isinstance(item, dict):
            continue

        normalized.append(
            {
                "type": item.get("type", ""),
                "source": item.get("source", ""),
                "target": item.get("target", ""),
                "confidence": item.get("confidence", "low"),
                "reason": item.get("reason", "Suggested by Ollama"),
            }
        )

    return normalized


@router.post("/generate")
async def generate_mapping_suggestions(
    request: Request,
    source_schema_id: int = Form(...),
    target_schema_id: int = Form(...),
):
    logger.info(
        "Generating Ollama mapping suggestions source_schema_id=%s target_schema_id=%s",
        source_schema_id,
        target_schema_id,
    )

    source_schema = get_schema_by_id(source_schema_id)
    target_schema = get_schema_by_id(target_schema_id)

    if not source_schema or not target_schema:
        suggestions: list[dict[str, Any]] = []
        mapping_json = "[]"
    else:
        prompt = _build_mapping_prompt(source_schema, target_schema)
        ollama_response = call_ollama_json(prompt)
        suggestions = _normalize_ollama_response(ollama_response)
        mapping_json = json.dumps(suggestions, indent=2)

    return templates.TemplateResponse(
        "partials/mapping_suggestions.html",
        {
            "request": request,
            "source_schema_id": source_schema_id,
            "target_schema_id": target_schema_id,
            "suggestions": suggestions,
            "mapping_json": mapping_json,
        },
    )


# Backward-compatible old endpoint.
@router.post("/mappings")
async def suggest_mappings(
    request: Request,
    source_schema_id: int = Form(...),
    target_schema_id: int = Form(...),
):
    return await generate_mapping_suggestions(request, source_schema_id, target_schema_id)
