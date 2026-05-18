import logging
from app.models.schema_models import BlockSchema
from app.services.ollama_service import call_ollama_json

logger = logging.getLogger(__name__)


def extract_schema_from_text(
    vendor: str,
    block_name: str,
    block_type: str,
    version: str,
    snippet: str,
) -> BlockSchema:
    prompt = f"""
Extract a function block schema from the text below.

Return ONLY valid JSON.

Use this exact JSON structure:

{{
  "vendor": "string",
  "block_name": "string",
  "block_type": "string",
  "version": "string",
  "description": "string",
  "pins": [
    {{
      "name": "string",
      "dir": "in",
      "type": "string",
      "mandatory": true,
      "description": "string"
    }}
  ],
  "parameters": [
    {{
      "name": "string",
      "type": "string",
      "default": "string",
      "mandatory": true,
      "description": "string"
    }}
  ],
  "notes": "string"
}}

Rules:
- If vendor is missing, use "{vendor}".
- If block_name is missing, use "{block_name}".
- If block_type is missing, use "{block_type}".
- If version is missing, use "{version}".
- block_name is the stable user-facing name for this block family.
- block_type is the vendor-specific function block type/code from the documentation.
- Extract all obvious inputs and outputs as pins.
- Extract named configuration values from the Parameters section as parameters.
- dir must be either "in" or "out".
- mandatory must be true or false.
- Do not include blank placeholder pins or parameters.
- Do not include markdown.
- Do not include explanation text.

Text:
{snippet}
"""

    logger.info("Extracting schema from text")

    parsed_json = call_ollama_json(prompt)

    parsed_json["vendor"] = parsed_json.get("vendor") or vendor
    parsed_json["block_name"] = parsed_json.get("block_name") or block_name
    parsed_json["block_type"] = parsed_json.get("block_type") or block_type
    parsed_json["version"] = parsed_json.get("version") or version

    parsed_json["pins"] = [
        pin for pin in parsed_json.get("pins", [])
        if isinstance(pin, dict) and pin.get("name")
    ]
    parsed_json["parameters"] = [
        parameter for parameter in parsed_json.get("parameters", [])
        if isinstance(parameter, dict) and parameter.get("name")
    ]

    return BlockSchema(**parsed_json)
